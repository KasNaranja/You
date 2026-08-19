# -*- coding: utf-8 -*-
"""Genera la voz de un vídeo con ElevenLabs, en una sola toma continua.

    python generar-voz-eleven.py "<escenas.py|guion.md>" "<carpeta salida>" [--voz ID] [--seco]

La diferencia con `generar-voz.py` no es el motor, es el método.

**El método viejo (edge-tts):** una locución por marca de tiempo, calibrada en
velocidad hasta que cupiera en su hueco, y silencio de relleno hasta la
siguiente. 141 trozos pegados. De ahí salían tres problemas:

- deriva por concatenación (~60 ms por unión en MP3),
- micro-silencios entre todas las frases, que es lo que sonaba a robot,
- líneas aceleradas al 30% o al 48% para que cupieran, que se notan.

**El método nuevo:** se manda el guion entero de un tirón y ElevenLabs devuelve
el audio **y las marcas de tiempo carácter a carácter**. De ahí sale el segundo
exacto en que arranca cada línea, y son **las imágenes las que se colocan sobre
el audio**, no el audio el que se mete a la fuerza en huecos de 3 segundos.

Las marcas del guion pasan a ser el orden y el reparto aproximado, no una
camisa de fuerza. El resultado es una narración con prosodia continua: las
frases encadenan como las encadena una persona.

**El troceado** existe solo porque la API acepta unos 5.000 caracteres por
petición, y el guion son ~5.900. Se parte entre líneas y se cose con
`previous_request_ids`, que le dice al modelo que continúe la entonación de lo
anterior en vez de empezar de cero. La unión no se oye.

Salidas:

    voz.wav      la narración masterizada al nivel del canal
    tramos.json  el segundo real en que arranca cada línea  <-- lo que consume el montador
    crudo.mp3    lo que devolvió la API, sin tocar
"""
import base64
import importlib.util
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

API = "https://api.elevenlabs.io/v1"
MODELO = "eleven_multilingual_v2"
LIMITE = 4800           # margen bajo el tope de la API
VOZ_POR_DEFECTO = "hjCyEOhV6mCX4KFzbMDQ"  # "You", el clon del propio autor
CADENA = (
    "highpass=f=85,"
    "equalizer=f=250:t=q:w=1.2:g=-2.5,"
    "equalizer=f=3200:t=q:w=1.5:g=2.5,"
    "acompressor=threshold=-18dB:ratio=3:attack=8:release=120,"
    "loudnorm=I=-16:TP=-1.5:LRA=11"
)


def clave():
    k = os.environ.get("ELEVENLABS_API_KEY")
    if k:
        return k.strip()
    f = Path.home() / ".config" / "elevenlabs" / ".env"
    if f.exists():
        for linea in f.read_text(encoding="utf-8").splitlines():
            if linea.strip().startswith("ELEVENLABS_API_KEY"):
                return linea.split("=", 1)[1].strip().strip('"').strip("'")
    sys.exit(
        "Falta la clave. Ponla en una de estas dos:\n"
        "  variable de entorno  ELEVENLABS_API_KEY\n"
        f"  fichero              {f}   ->  ELEVENLABS_API_KEY=sk_...")


def pedir(ruta, cuerpo=None, clave_api=None):
    datos = json.dumps(cuerpo).encode() if cuerpo is not None else None
    req = urllib.request.Request(
        API + ruta, data=datos, method="POST" if datos else "GET",
        headers={"xi-api-key": clave_api, "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=300) as r:
            return json.loads(r.read()), dict(r.headers)
    except urllib.error.HTTPError as ex:
        sys.exit(f"API {ex.code}: {ex.read().decode('utf-8', 'replace')[:400]}")


def segundos(ident):
    m, s = ident.split("-") if "-" in ident else ident.split(":")
    return int(m) * 60 + int(s)


def leer_lineas(p):
    """Devuelve [(ident, texto)] desde un escenas.py o desde un guion.md."""
    if p.suffix == ".py":
        spec = importlib.util.spec_from_file_location("e", str(p))
        e = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(e)
        return [(g[0], g[1]) for g in e.GUION]
    lineas, dentro = [], False
    for linea in p.read_text(encoding="utf-8").splitlines():
        if linea.startswith("## Guion"):
            dentro = True
            continue
        if not dentro:
            continue
        m = re.match(r"^(\d+:\d\d)\s+(.+)$", linea.strip())
        if m:
            lineas.append((m.group(1).replace(":", "-"), m.group(2).strip()))
    return lineas


def duracion(p):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "default=nw=1:nk=1", str(p)], capture_output=True, text=True)
    return float(r.stdout.strip())


