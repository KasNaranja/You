# -*- coding: utf-8 -*-
"""Monta el vídeo final: imágenes atadas a las marcas de tiempo, más la voz.

    python montar-video.py "<escenas.py>" "<carpeta imagenes>" "<voz.wav>" "<salida.mp4>"

Cada imagen dura exactamente lo que el guion asigna a su frase, así que el
cambio de imagen cae en el segundo escrito. La última cubre hasta el final del
audio.

Sale con las especificaciones que recomienda YouTube: H.264 High, GOP cerrado de
2 s, yuv420p, AAC-LC a 48 kHz estéreo y el índice al principio del fichero.

Dos detalles que costaron encontrarse:

- **`-shortest` es obligatorio.** El demuxer concat necesita repetir el último
  fichero, y sin esa bandera el vídeo acaba durando varios segundos más que el
  audio.
- **CRF 14, no 20.** En dibujo de color plano, un origen pobre hace que el
  reencodeo de YouTube saque bandas alrededor de las líneas negras.
"""
import importlib.util
import subprocess
import sys
from pathlib import Path

if len(sys.argv) < 5:
    sys.exit(__doc__)

ESCENAS, IMG, VOZ, SALIDA = (Path(a) for a in sys.argv[1:5])

spec = importlib.util.spec_from_file_location("e", str(ESCENAS))
e = importlib.util.module_from_spec(spec)
spec.loader.exec_module(e)


def segundos(ident):
    m, s = ident.split("-")
    return int(m) * 60 + int(s)


def duracion(p):
    r = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(p)],
        capture_output=True, text=True)
    return float(r.stdout.strip())


IDS = sorted((g[0] for g in e.GUION), key=segundos)
total = duracion(VOZ)

filas, faltan, acum = [], [], 0.0
for n, ident in enumerate(IDS):
    img = IMG / f"{ident}.png"
    if not img.exists():
        faltan.append(ident)
        continue
    dur = (segundos(IDS[n + 1]) - segundos(ident)) if n + 1 < len(IDS) else total - acum
    acum += dur
    filas.append(f"file '{img.as_posix()}'")
    filas.append(f"duration {dur:.3f}")

if faltan:
    sys.exit(f"faltan imagenes: {faltan}")

filas.append(f"file '{(IMG / (IDS[-1] + '.png')).as_posix()}'")
lista = SALIDA.parent / "_lista_montaje.txt"
lista.write_text("\n".join(filas) + "\n", encoding="utf-8")
print(f"imagenes: {len(IDS)}   video: {acum:.2f}s   audio: {total:.2f}s")

subprocess.run(
    ["ffmpeg", "-y", "-loglevel", "error",
     "-f", "concat", "-safe", "0", "-i", str(lista),
     "-i", str(VOZ),
     "-vf", "scale=1920:1080:force_original_aspect_ratio=decrease,"
            "pad=1920:1080:(ow-iw)/2:(oh-ih)/2:black,fps=30,format=yuv420p",
     "-c:v", "libx264", "-profile:v", "high", "-preset", "slow", "-crf", "14",
     "-x264-params", "keyint=60:min-keyint=60:scenecut=0:bframes=2",
     "-af", "aresample=48000", "-ac", "2", "-c:a", "aac", "-b:a", "256k", "-ar", "48000",
     "-movflags", "+faststart", "-shortest", str(SALIDA)],
    capture_output=True, check=True)

lista.unlink(missing_ok=True)
d = duracion(SALIDA)
m, s = divmod(int(round(d)), 60)
print(f"\nLISTO: {SALIDA}")
print(f"{m}:{s:02d} ({d:.2f}s)   {SALIDA.stat().st_size / 1024 / 1024:.1f} MB")
