# Dónde están los ficheros del vídeo 5

**Estado:** vídeo completo montado — 5:52, 196 MB.

## El vídeo completo

```
C:\Users\oriol\You\mundo en piezas\Video 5\video.mp4
```

5:52 (351,5 s), 1920×1080, 30 fps, H.264 High, AAC 48 kHz estéreo. Se remonta
gratis con `herramientas/montar-video-efectos.py` desde las imágenes, los
tramos y la voz.

## El gancho suelto

```
C:\Users\oriol\You\mundo en piezas\Video 5\gancho.mp4
```

27,80 s, 1920×1080, 30 fps, 22 MB. Git lo ignora —es reproducible desde los
clips y la voz— pero el fichero existe en disco.

```
explorer "C:\Users\oriol\You\mundo en piezas\Video 5"
```

## Qué sí está versionado

| | |
|---|---|
| `clips/gancho-1..4.mp4` | Los cuatro clips crudos de Veo. **No son reproducibles** y cuestan 8 créditos cada uno |
| `prueba-literal/` | Las imágenes semilla, incluida `4b-competencia.png`, que es la que se usó |
| `audio/gancho.mp3` | La voz del gancho, con la voz clonada del autor, masterizada |
| `guion.md` | Las 146 marcas |
| `produccion/gancho.md` | Tiempos, silencios y qué hace cada clip |
| `produccion/biblia-visual.md` | Los objetos recurrentes, palabra por palabra |

## Cómo se remonta el gancho

Desde `clips/` y `audio/gancho.mp3`, sin gastar créditos. Cada clip se recorta a
su duración de uso —9,05 / 2,80 / 9,03 / 6,94, los tramos 1 y 3 ralentizados un 13%— y el cuarto lleva
`eq=saturation=0.66` para que su turquesa no desentone con los otros tres.

Los valores exactos y el porqué están en `produccion/gancho.md`.

## Aviso

**Haz copia de `clips/` fuera de esta carpeta.** Están en Git, pero si algún día
se limpia el histórico por peso, son lo único de este vídeo que no se puede
volver a generar igual: Veo no es determinista.
