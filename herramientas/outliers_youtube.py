#!/usr/bin/env python3
"""Busca los vídeos outlier de varios canales de YouTube sobre una temática.

Un outlier es un vídeo que rinde muy por encima de lo normal en su canal. Se
miden dos cosas distintas, porque cada una miente de una manera:

  ratio  = visualizaciones ÷ suscriptores del canal
  x_med  = visualizaciones ÷ mediana de visualizaciones del canal

El `ratio` es intuitivo, pero YouTube redondea los suscriptores y los publica
con retraso, así que un canal recién disparado sale inflado. La `x_med` compara
cada vídeo con la audiencia real de su propio canal y no depende de ese número.

Cuando las dos coinciden, el outlier es de fiar. Cuando discrepan, mirar a mano.

Uso:
    outliers --tema "economia espana"
    outliers --canales @ecomonos @juanrallo --videos 40
    outliers --tema "geopolitica" --csv informe.csv

No necesita clave de API: los datos salen de yt-dlp. Solo funciona desde una
conexión doméstica; YouTube bloquea las IPs de centros de datos.
"""
from __future__ import annotations

import argparse
import csv
import statistics
import sys
from collections import Counter

try:
    from yt_dlp import YoutubeDL
except ImportError:
    sys.exit("Falta yt-dlp.  Instálalo con:  pip install yt-dlp")


# El progreso se emite por aquí para que la interfaz gráfica pueda
# redirigirlo a su barra de estado en vez de a una consola que nadie ve.
_emisor = print


def fijar_log(fn) -> None:
    global _emisor
    _emisor = fn


def log(msg: str) -> None:
    _emisor(msg)


# Un canal puede publicar solo en una de estas pestañas: los canales de
# Shorts no tienen siquiera pestaña /videos.
PESTANAS = {"videos": "vídeo", "shorts": "short", "streams": "directo"}

class _Mudo:
    """yt-dlp escribe en stderr aunque se le pida silencio.

    Aquí molesta especialmente: preguntar por una pestaña que el canal no
    tiene es parte del funcionamiento normal, no un fallo que deba verse.
    """
    def debug(self, m): pass
    def info(self, m): pass
    def warning(self, m): pass
    def error(self, m): pass


OPCIONES = {
    "logger": _Mudo(),
    "quiet": True,
    "no_warnings": True,
    "skip_download": True,
    "ignoreerrors": True,
    "extract_flat": "in_playlist",
}


def extraer(url: str, limite: int | None = None) -> dict | None:
    opts = dict(OPCIONES)
    if limite:
        opts["playlistend"] = limite
    try:
        with YoutubeDL(opts) as ydl:
            return ydl.extract_info(url, download=False)
    except Exception as e:
        print(f"  ! {url}: {type(e).__name__}", file=sys.stderr)
        return None


def buscar_canales(tema: str, cuantos: int, muestra: int = 60) -> list[str]:
    """Deduce los canales más presentes en una temática.

    No hay una búsqueda de canales fiable en yt-dlp, así que se buscan vídeos
    del tema y se cuentan los canales que más aparecen. Quien domina los
    resultados de una búsqueda es, a efectos prácticos, quien manda en el nicho.
    """
    log(f"Buscando canales de «{tema}»…")
    info = extraer(f"ytsearch{muestra}:{tema}")
    if not info:
        return []

    vistos: Counter[str] = Counter()
    nombres: dict[str, str] = {}
    for e in info.get("entries") or []:
        if not e:
            continue
        cid = e.get("channel_id") or e.get("uploader_id")
        if not cid:
            continue
        vistos[cid] += 1
        nombres.setdefault(cid, e.get("channel") or e.get("uploader") or cid)

    elegidos = [cid for cid, _ in vistos.most_common(cuantos)]
    for cid in elegidos:
        log(f"  · {nombres[cid]}  ({vistos[cid]} vídeos en la búsqueda)")
    return [f"https://www.youtube.com/channel/{cid}" for cid in elegidos]


def normalizar(canal: str) -> str:
    c = canal.strip()
    if c.startswith("http"):
        return c.rstrip("/")
    if c.startswith("@"):
        return f"https://www.youtube.com/{c}"
    return f"https://www.youtube.com/@{c}"


