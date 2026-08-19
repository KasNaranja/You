# -*- coding: utf-8 -*-
"""Monta el vídeo con efectos de cámara y duraciones del audio real.

    python montar-video-efectos.py "<escenas.py>" "<imagenes>" "<tramos.json>" "<voz.wav>" "<salida.mp4>" [--gancho g.mp4]

Diferencias con montar-video.py (que queda para los vídeos sin efectos):

1. **Las duraciones salen de tramos.json**, la alineación carácter a carácter
   de la voz clonada. La imagen cambia donde de verdad empieza su frase.
2. **Cada escena lleva su efecto** («in», «out», «fijo»), declarado en
   escenas.py. El zoom es un 6% total, dure lo que dure la escena: la
   velocidad varía, la sensación no.
3. **El gancho se pega delante** tal cual (--gancho), sin reencodear.

El temblor del zoompan: zoompan trunca las coordenadas a enteros, y sobre la
imagen a resolución nativa el zoom avanza a saltos visibles. Se escala antes a
5760 px de ancho con lanczos y el salto pasa a ser subpíxel en el resultado.

Cada escena se codifica como segmento propio con GOP cerrado y parámetros
idénticos; el concat final va con -c copy, sin generación perdida.
"""
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

if len(sys.argv) < 6:
    sys.exit(__doc__)

ESCENAS, IMG, TRAMOS, VOZ, SALIDA = (Path(a) for a in sys.argv[1:6])
GANCHO = Path(sys.argv[sys.argv.index("--gancho") + 1]) if "--gancho" in sys.argv else None

ZOOM = 0.06          # 6% total por escena, sea cual sea su duración
FPS = 30
ANCHO_SUB = 5760     # escalado previo: el paso del zoom queda subpíxel

CODEC = ["-c:v", "libx264", "-profile:v", "high", "-preset", "medium", "-crf", "14",
         "-x264-params", "keyint=60:min-keyint=60:scenecut=0:bframes=2",
         "-pix_fmt", "yuv420p"]

spec = importlib.util.spec_from_file_location("e", str(ESCENAS))
e = importlib.util.module_from_spec(spec)
spec.loader.exec_module(e)

inicio = {t["id"]: t["inicio"] for t in json.loads(TRAMOS.read_text(encoding="utf-8"))}


def duracion(p):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "default=nw=1:nk=1", str(p)], capture_output=True, text=True)
    return float(r.stdout.strip())


total_voz = duracion(VOZ)
carpeta = SALIDA.parent / "_segmentos"
carpeta.mkdir(exist_ok=True)

# --- duración real de cada escena: hasta el arranque de la siguiente --------
escenas = e.ESCENAS
faltan = [x["id"] for x in escenas if not (IMG / (x["id"] + ".png")).exists()]
if faltan:
    sys.exit(f"faltan {len(faltan)} imagenes: {faltan[:10]}...")

for n, x in enumerate(escenas):
    ini = inicio[x["id"]]
    fin = inicio[escenas[n + 1]["id"]] if n + 1 < len(escenas) else total_voz
    x["_dur"] = round(fin - ini, 3)

# --- un segmento por escena --------------------------------------------------
def filtro(efecto, dur):
    frames = max(int(round(dur * FPS)), 1)
    base = f"scale={ANCHO_SUB}:-2:flags=lanczos,"
    centro = "x='iw/2-(iw/zoom)/2':y='ih/2-(ih/zoom)/2'"
    if efecto == "in":
        z = f"z='1+{ZOOM}*on/{frames}'"
    elif efecto == "out":
        z = f"z='{1 + ZOOM}-{ZOOM}*on/{frames}'"
    else:
        return f"scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2:black,fps={FPS},format=yuv420p"
    return base + f"zoompan={z}:{centro}:d=1:fps={FPS}:s=1920x1080,format=yuv420p"


print(f"escenas: {len(escenas)}   voz: {total_voz:.2f}s")
for n, x in enumerate(escenas):
    seg = carpeta / f"{x['id']}.mp4"
    if seg.exists() and abs(duracion(seg) - x["_dur"]) < 0.05:
        continue
    subprocess.run(
        ["ffmpeg", "-y", "-loglevel", "error", "-loop", "1", "-framerate", str(FPS),
         "-t", f"{x['_dur']:.3f}", "-i", str(IMG / (x["id"] + ".png")),
         "-vf", filtro(x["efecto"], x["_dur"]), "-t", f"{x['_dur']:.3f}", "-an",
         *CODEC, str(seg)],
        capture_output=True, check=True)
    if (n + 1) % 20 == 0:
        print(f"  {n + 1}/{len(escenas)}")

# --- concat de segmentos + voz ----------------------------------------------
lista = carpeta / "lista.txt"
lista.write_text("\n".join(f"file '{(carpeta / (x['id'] + '.mp4')).resolve().as_posix()}'"
                           for x in escenas) + "\n", encoding="utf-8")
cuerpo_mudo = carpeta / "_cuerpo_mudo.mp4"
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0",
                "-i", str(lista), "-c", "copy", str(cuerpo_mudo)], capture_output=True, check=True)

cuerpo = carpeta / "_cuerpo.mp4"
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(cuerpo_mudo), "-i", str(VOZ),
                "-map", "0:v", "-map", "1:a", "-c:v", "copy",
                "-c:a", "aac", "-b:a", "256k", "-ar", "48000", "-ac", "2",
                "-shortest", str(cuerpo)], capture_output=True, check=True)

# --- gancho delante, sin reencodear ------------------------------------------
if GANCHO:
    lista2 = carpeta / "lista2.txt"
    lista2.write_text(f"file '{GANCHO.resolve().as_posix()}'\n"
                      f"file '{cuerpo.resolve().as_posix()}'\n", encoding="utf-8")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0",
                    "-i", str(lista2), "-c", "copy", "-movflags", "+faststart",
                    str(SALIDA)], capture_output=True, check=True)
else:
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(cuerpo),
                    "-c", "copy", "-movflags", "+faststart", str(SALIDA)],
                   capture_output=True, check=True)

d = duracion(SALIDA)
m, s = divmod(int(round(d)), 60)
esperado = (duracion(GANCHO) if GANCHO else 0) + total_voz
print(f"\nLISTO: {SALIDA}")
print(f"{m}:{s:02d} ({d:.2f}s, esperado {esperado:.2f}s)   "
      f"{SALIDA.stat().st_size / 1024 / 1024:.1f} MB")
