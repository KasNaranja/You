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
import json
import re
import sys
import urllib.parse
import urllib.request
from pathlib import Path

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/131.0"}

# De más a menos deseable: la primera es la vertical completa del Short.
MINIATURAS = ["oardefault", "maxresdefault", "hq720", "sddefault", "hqdefault"]


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


def fotograma(vid: str, destino: Path) -> str:
    """Guarda la mejor miniatura disponible. Devuelve cuál se ha usado."""
    for nombre in MINIATURAS:
        try:
            datos = bajar(f"https://i.ytimg.com/vi/{vid}/{nombre}.jpg")
        except Exception:
            continue
        # Una miniatura ausente devuelve una imagen gris diminuta, no un 404.
        if len(datos) > 8000:
            destino.write_bytes(datos)
            return nombre
    sys.exit("No se ha podido descargar ninguna miniatura del vídeo.")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("url")
    ap.add_argument("--salida", default=".", help="carpeta donde dejar el fotograma")
    args = ap.parse_args()

    vid = id_de(args.url)
    carpeta = Path(args.salida)
    carpeta.mkdir(parents=True, exist_ok=True)
    destino = carpeta / f"{vid}.jpg"

    cual = fotograma(vid, destino)
    titulo, canal = titulo_y_canal(vid)

    try:
        from PIL import Image
        medidas = "x".join(map(str, Image.open(destino).size))
    except Exception:
        medidas = "?"

    print(f"id       : {vid}")
    print(f"título   : {titulo}")
    print(f"canal    : {canal}")
    print(f"fotograma: {destino}  ({cual}, {medidas})")
    if cual != "oardefault":
        print("! No había miniatura vertical: puede que el texto salga recortado.")


if __name__ == "__main__":
    main()
