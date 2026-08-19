#!/usr/bin/env python3
"""Genera la portada de un Short: marca del canal + titular + cuerpo.

Reproduce el formato de los canales de clips que funcionan: logo y nombre
arriba, titular en amarillo con tipografía condensada pesada, cuerpo en blanco
centrado, y el resto del lienzo libre para el clip de vídeo.

    python3 herramientas/portada-short.py \
        --logo logo.png \
        --nombre MejoresClipsCine --handle @MejoresClipsCine-real \
        --titular "LO DELATÓ SU PISTOLA" \
        --cuerpo "Fíjate en cómo pelea con la funda..." \
        --salida portada

Deja dos ficheros: `<salida>-transparente.png` para superponer sobre el clip y
`<salida>-negro.png` para ver cómo queda.
"""
from __future__ import annotations

import argparse
import sys
import urllib.request
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

SS = 3          # supermuestreo: se dibuja grande y se reduce, bordes limpios
W, H = 1080, 1920

AMARILLO = (255, 221, 0)
GRIS = (170, 170, 170)
BLANCO = (255, 255, 255)

# Anton es la condensada pesada que usan estos canales. Es gratuita (OFL).
ANTON_URL = ("https://cdn.jsdelivr.net/gh/google/fonts@main/ofl/anton/"
             "Anton-Regular.ttf")
CACHE = Path.home() / ".cache" / "portada-short"

CANDIDATAS_BOLD = [
    "C:/Windows/Fonts/arialbd.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
]
CANDIDATAS_REG = [
    "C:/Windows/Fonts/arial.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    "/System/Library/Fonts/Supplemental/Arial.ttf",
]


def primera_que_exista(rutas: list[str]) -> str:
    for r in rutas:
        if Path(r).exists():
            return r
    sys.exit("No se ha encontrado ninguna fuente Arial/Liberation en el sistema.")


def anton() -> str:
    """Descarga Anton la primera vez y la reutiliza después."""
    destino = CACHE / "Anton-Regular.ttf"
    if destino.exists() and destino.stat().st_size > 50_000:
        return str(destino)
    CACHE.mkdir(parents=True, exist_ok=True)
    print("Descargando la tipografía Anton (solo la primera vez)…")
    try:
        req = urllib.request.Request(ANTON_URL, headers={"User-Agent": "Mozilla/5.0"})
        destino.write_bytes(urllib.request.urlopen(req, timeout=60).read())
    except Exception as e:
        sys.exit(f"No se ha podido descargar Anton: {e}")
    return str(destino)


def redondear(ruta: str, d: int) -> Image.Image:
    """Recorta el logo en círculo con máscara suavizada."""
    im = Image.open(ruta).convert("RGBA").resize((d, d), Image.LANCZOS)
    m = Image.new("L", (d * 4, d * 4), 0)
    ImageDraw.Draw(m).ellipse([0, 0, d * 4 - 1, d * 4 - 1], fill=255)
    im.putalpha(m.resize((d, d), Image.LANCZOS))
    return im


def ajustar(dib, texto: str, fuente_ruta: str, ancho: int, inicial: int) -> ImageFont.FreeTypeFont:
    """Mayor cuerpo que quepa en `ancho`. Evita partir el titular en dos líneas."""
    tam = inicial
    while tam > 20 * SS:
        f = ImageFont.truetype(fuente_ruta, tam)
        if dib.textlength(texto, font=f) <= ancho:
            return f
        tam -= 2 * SS
    return ImageFont.truetype(fuente_ruta, tam)


def envolver(dib, texto: str, fuente, ancho: int) -> list[str]:
    """Corta por medida real del texto, no por número de caracteres."""
    lineas, actual = [], ""
    for palabra in texto.split():
        prueba = (actual + " " + palabra).strip()
        if dib.textlength(prueba, font=fuente) <= ancho:
            actual = prueba
        else:
            if actual:
                lineas.append(actual)
            actual = palabra
    if actual:
        lineas.append(actual)
    return lineas


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--logo", required=True)
    ap.add_argument("--nombre", required=True)
    ap.add_argument("--handle", required=True)
    ap.add_argument("--titular", required=True)
    ap.add_argument("--cuerpo", required=True)
    ap.add_argument("--salida", default="portada")
    ap.add_argument("--y-marca", type=int, default=102)
    ap.add_argument("--y-titular", type=int, default=300)
    args = ap.parse_args()

    BOLD, REG, TIT = primera_que_exista(CANDIDATAS_BOLD), primera_que_exista(CANDIDATAS_REG), anton()

    lienzo = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0))
    d = ImageDraw.Draw(lienzo)

    # ── marca del canal ──
    d_logo, hueco = 130 * SS, 26 * SS
    f_nom = ImageFont.truetype(BOLD, 52 * SS)
    f_han = ImageFont.truetype(REG, 33 * SS)
    d_badge, hueco_badge = 30 * SS, 12 * SS

    w_nom = d.textlength(args.nombre, font=f_nom)
    w_han = d.textlength(args.handle, font=f_han)
    gw = int(d_logo + hueco + max(w_nom + hueco_badge + d_badge, w_han))
    gx, gy = (W * SS - gw) // 2, args.y_marca * SS

    lienzo.alpha_composite(redondear(args.logo, d_logo), (gx, gy))
    tx = gx + d_logo + hueco
    ty = gy + (d_logo - (f_nom.size * 1.02 + f_han.size * 1.15)) / 2
    d.text((tx, ty), args.nombre, font=f_nom, fill=BLANCO)

    bx, by = tx + w_nom + hueco_badge, ty + f_nom.size * 0.30
    d.ellipse([bx, by, bx + d_badge, by + d_badge], fill=(150, 150, 150, 255))
    r = d_badge
    d.line([(bx + r * .27, by + r * .52), (bx + r * .43, by + r * .68),
            (bx + r * .75, by + r * .33)], fill=BLANCO, width=int(3.2 * SS), joint="curve")
    d.text((tx, ty + f_nom.size * 1.12), args.handle, font=f_han, fill=GRIS)

    # ── titular ──
    f_tit = ajustar(d, args.titular.upper(), TIT, int(W * .84) * SS, 130 * SS)
    y_tit = args.y_titular * SS
    d.text((W * SS / 2, y_tit), args.titular.upper(), font=f_tit,
           fill=AMARILLO, anchor="ma")

    # ── cuerpo ──
    f_cue = ImageFont.truetype(BOLD, 44 * SS)
    lineas = envolver(d, args.cuerpo, f_cue, int(W * .79) * SS)
    y = y_tit + f_tit.size * 1.52
    for ln in lineas:
        d.text((W * SS / 2, y), ln, font=f_cue, fill=BLANCO, anchor="ma")
        y += f_cue.size * 1.32

    lienzo = lienzo.resize((W, H), Image.LANCZOS)
    lienzo.save(f"{args.salida}-transparente.png")
    negro = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    negro.alpha_composite(lienzo)
    negro.convert("RGB").save(f"{args.salida}-negro.png")

    libre = int(y / SS)
    print(f"✓ {args.salida}-transparente.png y -negro.png  ({W}x{H})")
    print(f"  titular {f_tit.size // SS}px · cuerpo en {len(lineas)} líneas")
    print(f"  el clip puede empezar en y={libre} ({H - libre} px libres)")
    if libre > 1000:
        print("  ! El texto ocupa más de la mitad del alto: acorta el cuerpo.")


if __name__ == "__main__":
    main()
