# -*- coding: utf-8 -*-
"""Genera la voz de un vídeo, calibrada a las marcas de tiempo del guion.

    python generar-voz.py "<ruta a escenas.py>" "<carpeta de salida>"

El fichero de escenas debe exponer GUION como lista de tuplas cuyo primer
elemento sea el identificador `M-SS` y el segundo el texto hablado.

Cómo funciona, y por qué así:

1. **Se recorta el silencio propio de edge-tts.** Cada clip trae ~0,23 s delante
   y ~0,85 s detrás. Sin recortarlo, el hueco real entre frases se va a 1,2 s y
   la voz se descuelga del guion.
2. **Se calibra la velocidad línea a línea.** Si el habla no cabe en su hueco,
   se regenera más rápida hasta que quepa. Un narrador real hace lo mismo.
3. **Se rellena el resto con silencio**, para que la frase siguiente arranque
   en su segundo exacto.
4. **El montaje va en WAV, no en MP3.** Concatenar MP3 arrastra ~60 ms de
   relleno del codificador por unión: en 300 trozos son 17 segundos de deriva,
   con cada frase llegando más tarde que la anterior. No lo delata ningún error.
"""
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

if len(sys.argv) < 3:
    sys.exit(__doc__)

ESCENAS = Path(sys.argv[1])
SALIDA = Path(sys.argv[2])
SALIDA.mkdir(parents=True, exist_ok=True)
TROZOS = SALIDA / "trozos"
WAVS = SALIDA / "wav"
TROZOS.mkdir(exist_ok=True)
WAVS.mkdir(exist_ok=True)

spec = importlib.util.spec_from_file_location("e", str(ESCENAS))
e = importlib.util.module_from_spec(spec)
spec.loader.exec_module(e)

RECORTE = (
    "silenceremove=start_periods=1:start_silence=0:start_threshold=-45dB:detection=peak,"
    "areverse,"
    "silenceremove=start_periods=1:start_silence=0:start_threshold=-45dB:detection=peak,"
    "areverse"
)
CADENA = (
    "highpass=f=85,"
    "equalizer=f=250:t=q:w=1.2:g=-2.5,"
    "equalizer=f=3200:t=q:w=1.5:g=2.5,"
    "acompressor=threshold=-18dB:ratio=3:attack=8:release=120,"
    "loudnorm=I=-16:TP=-1.5:LRA=11"
)
VOZ = "es-ES-AlvaroNeural"
HUECO_MIN = 0.12
RITMOS = [15, 22, 30, 38, 48, 60]


def segundos(ident):
    m, s = ident.split("-")
    return int(m) * 60 + int(s)


def duracion(p):
    r = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(p)],
        capture_output=True, text=True)
    return float(r.stdout.strip())


LINEAS = sorted([(g[0], g[1]) for g in e.GUION], key=lambda x: segundos(x[0]))
print(f"lineas: {len(LINEAS)}   de {segundos(LINEAS[0][0])}s a {segundos(LINEAS[-1][0])}s\n")

apretadas, desbordes = 0, []
for n, (ident, texto) in enumerate(LINEAS):
    hueco = (segundos(LINEAS[n + 1][0]) - segundos(ident)) if n + 1 < len(LINEAS) else None
    limpio = TROZOS / f"{ident}.mp3"
    elegido = None
    for k, pct in enumerate(RITMOS):
        bruto = TROZOS / f"{ident}_b.mp3"
        subprocess.run(
            [sys.executable, "-m", "edge_tts", "--voice", VOZ, "--rate", f"+{pct}%",
             "--text", texto, "--write-media", str(bruto)],
            capture_output=True, check=True)
        subprocess.run(
            ["ffmpeg", "-y", "-loglevel", "error", "-i", str(bruto),
             "-af", RECORTE, "-q:a", "2", str(limpio)],
            capture_output=True, check=True)
        d = duracion(limpio)
        if hueco is None or d <= hueco - HUECO_MIN:
            elegido = d
            if k > 0:
                apretadas += 1
            break
    if elegido is None:
        elegido = duracion(limpio)
        desbordes.append((ident, round(elegido, 2), hueco))
    if (n + 1) % 30 == 0:
        print(f"  {n + 1}/{len(LINEAS)}")

piezas, tramos, reloj = [], [], 0.0
for n, (ident, _t) in enumerate(LINEAS):
    wav = WAVS / f"{ident}.wav"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(TROZOS / f"{ident}.mp3"),
                    "-ar", "24000", "-ac", "1", str(wav)], capture_output=True, check=True)
    d = duracion(wav)
    piezas.append(wav)
    tramos.append((ident, round(reloj, 3), round(d, 3)))
    reloj += d
    if n + 1 < len(LINEAS):
        resto = round((segundos(LINEAS[n + 1][0]) - segundos(ident)) - d, 3)
        if resto > 0.001:
            sil = WAVS / f"{ident}_sil.wav"
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi",
                            "-i", "anullsrc=r=24000:cl=mono", "-t", f"{resto:.3f}", str(sil)],
                           capture_output=True, check=True)
            piezas.append(sil)
            reloj += duracion(sil)

lista = WAVS / "lista.txt"
lista.write_text("\n".join(f"file '{p.as_posix()}'" for p in piezas) + "\n", encoding="utf-8")
crudo = SALIDA / "crudo.wav"
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0",
                "-i", str(lista), "-c", "copy", str(crudo)], capture_output=True, check=True)
final = SALIDA / "voz.wav"
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(crudo),
                "-af", CADENA, str(final)], capture_output=True, check=True)

total = duracion(final)
m, s = divmod(int(round(total)), 60)
esperado = segundos(LINEAS[-1][0]) + tramos[-1][2]
peor = max((abs(ini - segundos(i)), i, ini - segundos(i)) for i, ini, _d in tramos)
print(f"\nvoz: {m}:{s:02d} ({total:.2f}s)")
print(f"esperado: {esperado:.2f}s   diferencia: {total - esperado:+.3f}s")
print(f"peor desvio: {peor[1]} -> {peor[2]:+.3f}s")
print(f"aceleradas: {apretadas}")
print("desbordes:", desbordes if desbordes else "ninguno")
(SALIDA / "tramos.json").write_text(
    json.dumps([{"id": i, "inicio": ini, "dur": d} for i, ini, d in tramos], indent=1),
    encoding="utf-8")
