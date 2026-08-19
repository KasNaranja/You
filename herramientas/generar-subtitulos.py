# -*- coding: utf-8 -*-
"""Genera subtítulos estilo THE QUICK (CapCut) desde la alineación de palabras.

    python generar-subtitulos.py "<palabras.json>" "<salida.ass>" "<salida.srt>"

`palabras.json` es una lista de {"w": palabra, "ini": seg, "fin": seg} con el
tiempo REAL de cada palabra — sale del forced-alignment de ElevenLabs sobre el
audio del vídeo (ver el vídeo 5 como referencia de cómo obtenerlo).

El estilo, calcado del preset «THE QUICK» de CapCut Pro:

- Bloques de hasta 6 palabras, siempre visibles enteros. La puntuación corta
  solo si el bloque ya tiene 3+ palabras: si corta siempre, el guion de frases
  cortas produce bloques de 2 palabras y el efecto se vuelve metralleta.
- La palabra que suena se ilumina en AMARILLO en su milisegundo exacto.
- Pop sutil solo al entrar cada bloque (86%→100% en 70 ms), no por palabra.
- Komika Axis 72 px (en `mundo en piezas/recursos/fuentes/`), MAYÚSCULAS,
  contorno negro de 8, sombra 4, abajo centrado.

Para grabarlos en el vídeo:

    ffmpeg -i video.mp4 -vf "subtitles=subs.ass:fontsdir=<carpeta con KOMIKAX_.ttf>" ...

El `.srt` es el mismo texto en plano, para subirlo como CC de YouTube.
"""
import json
import sys
from pathlib import Path

if len(sys.argv) < 4:
    sys.exit(__doc__)

PALABRAS, ASS, SRT = (Path(a) for a in sys.argv[1:4])

MAX_PALABRAS = 6
MIN_CORTE = 3       # la puntuación solo corta a partir de aquí
MAX_DUR = 2.6

palabras = json.loads(PALABRAS.read_text(encoding="utf-8"))

bloques, actual = [], []
for p in palabras:
    actual.append(p)
    fin_frase = p["w"].rstrip()[-1:] in ".:?!"
    dur = actual[-1]["fin"] - actual[0]["ini"]
    if (fin_frase and len(actual) >= MIN_CORTE) or len(actual) >= MAX_PALABRAS or dur > MAX_DUR:
        bloques.append(actual)
        actual = []
if actual:
    if len(actual) < MIN_CORTE and bloques:
        bloques[-1].extend(actual)
    else:
        bloques.append(actual)


def t(seg):
    h = int(seg // 3600)
    m = int(seg % 3600 // 60)
    return f"{h}:{m:02d}:{seg % 60:05.2f}"


def st(seg):
    h = int(seg // 3600)
    m = int(seg % 3600 // 60)
    return f"{h:02d}:{m:02d}:{int(seg % 60):02d},{int(seg % 1 * 1000):03d}"


AMARILLO = r"{\c&H00E6FF&}"
BLANCO = r"{\c&HFFFFFF&}"
POP = r"{\fscx86\fscy86\t(0,70,\fscx100\fscy100)}"

lineas = ["""[Script Info]
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Quick,Komika Axis,72,&H00FFFFFF,&H00FFFFFF,&H00000000,&H96000000,0,0,0,0,100,100,1,0,1,8,4,2,100,100,56,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"""]
srt = []

for nb, b in enumerate(bloques):
    fin_bloque = b[-1]["fin"]
    if nb + 1 < len(bloques):
        fin_bloque = min(bloques[nb + 1][0]["ini"], fin_bloque + 0.3)
    for i, p in enumerate(b):
        ini = p["ini"] if i > 0 else b[0]["ini"]
        fin = b[i + 1]["ini"] if i + 1 < len(b) else fin_bloque
        if fin <= ini:
            continue
        trozos = [(AMARILLO + q["w"].upper() + BLANCO) if j == i else q["w"].upper()
                  for j, q in enumerate(b)]
        pop = POP if i == 0 else ""
        lineas.append(f"Dialogue: 0,{t(ini)},{t(fin)},Quick,,0,0,0,,{pop}{' '.join(trozos)}")
    srt.append(f"{nb + 1}\n{st(b[0]['ini'])} --> {st(fin_bloque)}\n"
               f"{' '.join(p['w'] for p in b)}\n")

ASS.write_text("\n".join(lineas), encoding="utf-8")
SRT.write_text("\n".join(srt), encoding="utf-8")
media = sum(len(b) for b in bloques) / len(bloques)
print(f"bloques: {len(bloques)}   media: {media:.1f} palabras   eventos ASS: {len(lineas) - 13}")
