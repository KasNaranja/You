# Dónde está el vídeo montado

El `.mp4` **no está en el repositorio**. Pesa unos 190 MB y no hace falta para
rehacer nada: con las imágenes, la voz y el guion se vuelve a montar en minutos.

## Ruta en tu PC

```
C:\Users\oriol\You\mundo en piezas\Video 2\video.mp4
```

Está en esta misma carpeta, junto a este fichero. Git lo ignora, pero el fichero
existe en disco.

Para abrir la carpeta directamente:

```bash
explorer "C:\Users\oriol\You\mundo en piezas\Video 2"
```

## Qué sí está versionado

| | |
|---|---|
| `imagenes/` | Las 142, nombradas por su marca de tiempo |
| `audio/voz.mp3` | La voz sola, ya calibrada y masterizada |
| `guion.md` | El texto con sus marcas de tiempo |
| `produccion/escenas.py` | Qué se dibuja en cada una y con qué estilo |
| `miniaturas/` | Las cuatro candidatas |
| `publicacion/` | Título y descripción |

Con eso se reconstruye el vídeo entero sin volver a gastar un solo crédito.

## Cómo volver a montarlo

El montador está en `produccion/`. Necesita `ffmpeg` en el PATH y las imágenes
y la voz de esta carpeta. Tarda unos diez minutos, casi todo codificación.

## Aviso

**Haz copia del `.mp4` fuera de esta carpeta.** Al no estar en Git, si borras la
carpeta o cambias de máquina, el montaje se pierde y hay que rehacerlo.
