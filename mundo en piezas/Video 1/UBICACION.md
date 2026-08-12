# Dónde está el vídeo montado

El `.mp4` **ya no está en el repositorio**. Pesa 46,7 MB y no hace falta para
rehacer nada: con las imágenes, la voz y el guion se vuelve a montar en minutos.

## Ruta en tu PC

```
C:\Users\oriol\You\mundo en piezas\Video 1\video.mp4
```

Está en esta misma carpeta, junto a este fichero. Git lo ignora, pero el fichero
existe en disco.

Para abrir la carpeta directamente:

```bash
explorer "C:\Users\oriol\You\mundo en piezas\Video 1"
```

## Qué sí está versionado

| | |
|---|---|
| `imagenes/` | Las 145, nombradas por su marca de tiempo, con `index.txt` |
| `audio/voz.mp3` | La voz sola, ya calibrada y masterizada |
| `guion.md` | El texto con sus marcas de tiempo |
| `produccion/` | Ficha, escenas y los prompts exactos |
| `miniaturas/` | Las candidatas, con la elegida marcada |
| `publicacion/` | Título y descripción |

## Aviso

**Haz copia del `.mp4` fuera de esta carpeta.** Al no estar en Git, si borras la
carpeta o cambias de máquina, el montaje se pierde y hay que rehacerlo.

## Nota sobre el histórico

Este vídeo sí llegó a subirse a GitHub antes de tomar esta decisión, así que sus
46,7 MB siguen dentro del histórico de Git aunque el fichero ya no se rastree.
Quitarlo de verdad exigiría reescribir el histórico, cosa que no se ha hecho
porque hay más de una sesión trabajando sobre este repositorio.