def trocear(lineas):
    """Parte en bloques de <= LIMITE caracteres, cortando siempre entre líneas."""
    bloques, actual, n = [], [], 0
    for i, (_id, t) in enumerate(lineas):
        if n + len(t) + 1 > LIMITE and actual:
            bloques.append(actual)
            actual, n = [], 0
        actual.append(i)
        n += len(t) + 1
    if actual:
        bloques.append(actual)
    return bloques


def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    escenas, salida = Path(sys.argv[1]), Path(sys.argv[2])
    voz = VOZ_POR_DEFECTO
    if "--voz" in sys.argv:
        voz = sys.argv[sys.argv.index("--voz") + 1]
    if not voz:
        sys.exit("No hay voz elegida. Pásala con --voz <id>.")
    seco = "--seco" in sys.argv

    salida.mkdir(parents=True, exist_ok=True)
    lineas = leer_lineas(escenas)
    if not lineas:
        sys.exit(f"No he encontrado líneas de guion en {escenas}")

    bloques = trocear(lineas)
    total_car = sum(len(t) + 1 for _i, t in lineas)
    print(f"lineas: {len(lineas)}   caracteres: {total_car}   peticiones: {len(bloques)}")
    print(f"coste estimado: {total_car} creditos ({MODELO})")
    if seco:
        for b in bloques:
            print(f"  bloque {lineas[b[0]][0]} -> {lineas[b[-1]][0]}  "
                  f"{sum(len(lineas[i][1]) + 1 for i in b)} car")
        return

    k = clave()
    partes, tramos, previos, desfase = [], [], [], 0.0
    for nb, bloque in enumerate(bloques):
        # Las líneas se unen con un espacio. Se guarda el índice de carácter en
        # que arranca cada una para localizarla luego en la alineación.
        piezas, indices, pos = [], [], 0
        for i in bloque:
            indices.append((lineas[i][0], pos))
            piezas.append(lineas[i][1])
            pos += len(lineas[i][1]) + 1
        texto = " ".join(piezas)

        cuerpo = {"text": texto, "model_id": MODELO,
                  "voice_settings": {"stability": 0.45, "similarity_boost": 0.75,
                                     "style": 0.0, "use_speaker_boost": True}}
        if previos:
            cuerpo["previous_request_ids"] = previos[-3:]
        if nb:
            ant = bloques[nb - 1]
            cuerpo["previous_text"] = " ".join(lineas[i][1] for i in ant)[-400:]
        if nb + 1 < len(bloques):
            sig = bloques[nb + 1]
            cuerpo["next_text"] = " ".join(lineas[i][1] for i in sig)[:400]

        print(f"  peticion {nb + 1}/{len(bloques)}: {len(texto)} car...")
        r, cab = pedir(f"/text-to-speech/{voz}/with-timestamps", cuerpo, k)
        rid = cab.get("request-id") or cab.get("Request-Id")
        if rid:
            previos.append(rid)

        parte = salida / f"parte{nb}.mp3"
        parte.write_bytes(base64.b64decode(r["audio_base64"]))
        partes.append(parte)

        ini = r["alignment"]["character_start_times_seconds"]
        for ident, pos in indices:
            tramos.append({"id": ident,
                           "inicio": round(desfase + ini[min(pos, len(ini) - 1)], 3)})
        desfase += duracion(parte)

    lista = salida / "lista.txt"
    lista.write_text("\n".join(f"file '{p.resolve().as_posix()}'" for p in partes) + "\n",
                     encoding="utf-8")
    crudo = salida / "crudo.mp3"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0",
                    "-i", str(lista), "-c", "copy", str(crudo)], check=True)
    final = salida / "voz.wav"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(crudo),
                    "-af", CADENA, "-ar", "48000", "-ac", "1", str(final)], check=True)

    (salida / "tramos.json").write_text(
        json.dumps(tramos, indent=1, ensure_ascii=False), encoding="utf-8")

    t = duracion(final)
    m, s = divmod(int(round(t)), 60)
    guionado = segundos(lineas[-1][0])
    print(f"\nvoz: {m}:{s:02d} ({t:.2f}s)")
    print(f"ultima linea marcada en {guionado}s, suena en {tramos[-1]['inicio']}s "
          f"({tramos[-1]['inicio'] - guionado:+.1f}s)")
    print(f"tramos.json: {len(tramos)} marcas reales -> ahi se colocan las imagenes")


if __name__ == "__main__":
    main()
