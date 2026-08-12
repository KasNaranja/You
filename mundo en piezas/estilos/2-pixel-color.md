# Estilo 2 — Ilustración saturada con pixel art

Estilo de prueba para el vídeo 2, sacado de una referencia de app de fitness:
ilustración digital muy saturada con influencia de pixel art, fondos detallados,
colores vivos y acabado limpio.

**Modelo:** FLUX.2 `pro` · 16:9 · 1k

## Prompt maestro

```
Bright colorful digital cartoon illustration with pixel art influence. Crisp
clean rendering, highly saturated vivid colors, rich detailed background.
Cheerful storybook mobile game aesthetic. Clean black outlines, soft shading
inside flat color areas, small decorative details everywhere. Vivid blue sky
with fluffy white clouds, strong sunlight, lush vivid greens. Simple stylized
cartoon characters with friendly proportions. Everything readable and well
composed, generous margins, nothing cropped. Absolutely no text, no letters, no
words, no numbers anywhere in the image. Scene: <la escena>
```

## Qué se ha copiado de la referencia y qué no

**Sí:** la saturación, el acabado nítido con influencia de pixel art, los fondos
trabajados, el cielo azul con nubes, los verdes intensos y los detalles
decorativos.

**No:** el sol sonriente, los árboles frutales ni el prado. Eso era el *tema* de
la imagen de referencia, no su estilo. Copiarlo obligaría a meter una pradera
en un vídeo sobre fábricas paradas.

## El problema tonal, que conviene decidir antes de generar 145

Este estilo es **alegre**. Cielos azules, colores vivos, todo luminoso.

El vídeo 2 va de fábricas que cierran, una economía parada y un país que no
puede girar. El estilo 1 —cutre y feo a propósito— no tiene tono, y por eso
funciona con cualquier tema. Este sí lo tiene, y va en dirección contraria al
contenido.

Hay tres salidas:

1. **Asumir el contraste.** Un tema duro con estética luminosa puede funcionar
   como recurso, pero hay que hacerlo a propósito y sostenerlo.
2. **Bajar la alegría.** Quitar «cheerful», el cielo radiante y los verdes
   luminosos, y quedarse con la saturación y el acabado. Sigue siendo bonito sin
   parecer un anuncio.
3. **Reservarlo para otros vídeos.** El 4 (precio de la luz) o el 7 (canal de
   Panamá) aguantan mejor una estética luminosa.

## Variante sobria — la que funciona

Probada la salida 2. **Es claramente mejor para este vídeo.**

```
Colorful digital illustration with pixel art influence. Crisp clean pixel
rendering, saturated but restrained colors, rich detailed background. Serious
documentary mood, not cheerful, not playful, no whimsy. Clean dark outlines,
soft shading inside flat color areas. Overcast muted sky in grey and pale blue,
no bright sunshine. Industrial palette: rust, steel grey, brick red, soot black,
muted dark green. Simple stylized figures seen from a distance, small in the
frame, no detailed faces. Everything readable and well composed, generous
margins, nothing cropped. Absolutely no text, no letters, no words, no numbers
anywhere in the image. Scene: <la escena>
```

Cuatro cambios respecto a la alegre:

| Fuera | Dentro |
|---|---|
| `Cheerful storybook mobile game aesthetic` | `Serious documentary mood, not cheerful` |
| `Vivid blue sky, strong sunlight, lush vivid greens` | `Overcast muted sky, no bright sunshine` |
| (paleta libre) | `rust, steel grey, brick red, soot black` |
| `characters with friendly proportions` | `figures seen from a distance, no detailed faces` |

Ese último cambio importa para un canal faceless: la versión alegre metía caras
definidas y sonrientes, la sobria deja figuras pequeñas y anónimas.

## Lo que hay que decidir antes de comprometerse

Este estilo es **mucho más detallado** que el 1. Eso trae dos cosas:

**A favor** — es bonito, distinto de lo que hay en el nicho en español, y la
locomotora oxidada bajo cielo gris cuenta la tesis del vídeo sin narración.

**En contra** — el fondo compite con la idea. La virtud del estilo 1 es que es
tan simple que el concepto entra de golpe. Aquí el ojo se va a las chimeneas,
las vías y los detalles. En un vídeo explicativo eso puede restar.

Y a más detalle, más superficie de fallo: manos raras, caras deformes,
perspectivas imposibles. En 145 imágenes eso se acumula.

## Coste

Igual que el estilo 1: 1 crédito por imagen a 1k. 145 imágenes ≈ 145 créditos.

## Estado

Ambas variantes probadas con las 5 primeras escenas del vídeo 2:

- `Video 2/prueba-estilo/alegre/` — descartada por tono
- `Video 2/prueba-estilo/sobrio/` — candidata