def analizar_canal(url: str, n_videos: int) -> list[dict]:
    """Devuelve los últimos vídeos del canal con sus dos métricas.

    Se miran las tres pestañas por separado, no solo `/videos`: hay canales
    que publican únicamente Shorts y ahí la pestaña de vídeos ni existe.

    Y la mediana se calcula **por tipo**, no sobre el total. Un Short y un
    vídeo largo del mismo canal juegan en escalas distintas —los Shorts se
    mueven en órdenes de magnitud más de visitas—, así que mezclarlos haría
    que todos los Shorts parecieran outliers y ningún vídeo largo lo fuera.
    """
    base = normalizar(url)
    nombre, subs = base, 0
    por_tipo: dict[str, list[dict]] = {}

    for tab, etiqueta in PESTANAS.items():
        info = extraer(f"{base}/{tab}", limite=n_videos)
        if not info:
            continue  # la pestaña no existe en ese canal
        nombre = info.get("channel") or nombre
        subs = info.get("channel_follower_count") or subs

        lote = []
        for e in info.get("entries") or []:
            if not e:
                continue
            vistas = e.get("view_count")
            if not vistas:
                continue  # estrenos, privados o sin contador público
            lote.append({
                "canal": nombre,
                "subs": subs,
                "tipo": etiqueta,
                "titulo": (e.get("title") or "").strip(),
                "url": f"https://www.youtube.com/watch?v={e.get('id')}",
                "vistas": vistas,
                "duracion": e.get("duration") or 0,
            })
        if lote:
            por_tipo[etiqueta] = lote

    if not por_tipo:
        log(f"  ! {base}: sin vídeos con contador visible")
        return []

    todos: list[dict] = []
    resumen = []
    for etiqueta, lote in por_tipo.items():
        mediana = statistics.median(v["vistas"] for v in lote)
        for v in lote:
            v["subs"] = subs  # la pestaña de Shorts a veces no trae el dato
            v["ratio"] = v["vistas"] / subs if subs else 0.0
            v["x_med"] = v["vistas"] / mediana if mediana else 0.0
        todos.extend(lote)
        resumen.append(f"{len(lote)} {etiqueta}s (mediana {int(mediana):,})")

    log(f"  · {nombre}: {' + '.join(resumen)} · {subs:,} subs"
        .replace(",", "."))
    return todos


def tabla(filas: list[dict], top: int) -> None:
    if not filas:
        print("\nSin resultados.")
        return
    print(f"\n{'ratio':>6}  {'x_med':>6}  {'vistas':>10}  canal · título")
    print("─" * 100)
    for v in filas[:top]:
        titulo = v["titulo"][:58]
        vistas = f"{v['vistas']:,}".replace(",", ".")
        print(f"{v['ratio']:>6.2f}  {v['x_med']:>6.2f}  {vistas:>10}  "
              f"{v['canal'][:22]} · {titulo}")
        print(f"{'':>26}{v['url']}")


def main() -> None:
    ap = argparse.ArgumentParser(
        description="Encuentra los vídeos outlier de varios canales de YouTube.")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--tema", help="temática; deduce los canales automáticamente")
    g.add_argument("--canales", nargs="+", help="handles o URLs de canal")
    ap.add_argument("--n-canales", type=int, default=5)
    ap.add_argument("--videos", type=int, default=30,
                    help="últimos vídeos por canal (por defecto 30). Es el "
                         "filtro de antigüedad: la pestaña viene ordenada de "
                         "más nuevo a más viejo.")
    ap.add_argument("--top", type=int, default=20)
    ap.add_argument("--min-ratio", type=float, default=0.0)
    ap.add_argument("--min-vistas", type=int, default=5000,
                    help="descarta vídeos por debajo de estas visitas (5000 "
                         "por defecto). Sin este suelo, un canal diminuto "
                         "cuela cualquier vídeo: con 3.000 suscriptores, 800 "
                         "visitas ya dan un ratio alto sin haber llegado a "
                         "nadie.")
    ap.add_argument("--csv", help="guarda el resultado completo en un CSV")
    args = ap.parse_args()

    canales = (args.canales if args.canales
               else buscar_canales(args.tema, args.n_canales))
    if not canales:
        sys.exit("No se han encontrado canales.")

    print(f"\nAnalizando {len(canales)} canales…")
    todos: list[dict] = []
    for c in canales:
        todos.extend(analizar_canal(c, args.videos))

    # El filtro va DESPUÉS de calcular la mediana de cada canal, para que la
    # mediana siga reflejando el rendimiento real y no solo los vídeos grandes.
    todos = [v for v in todos
             if v["ratio"] >= args.min_ratio and v["vistas"] >= args.min_vistas]
    todos.sort(key=lambda v: v["ratio"], reverse=True)

    tabla(todos, args.top)

    if args.csv:
        campos = ["ratio", "x_med", "tipo", "vistas", "subs", "canal",
                  "titulo", "duracion", "url"]
        with open(args.csv, "w", newline="", encoding="utf-8-sig") as f:
            w = csv.DictWriter(f, fieldnames=campos, extrasaction="ignore")
            w.writeheader()
            w.writerows(todos)
        print(f"\nCSV: {args.csv}  ({len(todos)} vídeos)")


if __name__ == "__main__":
    main()
