# -*- coding: utf-8 -*-
"""Exporta las 140 escenas del video 4 a JSON."""
import importlib.util
import json
from pathlib import Path

RUTA = Path(r"C:\Users\oriol\You\mundo en piezas\Video 4\produccion\escenas.py")
spec = importlib.util.spec_from_file_location("e", str(RUTA))
e = importlib.util.module_from_spec(spec)
spec.loader.exec_module(e)

SOBRIO = (
    "Colorful digital illustration with pixel art influence. Crisp clean pixel "
    "rendering, saturated but restrained colors, rich detailed background. "
    "Serious documentary mood, not cheerful, no whimsy, neutral expressions, "
    "nobody smiling. Clean dark outlines, soft shading inside flat color areas. "
    "Realistic muted palette: concrete grey, sea blue, dry earth, white "
    "buildings, overcast sky. Any people are North African with brown "
    "Mediterranean skin tones and dark hair, in ordinary everyday clothes, drawn "
    "small and anonymous, no detailed faces. Everything readable and well "
    "composed, generous margins, nothing cropped. Absolutely no text, no "
    "letters, no words, no numbers anywhere in the image. Scene: "
)

datos = [{"id": i, "prompt": SOBRIO + escena} for i, _t, escena in e.GUION]
salida = Path(__file__).parent / "plan_v4.json"
salida.write_text(json.dumps(datos, ensure_ascii=False, indent=1), encoding="utf-8")
print(f"{len(datos)} escenas -> {salida}")
