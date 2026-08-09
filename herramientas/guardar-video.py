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


def descargar(url: str, trabajo: Path) -> dict:
    """Baja vídeo, subtítulos y metadatos. Devuelve el info.json como dict."""
    plantilla = str(trabajo / "video.%(ext)s")
    cmd = [
        "yt-dlp",
        "--no-playlist",
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


def extraer_frames(video: Path, destino: Path, tope: int) -> list[tuple[str, float]]:
    """Fotogramas por cambio de escena. Devuelve [(fichero, segundo), ...]."""
    destino.mkdir(parents=True, exist_ok=True)
    patron = str(destino / "frame_%03d.jpg")
    vf = "select='eq(n\\,0)+gt(scene\\,0.3)',scale=1280:-2,showinfo"
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


def guardar_transcripcion(trabajo: Path, destino: Path) -> bool:
    destino.mkdir(parents=True, exist_ok=True)
    vtts = sorted(trabajo.glob("video*.vtt"))
    if not vtts:
        (destino / "SIN-SUBTITULOS.txt").write_text(
            "Este vídeo no tenía subtítulos disponibles.\n"
            "El audio está en ../audio/audio.mp3 para transcribirlo aparte.\n",
            encoding="utf-8",
        )
        return False
    for v in vtts:
        shutil.copy2(v, destino / v.name)
    principal = vtts[0]
    texto = vtt_a_texto(principal.read_text(encoding="utf-8", errors="replace"))
    (destino / "transcript.txt").write_text(texto + "\n", encoding="utf-8")
    return True


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("url")
    ap.add_argument("--detail", choices=list(DETALLE), default="balanced")
    ap.add_argument("--push", action="store_true", help="commitea y sube a main")
    args = ap.parse_args()

    comprobar_dependencias()

    n = siguiente_numero()
    carpeta = DESTINO / str(n)
    trabajo = carpeta / ".trabajo"
    trabajo.mkdir(parents=True, exist_ok=True)

    print(f"→ Guardando en Transcriptions/{n}/")

    info = descargar(args.url, trabajo)
    video = localizar_video(trabajo)

    extraer_audio(video, carpeta / "audio")
    frames = extraer_frames(video, carpeta / "frames", DETALLE[args.detail])
    hay_subs = guardar_transcripcion(trabajo, carpeta / "transcript")

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
        "con_subtitulos": hay_subs,
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
        f"- **Subtítulos:** {'sí' if hay_subs else 'no — solo audio'}",
        "",
        "`frames/index.txt` relaciona cada imagen con su segundo del vídeo.",
    ]
    (carpeta / "README.md").write_text("\n".join(filas) + "\n", encoding="utf-8")

    shutil.rmtree(trabajo, ignore_errors=True)

    print(f"✓ {len(frames)} fotogramas · subtítulos: {'sí' if hay_subs else 'no'}")
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
