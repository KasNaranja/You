#!/usr/bin/env python3
"""Cruza el catálogo de @Scroll-Spheres con lo que ya ha adaptado @Tengri1337.

Tengri traduce a Scroll Spheres casi uno a uno, así que sus 39 shorts se
corresponden con 39 originales concretos. La correspondencia está escrita a
mano abajo —los títulos traducidos no coinciden literalmente, así que no hay
forma automática fiable de emparejarlos— y de ahí sale lo interesante: **qué
vídeos de Scroll Spheres funcionaron y Tengri todavía no ha tocado.**

    python3 analisis/scroll-spheres/cruce-tengri.py

Deja `hueco-vs-tengri.xlsx` con las tres columnas de siempre más dos: si Tengri
ya lo ha hecho y cuántas visitas le sacó.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI.parent.parent / "herramientas"))

# Título de Scroll Spheres ← short de Tengri que lo adapta.
# Se empareja por el título original porque los identificadores de Tengri no
# dicen nada sobre qué original están versionando.
ADAPTADOS = {
    "Insurance Companies Blacklisted Jackie Chan": "Jackie Chan Is Too Risky for Insurance Companies",
    "Tom Cruise Spent 5 Months Preparing For This Scene": "Tom Cruise Pasó 5 Meses Preparándose Para Esta Escena",
    "Ledger Ignored Nolan & Nailed It - The Dark Knight": "Ledger Improvised This Scene in One Take",
    "A $500,000 IMAX Camera Got Destroyed": "Catwoman Destruyó una Cámara de $500.000",
    "Jackie Chan Performs His Own Stunts - Rush Hour 3": "Jackie Chan Risked His Life For This Scene",
    "The Weapon That Defines Anton Chigurh": "The Terrifying Mindset of Anton Chigurh",
    "Kylo Ren Had The Most Terrifying Entrance": "Kylo Ren's Terrifying Entrance",
    "Jackie Chan Jumped Down 10 Stories At 52 Years Old": "Jackie Chan Rappelled Down 10 Floors Without CGI",
    "Christopher Lloyd Is Built Different - Nobody": "Christopher Lloyd Se Negó a Usar Armas Falsas",
    "Jason Statham Struggled With This Transporter 2 Scene": "Jason Statham Needed 12 Takes for This Scene",
    "The Narrator Did This To Get Rid of Tyler": "El Narrador Hizo Esto Para Deshacerse de Tyler",
    "He Finally Stared At The Baba Yaga - John Wick": "Finalmente Se Encontró Cara a Cara con Baba Yaga",
    "The Bullet Realism In John Wick: Chapter 3": "El Realismo de las Balas en John Wick: Capítulo 3",
    "The Realism Behind Ammo Tracking In John Wick 2": "El Realismo Detrás del Conteo de Balas en John Wick 2",
    "Gosling Faced His Fear For This Scene The Fall Guy": "Gosling Se Enfrentó a Su Miedo Para Esta Escena",
    "Why John Press Checks His Kimber - John Wick 2": "Why John Checks the Chamber of His Kimber",
    "The Ultimate John Wick Flex": "La Demostración de Poder Definitiva de John Wick",
    "Keanu Reeves' Stuntman Is A Legend - John Wick 3": "Keanu Reeves' Stunt Double Is a Legend",
    "The Coldest Flex In Movie History - John Wick 2": "La Demostración de Poder Más Brutal de la Historia del Cine",
    "He Knew To Leave Immediately - Nobody (2021)": "He Knew He Had to Leave Immediately",
    "Why Grace Reacts Like That In Project Hail Mary": "Why Grace Reacts That Way in Project Hail Mary",
    "The Toughest Henchman In John Wick 2": "El Secuaz Más Duro de John Wick 2",
    "The Marquis Was Doomed Either Way - John Wick 4": "The Marquis Was Doomed Either Way",
    "He Stopped The Gun With His Pinky - Nobody": "Detuvo el Arma con el Meñique",
    "Hunting Jaguar Paw On His Own Ground Was A Mistake": "Cazar a Jaguar Paw en Su Propio Territorio Fue un Error",
    "Vikings Mistook An Alien For A Dragon In Outlander": "Los Vikingos Confundieron a un Alienígena con un Dragón",
    "Apocalypto Is A Criminally Underrated Masterpiece": "Apocalypto Es una Obra Maestra Injustamente Infravalorada",
    "Nolan Pushed Anne Hathaway To Do Her Own Stunts": "Nolan Pushed Anne Hathaway to Do Her Own Stunts",
    "Keanu Called This Stuntman A Legend - John Wick": "Keanu Llamó a Este Especialista una Leyenda",
    "The Darkest Moment In Movie History - The Crow": "The Darkest Moment in Film History",
    "In Nobody He Strapped A Claymore To A Glass Shield": "En Nobody, Ató Una Mina Claymore a un Escudo de Cristal",
    "One Bullet Against An Ancient God - The Ritual": "Una Bala Contra un Dios Antiguo",
    # Scroll Spheres tiene dos shorts de Project Power. Tengri habla de un
    # impacto concreto, así que apunta a este y no al general de 10 M.
    "That Face Ripple Was 100% Practical Project Power": "Este Impacto de Bala Fue Real — Project Power",
}

# Shorts de Tengri cuyo original no he sabido localizar en el catálogo. Se
# listan para no dar por libre un tema que quizá ya esté cogido.
SIN_LOCALIZAR = [
    "I Didn't Have a Plan B",
    "Failed to Defuse the Nuclear Bomb — Fallout",
    "Este Detalle Reveló Que No Era un Policía de Verdad",
    "10 Años Después, Sigue Siendo el Mejor Deslizamiento del Cine — Maze Runner",
    "Tom Cruise Confió Su Vida a Hiroyuki Sanada — The Last Samurai",
    "Keanu Reeves Cobraba $39.000 Por Palabra — John Wick 4",
]


def tengri() -> dict[str, int]:
    """Visitas de cada short de Tengri, por título."""
    r = subprocess.run(
        ["yt-dlp", "--flat-playlist", "-J", "--no-warnings",
         "https://www.youtube.com/@Tengri1337/shorts"],
        capture_output=True, text=True, timeout=900)
    if r.returncode != 0:
        sys.exit(f"yt-dlp ha fallado:\n{r.stderr.strip()[-500:]}")
    return {e["title"]: e.get("view_count") or 0
            for e in json.loads(r.stdout).get("entries") or []}


def main() -> None:
    ss = json.loads((AQUI / "shorts-scrollspheres-catalogo.json").read_text("utf8"))
    tg = tengri()

    # Los títulos de Tengri en ADAPTADOS son un prefijo del real (llevan
    # « — Película» detrás), así que se busca por comienzo de cadena.
    def visitas_tengri(titulo_tg: str) -> int | None:
        for t, v in tg.items():
            if t.startswith(titulo_tg[:40]):
                return v
        return None

    for v in ss:
        adapt = ADAPTADOS.get(v["titulo"])
        v["tengri"] = "sí" if adapt else ""
        v["tengri_vistas"] = visitas_tengri(adapt) if adapt else None

    ss.sort(key=lambda v: v["vistas"] or 0, reverse=True)

    from openpyxl import Workbook
    from openpyxl.styles import Alignment, Font, PatternFill
    from openpyxl.utils import get_column_letter

    wb = Workbook()
    ws = wb.active
    ws.title = "Hueco"
    ws.append(["#", "Título (Scroll Spheres)", "Visitas SS",
               "¿Tengri lo ha hecho?", "Visitas Tengri"])
    for c in ws[1]:
        c.font = Font(bold=True)

    gris = PatternFill("solid", fgColor="DDDDDD")
    for i, v in enumerate(ss, 1):
        ws.append([i, v["titulo"], v["vistas"], v["tengri"], v["tengri_vistas"]])
        if v["tengri"]:
            for c in ws[ws.max_row]:
                c.fill = gris          # lo cogido se ve de un vistazo

    for col, ancho in ((1, 6), (2, 78), (3, 13), (4, 18), (5, 14)):
        ws.column_dimensions[get_column_letter(col)].width = ancho
    for fila in ws.iter_rows(min_row=2, min_col=3, max_col=5):
        fila[0].number_format = "#,##0"
        fila[1].alignment = Alignment(horizontal="center")
        fila[2].number_format = "#,##0"
    ws.freeze_panes = "A2"
    ws.auto_filter.ref = f"A1:E{ws.max_row}"

    cogidos = [v for v in ss if v["tengri"]]
    libres = [v for v in ss if not v["tengri"]]

    # Segunda hoja: lo que de verdad hay que mirar. El catálogo entero son
    # 1.758 filas de las que 1.476 no llegan a 100.000 visitas; la cola larga
    # no dice nada.
    h2 = wb.create_sheet("Libres +1M")
    h2.append(["#", "Título (Scroll Spheres)", "Visitas SS"])
    for c in h2[1]:
        c.font = Font(bold=True)
    for i, v in enumerate([x for x in libres if (x["vistas"] or 0) >= 1_000_000], 1):
        h2.append([i, v["titulo"], v["vistas"]])
    for col, ancho in ((1, 6), (2, 86), (3, 13)):
        h2.column_dimensions[get_column_letter(col)].width = ancho
    for fila in h2.iter_rows(min_row=2, min_col=3, max_col=3):
        fila[0].number_format = "#,##0"
    h2.freeze_panes = "A2"

    # Tercera hoja: qué le rindió a Tengri cada adaptación. Es lo único que
    # dice de verdad cuánto se traduce una cifra inglesa al castellano.
    h3 = wb.create_sheet("Rendimiento Tengri")
    h3.append(["Título (Scroll Spheres)", "Visitas SS", "Visitas Tengri", "% que retiene"])
    for c in h3[1]:
        c.font = Font(bold=True)
    for v in sorted(cogidos, key=lambda x: -(x["tengri_vistas"] or 0)):
        a, b = v["vistas"] or 0, v["tengri_vistas"]
        h3.append([v["titulo"], a, b, (b / a) if (a and b is not None) else None])
    for col, ancho in ((1, 70), (2, 13), (3, 14), (4, 14)):
        h3.column_dimensions[get_column_letter(col)].width = ancho
    for fila in h3.iter_rows(min_row=2, min_col=2, max_col=4):
        fila[0].number_format = fila[1].number_format = "#,##0"
        fila[2].number_format = "0,0%"
    h3.freeze_panes = "A2"

    wb.save(AQUI / "hueco-vs-tengri.xlsx")
    print(f"✓ hueco-vs-tengri.xlsx · {len(ss)} shorts de Scroll Spheres")
    print(f"  {len(cogidos)} ya adaptados por Tengri, {len(libres)} libres")
    print(f"  sin localizar el original: {len(SIN_LOCALIZAR)} shorts de Tengri")
    for corte in (10_000_000, 5_000_000, 1_000_000):
        n = sum(1 for v in libres if (v["vistas"] or 0) >= corte)
        print(f"  libres con más de {corte:,} visitas: {n}".replace(",", "."))


if __name__ == "__main__":
    main()
