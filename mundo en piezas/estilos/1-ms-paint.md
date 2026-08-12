# Estilo 1 — MS Paint

El usado en el vídeo 1. Dibujo deliberadamente cutre: monigotes de palo,
contorno negro grueso y tembloroso, fondo blanco, colores planos.

**Modelo:** FLUX.2 `pro` · 16:9 · 1k

## Prompt maestro

Va delante de cada escena. Solo cambia lo que sigue a `Scene:`.

```
Extremely simple crude childish drawing made in MS Paint by someone who cannot
draw. Pure plain white background. Thick wobbly uneven shaky black outlines.
Stick figure humans with round heads, thin straight line bodies, simple dot eyes
and very basic facial expressions. Flat solid colors only. No shading, no
gradients, no 3D, no lighting, no textures, no realism, no polish. Amateur,
funny, intentionally bad. Lots of empty white space, simple centered
composition, nothing cropped, generous margin around everything, full bodies
visible. Absolutely no text, no letters, no words, no numbers anywhere in the
image. Scene: <la escena>
```

## Por qué cada trozo

**`Absolutely no text...`** — sin esto el modelo se inventa palabras. En el
vídeo 1 apareció un «Hi» en la pantalla de un móvil que nadie había pedido.

**`generous margin, full bodies visible`** — sin esto corta las piernas de los
monigotes por el borde inferior.

**Nunca pidas cantidades exactas.** «Nueve de cada diez cuadrados» dio ocho
cuadrados. El modelo no cuenta. Describe el concepto —«un grupo grande de
cuadrados y una flecha»— y deja los números para la voz.

## Resultado

145 imágenes, 1 crédito cada una, unos 300 KB. Tasa de defectos observada
antes de endurecer el prompt: 22%. Después, sensiblemente menor.

Ejemplos en `Video 1/imagenes/`.
