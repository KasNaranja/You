#!/usr/bin/env python3
"""Saca el título y el fotograma de un Short de YouTube a partir de su enlace.

No usa yt-dlp a propósito. YouTube bloquea la descarga de vídeo desde IPs de
centros de datos, pero estas dos vías siguen abiertas:

  · el título, por oEmbed (`youtube.com/oembed`)
  · el fotograma, por la miniatura vertical (`i.ytimg.com/vi/<id>/oardefault.jpg`)

Y esa miniatura no es un recorte: en los Shorts es el primer fotograma completo
a 1080×1920, con el texto superpuesto legible. Que es justo lo que hace falta.

    python3 herramientas/short-fuente.py https://www.youtube.com/shorts/XXXX
"""
from __future__ import annotations

import argparse
import datetime
import json
import re
import sys
import urllib.parse
import urllib.request
from pathlib import Path

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/131.0"}

# Candidatas a mirar. No hay un orden fiable: en unos vídeos la vertical
# completa está en `oardefault` y en otros esa sale diminuta —357x638— y la
# buena es `oar2`. Así que se piden todas y se elige por tamaño real.
MINIATURAS = ["oardefault", "oar2", "maxresdefault", "hq720", "sddefault",
              "hqdefault"]


def id_de(url: str) -> str:
    """Acepta las formas /shorts/, watch?v= y youtu.be/, con o sin parámetros."""
    for patron in (r"/shorts/([A-Za-z0-9_-]{11})",
                   r"[?&]v=([A-Za-z0-9_-]{11})",
                   r"youtu\.be/([A-Za-z0-9_-]{11})",
                   r"^([A-Za-z0-9_-]{11})$"):
        m = re.search(patron, url)
        if m:
            return m.group(1)
    sys.exit(f"No se ha podido extraer el identificador del vídeo de: {url}")


def bajar(url: str, timeout: int = 45) -> bytes:
    return urllib.request.urlopen(
        urllib.request.Request(url, headers=UA), timeout=timeout).read()


# Registro de shorts ya trabajados. Vive en el repo para que sobreviva a la
# sesión: la memoria del chat se pierde, el fichero no.
REGISTRO = Path(__file__).resolve().parent / "skills" / "portada-short" / "ya-hechos.json"


def cargar_registro() -> dict:
    try:
        return json.loads(REGISTRO.read_text(encoding="utf8"))
    except Exception:
        return {}


def apuntar(vid: str, titulo: str) -> dict | None:
    """Devuelve la entrada previa si el vídeo ya se trabajó; si no, lo apunta."""
    reg = cargar_registro()
    previo = reg.get(vid)
    if previo is None:
        reg[vid] = {"titulo": titulo,
                    "fecha": datetime.date.today().isoformat()}
        REGISTRO.parent.mkdir(parents=True, exist_ok=True)
        REGISTRO.write_text(json.dumps(reg, ensure_ascii=False, indent=1),
                            encoding="utf8")
    return previo


CATALOGOS = ["analisis/scroll-spheres/shorts-scrollspheres-catalogo.json"]


def del_catalogo(vid: str) -> str:
    """Título guardado en un catálogo del repositorio, si lo hay.

    oEmbed devuelve 401 en los vídeos que tienen el incrustado desactivado
    —pasa con los que llevan música con derechos— y entonces no da el título.
    Como el catálogo del canal ya lo tiene, se tira de ahí antes de rendirse.
    """
    raiz = Path(__file__).resolve().parent.parent
    for rel in CATALOGOS:
        ruta = raiz / rel
        if not ruta.exists():
            continue
        try:
            for v in json.loads(ruta.read_text(encoding="utf8")):
                if v.get("id") == vid:
                    return v.get("titulo", "")
        except Exception:
            continue
    return ""


def titulo_y_canal(vid: str) -> tuple[str, str]:
    destino = ("https://www.youtube.com/oembed?url="
               + urllib.parse.quote(f"https://www.youtube.com/watch?v={vid}", safe="")
               + "&format=json")
    try:
        d = json.loads(bajar(destino))
        return d.get("title", ""), d.get("author_name", "")
    except Exception as e:
        respaldo = del_catalogo(vid)
        if respaldo:
            print(f"! oEmbed ha fallado ({e}); título sacado del catálogo.",
                  file=sys.stderr)
            return respaldo, ""
        print(f"! No se ha podido leer el título: {e}", file=sys.stderr)
        return "", ""


def medidas(datos: bytes) -> tuple[int, int]:
    try:
        from PIL import Image
        import io
        return Image.open(io.BytesIO(datos)).size
    except Exception:
        return (0, 0)


def fotograma(vid: str, destino: Path) -> tuple[str, tuple[int, int]]:
    """Guarda la miniatura más grande. Devuelve cuál se ha usado y su tamaño.

    Se comparan todas porque el nombre no dice nada del tamaño: hay vídeos en
    los que `oardefault` es la vertical a 1080x1920 y otros en los que esa
    misma sale a 357x638 y la buena está en `oar2`.
    """
    mejor = (0, "", b"", (0, 0))
    for nombre in MINIATURAS:
        try:
            datos = bajar(f"https://i.ytimg.com/vi/{vid}/{nombre}.jpg")
        except Exception:
            continue
        # Una miniatura ausente devuelve una imagen gris diminuta, no un 404.
        if len(datos) <= 8000:
            continue
        w, h = medidas(datos)
        área = w * h or len(datos)      # sin PIL, el peso sirve de sucedáneo
        if área > mejor[0]:
            mejor = (área, nombre, datos, (w, h))
    if not mejor[1]:
        sys.exit("No se ha podido descargar ninguna miniatura del vídeo.")
    destino.write_bytes(mejor[2])
    return mejor[1], mejor[3]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("url")
    ap.add_argument("--salida", default=".", help="carpeta donde dejar el fotograma")
    args = ap.parse_args()

    vid = id_de(args.url)
    carpeta = Path(args.salida)
    carpeta.mkdir(parents=True, exist_ok=True)
    destino = carpeta / f"{vid}.jpg"

    cual, (w, h) = fotograma(vid, destino)
    titulo, canal = titulo_y_canal(vid)

    print(f"id       : {vid}")
    print(f"título   : {titulo}")
    print(f"canal    : {canal}")
    print(f"fotograma: {destino}  ({cual}, {w or '?'}x{h or '?'})")
    if h and h < w:
        print("! El fotograma es apaisado: el vídeo puede no ser un Short.")
    elif h and h < 1200:
        print("! Fotograma pequeño: el texto en pantalla puede costar de leer.")

    previo = apuntar(vid, titulo)
    if previo:
        print(f"\n¡OJO! Este short YA SE TRABAJÓ el {previo.get('fecha', '?')}:")
        print(f"      «{previo.get('titulo', '')}»")
        print("      Avisar al usuario antes de rehacerlo.")


if __name__ == "__main__":
    main()
