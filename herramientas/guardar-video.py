#!/usr/bin/env python3
"""Guarda un vídeo de YouTube (u otra plataforma) en Transcriptions/.

Crea una carpeta numerada por vídeo con la estructura:

    Transcriptions/<N>/
        audio/       audio extraído en mp3 mono 16 kHz
        frames/      fotogramas por cambio de escena + index.txt con sus tiempos
        transcript/  subtítulos en .vtt y en texto plano con marcas de tiempo
        metadata.json
        README.md

Uso:
    python3 herramientas/guardar-video.py <url> [--detail balanced] [--push]

Requiere `yt-dlp` y `ffmpeg` en el PATH. Pensado para ejecutarse en una máquina
con IP doméstica: YouTube bloquea las IPs de centros de datos.

Opcionalmente, `pip install faster-whisper` habilita la transcripción en local
de los vídeos que no traigan subtítulos. Es gratis, sin claves ni cuotas, y el
audio no sale de la máquina. Sin ese paquete el script sigue funcionando: esos
vídeos se archivan con audio y fotogramas, pero sin transcripción.
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
DESTINO = RAIZ / "Transcriptions"

# Tope de fotogramas por nivel de detalle.
DETALLE = {"efficient": 50, "balanced": 100, "token-burner": 0}  # 0 = sin tope

ETIQUETA_FUENTE = {
    "subtitulos": "sí — subtítulos del vídeo",
    "whisper-local": "sí — Whisper en local",
    "ninguna": "no — solo audio",
}


def comprobar_dependencias() -> None:
    faltan = [b for b in ("yt-dlp", "ffmpeg") if shutil.which(b) is None]
    if faltan:
        sys.exit(
            f"Faltan dependencias: {', '.join(faltan)}.\n"
            "En Windows: winget install yt-dlp.yt-dlp Gyan.FFmpeg"
        )


def flag_fps() -> list[str]:
    """`-vsync` se eliminó en ffmpeg 8; a partir de ahí es `-fps_mode`."""
    try:
        salida = subprocess.run(
            ["ffmpeg", "-version"], capture_output=True, text=True, check=False
        ).stdout
        m = re.search(r"ffmpeg version n?(\d+)", salida)
        mayor = int(m.group(1)) if m else 0
    except OSError:
        mayor = 0
    return ["-fps_mode", "vfr"] if mayor >= 8 else ["-vsync", "vfr"]


def siguiente_numero() -> int:
    DESTINO.mkdir(parents=True, exist_ok=True)
    usados = [int(p.name) for p in DESTINO.iterdir() if p.is_dir() and p.name.isdigit()]
    return max(usados, default=0) + 1


def descargar(url: str, trabajo: Path, alto_max: int) -> dict:
    """Baja vídeo, subtítulos y metadatos. Devuelve el info.json como dict.

    Se limita la resolución de origen porque los fotogramas se escalan luego a
    1280 px de ancho: bajar 4K no mejora el resultado y multiplica por cuatro el
    trabajo de decodificación. Un vídeo de 28 min en 4K50 son 780 MB y decenas
    de minutos de ffmpeg para producir exactamente los mismos JPEG que 1080p.
    """
    plantilla = str(trabajo / "video.%(ext)s")
    cmd = [
        "yt-dlp",
        "--no-playlist",
        "-S", f"res:{alto_max}",
        "--write-info-json",
        "--write-subs",
        "--write-auto-subs",
        "--sub-langs", "es.*,en.*",
        "--sub-format", "vtt",
        "--convert-subs", "vtt",
        "--merge-output-format", "mp4",
        # Una pista de subtítulos que falle (típicamente un 429 de YouTube en un
        # idioma secundario) no debe abortar la descarga del vídeo.
        "--ignore-errors",
        "-o", plantilla,
        "--",
        url,
    ]
    codigo = subprocess.run(cmd).returncode
    hay_video = any(trabajo.glob(f"video*{e}") for e in (".mp4", ".mkv", ".webm", ".mov"))
    if codigo != 0 and not hay_video:
        sys.exit("yt-dlp falló. Si es un 429 o pide iniciar sesión, reintenta más tarde.")

    info_path = trabajo / "video.info.json"
    if not info_path.exists():
        return {"webpage_url": url}
    return json.loads(info_path.read_text(encoding="utf-8"))


def localizar_video(trabajo: Path) -> Path:
    for ext in (".mp4", ".mkv", ".webm", ".mov"):
        for c in trabajo.glob(f"video*{ext}"):
            return c
    sys.exit("No se encontró el fichero de vídeo descargado.")


def extraer_audio(video: Path, destino: Path) -> None:
    destino.mkdir(parents=True, exist_ok=True)
    cmd = [
        "ffmpeg", "-y", "-i", str(video),
        "-vn", "-ac", "1", "-ar", "16000", "-b:a", "64k",
        str(destino / "audio.mp3"),
    ]
    subprocess.run(cmd, capture_output=True)


def extraer_frames(
    video: Path, destino: Path, tope: int, duracion: float | None, cada: float | None
) -> list[tuple[str, float]]:
    """Fotogramas por cambio de escena, con cobertura temporal garantizada.

    La detección de escenas por sí sola agrupa los fotogramas donde hay cortes y
    deja el resto a oscuras: en un vídeo de 28 min de charla a cámara, 9 de 11
    fotogramas caían dentro del mismo minuto y 23 minutos se quedaban sin una
    sola imagen. Por eso, además de los cortes, se fuerza un fotograma cada
    `intervalo` segundos — `prev_selected_t` es el segundo del último fotograma
    seleccionado, así que la condición cubre cualquier hueco demasiado largo.
    """
    destino.mkdir(parents=True, exist_ok=True)
    patron = str(destino / "frame_%03d.jpg")

    # Con `cada` (5 s por defecto) el intervalo es fijo y el tope se levanta: si
    # pides un fotograma cada N segundos, el tope no debe recortarte el final
    # del vídeo. En disco salen 50-90 KB por imagen segun lo movido que sea, asi
    # que la densidad es barata; lo caro es leerlas luego todas de golpe, y para
    # eso esta `index.txt`, que permite ir solo a los tramos que interesen.
    # Con `--cada 0` se vuelve al intervalo automatico por duracion.
    if cada:
        intervalo = float(cada)
        tope = 0
    else:
        # Si no, se calcula para que el muestreo uniforme ocupe ~el 80% del
        # tope y quede sitio a los cambios de escena. El suelo de 5 s evita
        # que un vídeo corto se llene de fotogramas casi idénticos.
        efectivo = tope or 100
        intervalo = max(duracion / (efectivo * 0.8), 5.0) if duracion else 30.0

    vf = (
        f"select='eq(n\\,0)+gt(scene\\,0.3)+gte(t-prev_selected_t\\,{intervalo:.2f})'"
        ",scale=1280:-2,showinfo"
    )
    cmd = ["ffmpeg", "-y", "-i", str(video), "-vf", vf, *flag_fps()]
    if tope:
        cmd += ["-frames:v", str(tope)]
    cmd += ["-q:v", "4", patron]

    res = subprocess.run(cmd, capture_output=True, text=True, errors="replace")
    tiempos = [float(t) for t in re.findall(r"pts_time:([\d.]+)", res.stderr or "")]

    ficheros = sorted(p.name for p in destino.glob("frame_*.jpg"))

    # Si la detección de escenas apenas encuentra nada (vídeo estático), se
    # recurre a un muestreo uniforme para no quedarse sin imágenes.
    if len(ficheros) < 5:
        for p in destino.glob("frame_*.jpg"):
            p.unlink()
        cmd = [
            "ffmpeg", "-y", "-i", str(video),
            "-vf", "fps=1/3,scale=1280:-2,showinfo",
            *flag_fps(), "-frames:v", str(tope or 100), "-q:v", "4", patron,
        ]
        res = subprocess.run(cmd, capture_output=True, text=True, errors="replace")
        tiempos = [float(t) for t in re.findall(r"pts_time:([\d.]+)", res.stderr or "")]
        ficheros = sorted(p.name for p in destino.glob("frame_*.jpg"))

    pares = list(zip(ficheros, tiempos + [0.0] * len(ficheros)))
    indice = "\n".join(f"{f}\t{seg:.2f}s" for f, seg in pares)
    (destino / "index.txt").write_text(indice + "\n", encoding="utf-8")
    return pares


def vtt_a_texto(vtt: str) -> str:
    """Convierte un .vtt en texto con marcas de tiempo, sin líneas repetidas."""
    lineas: list[str] = []
    sello = ""
    visto = ""
    for linea in vtt.splitlines():
        linea = linea.strip()
        if not linea or linea.startswith(("WEBVTT", "Kind:", "Language:", "NOTE")):
            continue
        if "-->" in linea:
            sello = linea.split("-->")[0].strip().split(".")[0]
            continue
        texto = re.sub(r"<[^>]+>", "", linea).strip()
        # Los subtítulos automáticos repiten la línea anterior en cada bloque.
        if not texto or texto == visto:
            continue
        visto = texto
        lineas.append(f"[{sello}] {texto}")
    return "\n".join(lineas)


def transcribir_local(audio: Path, destino: Path, modelo: str) -> bool:
    """Transcribe el audio con Whisper en local (faster-whisper).

    Sin claves de API, sin red y sin cuotas: el audio no sale de la máquina.
    El modelo se descarga una sola vez y queda en la caché de Hugging Face.
    """
    if not audio.exists():
        return False
    try:
        from faster_whisper import WhisperModel
    except ImportError:
        print("  faster-whisper no está instalado: pip install faster-whisper")
        return False

    print(f"→ Sin subtítulos: transcribiendo en local con Whisper «{modelo}»…")
    lineas: list[str] = []
    try:
        wm = WhisperModel(modelo, device="cpu", compute_type="int8")
        segmentos, info = wm.transcribe(str(audio), vad_filter=True)
        for s in segmentos:
            texto = s.text.strip()
            if not texto:
                continue
            h, resto = divmod(int(s.start), 3600)
            m, seg = divmod(resto, 60)
            lineas.append(f"[{h:02d}:{m:02d}:{seg:02d}] {texto}")
    except Exception as e:  # cualquier fallo degrada a "sin transcripción"
        print(f"  Whisper local falló: {e}")
        return False

    if not lineas:
        return False
    destino.mkdir(parents=True, exist_ok=True)
    cabecera = f"# Transcrito en local con Whisper «{modelo}» (idioma: {info.language})"
    (destino / "transcript.txt").write_text(
        cabecera + "\n" + "\n".join(lineas) + "\n", encoding="utf-8"
    )
    return True


def guardar_transcripcion(trabajo: Path, destino: Path, audio: Path, modelo: str) -> str:
    """Devuelve la fuente: `subtitulos`, `whisper-local` o `ninguna`."""
    destino.mkdir(parents=True, exist_ok=True)
    vtts = sorted(trabajo.glob("video*.vtt"))
    if vtts:
        for v in vtts:
            shutil.copy2(v, destino / v.name)
        texto = vtt_a_texto(vtts[0].read_text(encoding="utf-8", errors="replace"))
        (destino / "transcript.txt").write_text(texto + "\n", encoding="utf-8")
        return "subtitulos"

    if modelo != "no" and transcribir_local(audio, destino, modelo):
        return "whisper-local"

    (destino / "SIN-SUBTITULOS.txt").write_text(
        "Este vídeo no tenía subtítulos y no se pudo transcribir en local.\n"
        "El audio está en ../audio/audio.mp3 para transcribirlo aparte.\n",
        encoding="utf-8",
    )
    return "ninguna"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("url")
    ap.add_argument("--detail", choices=list(DETALLE), default="balanced")
    ap.add_argument(
        "--modelo",
        default="small",
        help="modelo de Whisper local para vídeos sin subtítulos "
             "(tiny, base, small, medium, large-v3; «no» lo desactiva)",
    )
    ap.add_argument(
        "--cada",
        type=float,
        default=5.0,
        metavar="SEGUNDOS",
        help="un fotograma cada N segundos, además de los cambios de escena "
             "(5 por defecto). Levanta el tope de --detail. Con 0 vuelve al "
             "intervalo automático calculado a partir de la duración",
    )
    ap.add_argument(
        "--alto-max",
        type=int,
        default=1080,
        help="tope de resolución de origen en px de alto (por defecto 1080). "
             "Los fotogramas se escalan a 1280 de ancho, así que bajar más "
             "resolución no mejora nada y encarece mucho la decodificación",
    )
    ap.add_argument("--push", action="store_true", help="commitea y sube a main")
    args = ap.parse_args()

    comprobar_dependencias()

    n = siguiente_numero()
    carpeta = DESTINO / str(n)
    trabajo = carpeta / ".trabajo"
    trabajo.mkdir(parents=True, exist_ok=True)

    print(f"→ Guardando en Transcriptions/{n}/")

    info = descargar(args.url, trabajo, args.alto_max)
    video = localizar_video(trabajo)

    extraer_audio(video, carpeta / "audio")
    frames = extraer_frames(
        video, carpeta / "frames", DETALLE[args.detail], info.get("duration"), args.cada
    )
    fuente = guardar_transcripcion(
        trabajo, carpeta / "transcript", carpeta / "audio" / "audio.mp3", args.modelo
    )

    meta = {
        "n": n,
        "url": info.get("webpage_url", args.url),
        "titulo": info.get("title", "(desconocido)"),
        "canal": info.get("uploader"),
        "duracion_s": info.get("duration"),
        "fecha_subida": info.get("upload_date"),
        "guardado": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        "detalle": args.detail,
        "fotogramas": len(frames),
        "con_subtitulos": fuente == "subtitulos",
        "transcripcion": fuente,
    }
    (carpeta / "metadata.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    dur = meta["duracion_s"]
    filas = [
        f"# {n}. {meta['titulo']}",
        "",
        f"- **URL:** {meta['url']}",
        f"- **Canal:** {meta['canal'] or '—'}",
    ]
    if dur:
        filas.append(f"- **Duración:** {dur}s")
    filas += [
        f"- **Guardado:** {meta['guardado']}",
        f"- **Fotogramas:** {len(frames)} ({args.detail})",
        f"- **Transcripción:** {ETIQUETA_FUENTE[fuente]}",
        "",
        "`frames/index.txt` relaciona cada imagen con su segundo del vídeo.",
    ]
    (carpeta / "README.md").write_text("\n".join(filas) + "\n", encoding="utf-8")

    shutil.rmtree(trabajo, ignore_errors=True)

    print(f"✓ {len(frames)} fotogramas · transcripción: {ETIQUETA_FUENTE[fuente]}")
    print(f"  {carpeta}")

    if args.push:
        subprocess.run(["git", "-C", str(RAIZ), "add", "Transcriptions"], check=False)
        subprocess.run(
            ["git", "-C", str(RAIZ), "commit", "-m",
             f"vídeo {n}: {meta['titulo']}"],
            check=False,
        )
        subprocess.run(["git", "-C", str(RAIZ), "push", "origin", "HEAD:main"], check=False)


if __name__ == "__main__":
    main()
