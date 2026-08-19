# Dónde están los ficheros del vídeo 5

**Estado:** solo el gancho está montado. El cuerpo del vídeo (146 marcas) aún no
tiene imágenes.

## El gancho

```
C:\Users\oriol\You\mundo en piezas\Video 5\gancho.mp4
```

25,48 s, 1920×1080, 30 fps, 22 MB. Git lo ignora —es reproducible desde los
clips y la voz— pero el fichero existe en disco.

```
explorer "C:\Users\oriol\You\mundo en piezas\Video 5"
```

## Qué sí está versionado

| | |
|---|---|
| `clips/gancho-1..4.mp4` | Los cuatro clips crudos de Veo. **No son reproducibles** y cuestan 8 créditos cada uno |
| `prueba-literal/` | Las imágenes semilla, incluida `4b-competencia.png`, que es la que se usó |
| `audio/gancho.mp3` | La voz del gancho, ya masterizada y cortada en 25,55 s |
| `guion.md` | Las 146 marcas |
| `produccion/gancho.md` | Tiempos, silencios y qué hace cada clip |
| `produccion/biblia-visual.md` | Los objetos recurrentes, palabra por palabra |

## Cómo se remonta el gancho

Desde `clips/` y `audio/gancho.mp3`, sin gastar créditos. Cada clip se recorta a
su duración de uso —8,00 / 2,70 / 8,00 / 6,85— y el cuarto lleva
`eq=saturation=0.66` para que su turquesa no desentone con los otros tres.

Los valores exactos y el porqué están en `produccion/gancho.md`.

## Aviso

**Haz copia de `clips/` fuera de esta carpeta.** Están en Git, pero si algún día
se limpia el histórico por peso, son lo único de este vídeo que no se puede
volver a generar igual: Veo no es determinista.
