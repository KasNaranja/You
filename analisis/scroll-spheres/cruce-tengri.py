#!/usr/bin/env python3
"""Cruza el catálogo de @Scroll-Spheres con lo que ya ha adaptado @Tengri1337.

Tengri traduce a Scroll Spheres casi uno a uno, así que sus 39 shorts se
corresponden con 39 originales concretos. La correspondencia está escrita a
mano abajo —los títulos traducidos no coinciden literalmente, así que no hay
forma automática fiable de emparejarlos— y de ahí sale lo interesante: **qué
vídeos de Scroll Spheres funcionaron y Tengri todavía no ha tocado.**

    python3 analisis/scroll-spheres/cruce-tengri.py

Deja `hueco-vs-tengri.xlsx` con cuatro hojas: el catálogo entero marcando en qué
estado está cada vídeo, las candidatas libres que pasaron del millón con su
potencial, el rendimiento de cada adaptación de Tengri y el criterio de la
criba. La criba en sí vive en `potencial.py`.

Los colores del libro:
    verde  potencial alto, y libre
    gris   ya lo ha hecho Tengri
    azul   ya lo hemos hecho nosotros
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import potencial as pot  # noqa: E402

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


# Texto de la hoja «Criterio». (línea, en negrita)
CRITERIO = [
    ("Cómo se ha hecho la criba", True),
    ("", False),
    ("Tengri traduce a Scroll Spheres uno a uno, así que sus 39 shorts son un "
     "experimento ya pagado: sabemos qué original rindió y cuál no al pasarlo "
     "al castellano. El verde sale de ahí, no de una intuición.", False),
    ("", False),
    ("Las cuatro preguntas", True),
    ("1. ¿Se entiende en los tres primeros segundos, sin haber visto la "
     "película?", False),
    ("2. ¿Hay algo físico que ver, o es un dato que hay que contar?", False),
    ("3. ¿Sobrevive a la traducción? Los acentos, los juegos de palabras y las "
     "frases míticas en inglés se mueren en castellano, y más con el doblaje.", False),
    ("4. ¿La película o el actor significan algo en España?", False),
    ("", False),
    ("Las cuatro a favor es «alto» y va en verde. Una en contra, «medio». Dos o "
     "más, «bajo».", False),
    ("", False),
    ("Por qué no basta con ordenar por visitas", True),
    ("De los shorts que Tengri adaptó, los tres originales de 39 millones le "
     "retuvieron un 2,6 %, un 0,7 % y un 0,6 %. En cambio Transporter 2, que en "
     "Scroll Spheres se quedó en 26.000 visitas, le hizo 468.000; y Anton "
     "Chigurh, con 43.000 de origen, le hizo 352.000. La mediana de conversión "
     "es del 1,9 %, pero el reparto no guarda relación con el tamaño del "
     "original.", False),
    ("", False),
    ("Con una salvedad honesta: parte de sus cifras bajas son de shorts recién "
     "publicados. Aun así, entre los más antiguos hay tanto 4,7 millones como "
     "1.400 visitas, así que la varianza es real y no solo cuestión de "
     "antigüedad.", False),
    ("", False),
    ("El corte del millón", True),
    ("De los 1.758 shorts del canal, 1.476 no llegan a 100.000 visitas y la "
     "mediana está en 25.000. Los 100 mejores se llevan el 87 % de los mil "
     "millones de visitas. Por debajo del millón hay muy poco que rascar, y por "
     "eso la hoja de candidatas corta ahí.", False),
    ("", False),
    ("Colores", True),
    ("verde: libre y de potencial alto — por aquí se empieza", False),
    ("gris: lo tiene Tengri — se puede hacer igual, pero compites de frente", False),
    ("azul: ya lo hemos preparado nosotros", False),
    ("sin color: libre, de potencial medio o bajo", False),
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
        tuyo = v["id"] in pot.TUYOS
        v["estado"] = ("ya es tuyo (y de Tengri)" if tuyo and adapt else
                       "ya es tuyo" if tuyo else
                       "lo tiene Tengri" if adapt else "libre")
        v["potencial"], v["porque"] = pot.POTENCIAL.get(v["titulo"], ("", ""))

    ss.sort(key=lambda v: v["vistas"] or 0, reverse=True)

    from openpyxl import Workbook
    from openpyxl.styles import Alignment, Font, PatternFill
    from openpyxl.utils import get_column_letter

    verde = PatternFill("solid", fgColor="C6EFCE")   # potencial alto
    gris = PatternFill("solid", fgColor="DDDDDD")    # ya cogido
    azul = PatternFill("solid", fgColor="DDEBF7")    # ya es tuyo

    def pintar(hoja, v):
        relleno = (azul if v["estado"].startswith("ya es tuyo") else
                   gris if v["estado"] == "lo tiene Tengri" else
                   verde if v["potencial"] == "alto" else None)
        if relleno:
            for c in hoja[hoja.max_row]:
                c.fill = relleno

    wb = Workbook()
    ws = wb.active
    ws.title = "Hueco"
    ws.append(["#", "Título (Scroll Spheres)", "Visitas SS", "Estado",
               "Visitas Tengri", "Potencial", "Por qué"])
    for c in ws[1]:
        c.font = Font(bold=True)

    for i, v in enumerate(ss, 1):
        ws.append([i, v["titulo"], v["vistas"], v["estado"], v["tengri_vistas"],
                   v["potencial"], v["porque"]])
        pintar(ws, v)

    for col, ancho in ((1, 6), (2, 74), (3, 13), (4, 16), (5, 14), (6, 11), (7, 92)):
        ws.column_dimensions[get_column_letter(col)].width = ancho
    for fila in ws.iter_rows(min_row=2, min_col=3, max_col=6):
        fila[0].number_format = fila[2].number_format = "#,##0"
        fila[1].alignment = Alignment(horizontal="center")
        fila[3].alignment = Alignment(horizontal="center")
    ws.freeze_panes = "C2"
    ws.auto_filter.ref = f"A1:G{ws.max_row}"

    cogidos = [v for v in ss if v["tengri"]]
    libres = [v for v in ss if v["estado"] == "libre"]

    # Segunda hoja: lo que de verdad hay que mirar. El catálogo entero son
    # 1.758 filas de las que 1.476 no llegan a 100.000 visitas; la cola larga
    # no dice nada.
    # Ordenados por potencial primero y por visitas después: la lista se lee
    # de arriba abajo y lo verde queda junto.
    orden = {"alto": 0, "medio": 1, "bajo": 2, "": 3}
    candidatas = sorted([x for x in libres if (x["vistas"] or 0) >= 1_000_000],
                        key=lambda v: (orden[v["potencial"]], -(v["vistas"] or 0)))

    h2 = wb.create_sheet("Libres +1M")
    h2.append(["#", "Título (Scroll Spheres)", "Visitas SS", "Potencial", "Por qué"])
    for c in h2[1]:
        c.font = Font(bold=True)
    for i, v in enumerate(candidatas, 1):
        h2.append([i, v["titulo"], v["vistas"], v["potencial"], v["porque"]])
        pintar(h2, v)
    for col, ancho in ((1, 6), (2, 74), (3, 13), (4, 11), (5, 96)):
        h2.column_dimensions[get_column_letter(col)].width = ancho
    for fila in h2.iter_rows(min_row=2, min_col=3, max_col=4):
        fila[0].number_format = "#,##0"
        fila[1].alignment = Alignment(horizontal="center")
    h2.freeze_panes = "C2"
    h2.auto_filter.ref = f"A1:E{h2.max_row}"

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

    # Cuarta hoja: de dónde sale el verde, para que la criba se pueda discutir
    # en vez de tener que creérsela.
    h4 = wb.create_sheet("Criterio")
    h4.column_dimensions["A"].width = 118
    for linea, negrita in CRITERIO:
        h4.append([linea])
        if negrita:
            h4[h4.max_row][0].font = Font(bold=True)
        h4[h4.max_row][0].alignment = Alignment(wrap_text=True, vertical="top")

    for hoja, col in ((ws, "G"), (h2, "E")):
        for fila in hoja.iter_rows(min_row=2, min_col=hoja.max_column,
                                   max_col=hoja.max_column):
            fila[0].alignment = Alignment(wrap_text=True, vertical="top")

    wb.save(AQUI / "hueco-vs-tengri.xlsx")

    altos = [v for v in candidatas if v["potencial"] == "alto"]
    print(f"✓ hueco-vs-tengri.xlsx · {len(ss)} shorts de Scroll Spheres")
    print(f"  {len(cogidos)} los tiene Tengri · {len(pot.TUYOS)} ya son tuyos "
          f"· {len(libres)} libres")
    print(f"  sin localizar el original: {len(SIN_LOCALIZAR)} shorts de Tengri")
    print(f"  candidatas libres con +1M: {len(candidatas)}, "
          f"de las que {len(altos)} en verde")
    for corte in (10_000_000, 5_000_000, 1_000_000):
        n = sum(1 for v in libres if (v["vistas"] or 0) >= corte)
        print(f"  libres con más de {corte:,} visitas: {n}".replace(",", "."))


if __name__ == "__main__":
    main()
