# Dónde está el vídeo montado

El `.mp4` **no está en el repositorio**. Pesa 238 MB y no hace falta para
rehacer nada: con las imágenes, la voz y el guion se remonta en minutos.

## Ruta en tu PC

```
C:\Users\oriol\You\mundo en piezas\Video 4\video.mp4
```

Para abrir la carpeta:

```
explorer "C:\Users\oriol\You\mundo en piezas\Video 4"
```

## Qué sí está versionado

| | |
|---|---|
| `guion.md` | Las 140 marcas de tiempo y la tabla de fuentes |
| `imagenes/` | Las 140, nombradas por su marca |
| `audio/voz.mp3` | La voz sola, calibrada y masterizada |
| `produccion/escenas.py` | Qué se dibuja en cada marca |
| `produccion/plan.json` | Los 140 prompts exactos |
| `miniaturas/` | Las cuatro candidatas |
| `publicacion/` | Título y descripción |

## Cómo remontarlo

Primero la voz, que es gratis:

```
python herramientas\generar-voz.py "mundo en piezas\Video 4\produccion\escenas.py" salida\
```

Y después el montaje:

```
python herramientas\montar-video.py "mundo en piezas\Video 4\produccion\escenas.py" "mundo en piezas\Video 4\imagenes" salida\voz.wav "mundo en piezas\Video 4\video.mp4"
```

## Aviso

**Haz copia del `.mp4` fuera de esta carpeta.** Al no estar en Git, si borras la
carpeta o cambias de máquina, el montaje se pierde y hay que rehacerlo.
