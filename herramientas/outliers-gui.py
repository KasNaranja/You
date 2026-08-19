#!/usr/bin/env python3
"""Ventana para el buscador de vídeos outlier de YouTube.

Toda la lógica vive en `outliers_youtube.py`; esto es solo la interfaz. Se
ejecuta el análisis en un hilo aparte y los resultados viajan por una cola,
porque tkinter no admite que se toquen sus widgets desde otro hilo: si se hace,
la ventana se congela o revienta de formas difíciles de reproducir.

Compilar a .exe (en Windows):
    pyinstaller --onefile --windowed --name outliers herramientas/outliers-gui.py
"""
from __future__ import annotations

import csv
import queue
import sys
import threading
import tkinter as tk
import webbrowser
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

sys.path.insert(0, str(Path(__file__).resolve().parent))
import outliers_youtube as core  # noqa: E402

COLUMNAS = [
    ("ratio", "Ratio", 70),
    ("x_med", "× mediana", 85),
    ("vistas", "Visitas", 95),
    ("subs", "Subs", 95),
    ("canal", "Canal", 170),
    ("titulo", "Título", 460),
]


def miles(n: int) -> str:
    return f"{n:,}".replace(",", ".")


class App(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Outliers de YouTube")
        self.geometry("1150x680")
        self.minsize(900, 500)

        self.cola: queue.Queue = queue.Queue()
        self.filas: list[dict] = []
        self.trabajando = False
        self.orden_desc = True

        self._construir()
        core.fijar_log(lambda m: self.cola.put(("log", m)))
        self.after(100, self._vaciar_cola)

    # ── interfaz ──────────────────────────────────────────────────────
    def _construir(self) -> None:
        top = ttk.Frame(self, padding=10)
        top.pack(fill="x")

        self.modo = tk.StringVar(value="tema")
        ttk.Radiobutton(top, text="Por temática", variable=self.modo,
                        value="tema", command=self._cambiar_modo).grid(row=0, column=0, sticky="w")
        ttk.Radiobutton(top, text="Por canales", variable=self.modo,
                        value="canales", command=self._cambiar_modo).grid(row=0, column=1, sticky="w", padx=(12, 0))

        self.entrada = ttk.Entry(top, width=60)
        self.entrada.grid(row=1, column=0, columnspan=4, sticky="we", pady=(8, 0))
        self.entrada.insert(0, "economia espana")
        self.entrada.bind("<Return>", lambda _: self._buscar())

        self.pista = ttk.Label(top, foreground="#666",
                               text="Tema a buscar. Los canales se deducen solos.")
        self.pista.grid(row=2, column=0, columnspan=4, sticky="w", pady=(3, 0))

        opts = ttk.Frame(top)
        opts.grid(row=3, column=0, columnspan=5, sticky="w", pady=(10, 0))

        self.n_canales = tk.IntVar(value=5)
        self.n_videos = tk.IntVar(value=30)
        spins = {}
        for clave, etiqueta, var, hasta in (
            ("canales", "Canales:", self.n_canales, 15),
            ("videos", "Últimos vídeos por canal:", self.n_videos, 200),
        ):
            ttk.Label(opts, text=etiqueta).pack(side="left", padx=(0, 4))
            s = ttk.Spinbox(opts, from_=1, to=hasta, width=5, textvariable=var)
            s.pack(side="left", padx=(0, 16))
            spins[clave] = s
        self.spin_canales = spins["canales"]

        self.boton = ttk.Button(top, text="Buscar", command=self._buscar)
        self.boton.grid(row=1, column=4, padx=(10, 0), pady=(8, 0))
        top.columnconfigure(3, weight=1)

        # ── tabla ──
        marco = ttk.Frame(self, padding=(10, 0))
        marco.pack(fill="both", expand=True)

        self.tabla = ttk.Treeview(marco, columns=[c[0] for c in COLUMNAS],
                                  show="headings", selectmode="browse")
        for cid, titulo, ancho in COLUMNAS:
            self.tabla.heading(cid, text=titulo,
                               command=lambda c=cid: self._ordenar(c))
            self.tabla.column(cid, width=ancho,
                              anchor="e" if cid in ("ratio", "x_med", "vistas", "subs") else "w")

        barra = ttk.Scrollbar(marco, orient="vertical", command=self.tabla.yview)
        self.tabla.configure(yscrollcommand=barra.set)
        self.tabla.pack(side="left", fill="both", expand=True)
        barra.pack(side="right", fill="y")

        # Un outlier claro se ve de un vistazo, sin leer los números.
        self.tabla.tag_configure("fuerte", background="#fff2cc")
        self.tabla.tag_configure("muy_fuerte", background="#ffd9a0")
        self.tabla.bind("<Double-1>", self._abrir)

        pie = ttk.Frame(self, padding=10)
        pie.pack(fill="x")
        self.estado = ttk.Label(pie, text="Listo.", foreground="#444")
        self.estado.pack(side="left")
        self.btn_csv = ttk.Button(pie, text="Exportar CSV",
                                  command=self._exportar, state="disabled")
        self.btn_csv.pack(side="right")
        ttk.Label(pie, text="Doble clic en una fila para abrir el vídeo",
                  foreground="#888").pack(side="right", padx=(0, 12))

    def _cambiar_modo(self) -> None:
        por_tema = self.modo.get() == "tema"
        self.pista.config(text="Tema a buscar. Los canales se deducen solos."
                          if por_tema else
                          "Handles o URLs separados por espacios: @ecomonos @juanrallo")
        self.spin_canales.configure(state="normal" if por_tema else "disabled")
        self.entrada.delete(0, "end")
        self.entrada.insert(0, "economia espana" if por_tema else "@ecomonos @juanrallo")

    # ── búsqueda ──────────────────────────────────────────────────────
    def _buscar(self) -> None:
        if self.trabajando:
            return
        texto = self.entrada.get().strip()
        if not texto:
            messagebox.showwarning("Falta el dato", "Escribe un tema o unos canales.")
            return

        self.trabajando = True
        self.boton.config(state="disabled", text="Buscando…")
        self.btn_csv.config(state="disabled")
        self.tabla.delete(*self.tabla.get_children())
        self.filas = []

        threading.Thread(target=self._trabajar, args=(texto,), daemon=True).start()

    def _trabajar(self, texto: str) -> None:
        """Corre en un hilo aparte: aquí no se toca ningún widget."""
        try:
            if self.modo.get() == "tema":
                canales = core.buscar_canales(texto, self.n_canales.get())
            else:
                canales = texto.split()
            if not canales:
                self.cola.put(("fin", []))
                return

            todos: list[dict] = []
            for c in canales:
                todos.extend(core.analizar_canal(c, self.n_videos.get()))
            todos.sort(key=lambda v: v["ratio"], reverse=True)
            self.cola.put(("fin", todos))
        except Exception as e:  # el hilo no debe morir en silencio
            self.cola.put(("error", f"{type(e).__name__}: {e}"))

    def _vaciar_cola(self) -> None:
        try:
            while True:
                tipo, dato = self.cola.get_nowait()
                if tipo == "log":
                    self.estado.config(text=str(dato).strip())
                elif tipo == "error":
                    self._terminar()
                    messagebox.showerror("Ha fallado", str(dato))
                elif tipo == "fin":
                    self.filas = dato
                    self._pintar()
                    self._terminar()
        except queue.Empty:
            pass
        self.after(100, self._vaciar_cola)

    def _terminar(self) -> None:
        self.trabajando = False
        self.boton.config(state="normal", text="Buscar")

    def _pintar(self) -> None:
        self.tabla.delete(*self.tabla.get_children())
        for v in self.filas:
            tag = ("muy_fuerte",) if v["x_med"] >= 3 else \
                  ("fuerte",) if v["x_med"] >= 2 else ()
            self.tabla.insert("", "end", tags=tag, values=(
                f"{v['ratio']:.2f}", f"{v['x_med']:.2f}",
                miles(v["vistas"]), miles(v["subs"]),
                v["canal"], v["titulo"]))
        if self.filas:
            self.btn_csv.config(state="normal")
            self.estado.config(text=f"{len(self.filas)} vídeos. "
                                    "Resaltados los que superan el doble de la mediana.")
        else:
            self.estado.config(text="Sin resultados. Prueba con otro tema.")

    def _ordenar(self, col: str) -> None:
        if not self.filas:
            return
        clave = {"vistas": "vistas", "subs": "subs", "ratio": "ratio",
                 "x_med": "x_med", "canal": "canal", "titulo": "titulo"}[col]
        self.orden_desc = not self.orden_desc
        self.filas.sort(key=lambda v: v[clave], reverse=self.orden_desc)
        self._pintar()

    def _abrir(self, _) -> None:
        sel = self.tabla.selection()
        if sel:
            webbrowser.open(self.filas[self.tabla.index(sel[0])]["url"])

    def _exportar(self) -> None:
        ruta = filedialog.asksaveasfilename(
            defaultextension=".csv", filetypes=[("CSV", "*.csv")],
            initialfile="outliers.csv")
        if not ruta:
            return
        campos = ["ratio", "x_med", "vistas", "subs", "canal", "titulo",
                  "duracion", "url"]
        # utf-8-sig para que Excel en Windows no destroce las tildes.
        with open(ruta, "w", newline="", encoding="utf-8-sig") as f:
            w = csv.DictWriter(f, fieldnames=campos, extrasaction="ignore")
            w.writeheader()
            w.writerows(self.filas)
        self.estado.config(text=f"Guardado: {ruta}")


def main() -> None:
    if sys.platform == "win32":
        try:  # sin esto la ventana se ve borrosa en pantallas con escalado
            from ctypes import windll
            windll.shcore.SetProcessDpiAwareness(1)
        except Exception:
            pass
    App().mainloop()


if __name__ == "__main__":
    main()
