# Gancho — Vídeo 5

Los 25,55 primeros segundos, animados. **Audio de un solo bloque, sin uniones.**

## Texto

> Hay algo que está encareciendo el dinero en todo el mundo, y probablemente
> terminará afectando a tu hipoteca, a tus inversiones y a lo que pagas por casi
> todo. Y lo extraño es que no son los bancos centrales. Mientras Estados Unidos,
> Reino Unido, Japón y Europa ven cómo suben sus tipos de interés a largo plazo,
> está ocurriendo algo mucho más importante detrás: los gobiernos necesitan cada
> vez más dinero, y la inteligencia artificial también. Y ambos están compitiendo
> por la misma cosa.

## Cómo se genera el audio

```
python -m edge_tts --voice es-ES-AlvaroNeural --rate +15% --text "<el texto>" \
  --write-media hook.mp3 --write-subtitles hook.srt
```

Un solo fichero, sin recortes ni silencios de relleno. Por eso no tiene parones.

**26,33 s** de fichero, pero **la voz acaba en 25,48 s**: edge-tts deja 0,85 s de
silencio al final. El montaje corta en **25,55 s**. Si no se corta, el vídeo
termina con casi un segundo de nada, que es justo lo que se nota.

## Dónde están las pausas de verdad

No basta con el `.srt`: sus marcas son de frase, y dentro de una frase hay
pausas mayores que entre dos. Lo que manda es la energía del audio:

```
ffmpeg -i hook.mp3 -af "silencedetect=n=-40dB:d=0.15" -f null -
```

| Segundo | Silencio | Qué separa |
|---|---|---|
| 7,15 – 8,10 | 0,95 s | …casi todo. ‖ Y lo extraño… |
| 10,20 – 11,16 | 0,96 s | …bancos centrales. ‖ Mientras… |
| 18,58 – 18,76 | 0,18 s | …más importante detrás: ‖ los gobiernos… |
| 22,60 – 23,57 | 0,97 s | …también. ‖ Y ambos… |
| 25,48 – 26,33 | 0,85 s | cola muerta, se corta |

**Los cortes de imagen caen dentro de esos huecos**, nunca encima de una palabra.

## Los cuatro clips

| Clip | Tramo | Dura | Genera | Qué se ve | Cámara |
|---|---|---|---|---|---|
| 1 | 0,00 – 8,00 | 8,00 | 8 s | LA CALLE. Un ciclista pasa, la gente camina, los coches parados | isométrica |
| 2 | 8,00 – 10,70 | 2,70 | 4 s | EL BANCO CENTRAL. Casi inmóvil, solo cruza gente por abajo | frontal |
| 3 | 10,70 – 18,70 | 8,00 | 8 s | LOS MÁSTILES. Las cuatro banderas ondean, el gráfico quieto | frontal |
| 4 | 18,70 – 25,55 | 6,85 | 8 s | MINISTERIO y CENTRO DE DATOS. Las dos colas avanzan hacia la cámara acorazada | isométrica |

Los clips 2 y 4 se generan más largos de lo que se usan porque Veo solo acepta
4, 6 u 8 segundos. Se recortan por el final con `-t`.

## Por qué este orden funciona

El clip 1 empieza en **tu calle**, no en una metáfora: un banco de barrio, un
cajero, gente andando. El espectador se reconoce antes de entender el tema.

El corte al banco central llega exactamente en «**no** son los bancos
centrales», y con él cambia la cámara: de isométrica a frontal. El cambio de
plano es el argumento.

El 3 enseña los cuatro países como cuatro banderas y una línea que sube. El 4
revela a los dos competidores —un ministerio y un centro de datos— con la
cámara acorazada abierta entre ellos, justo cuando la voz dice que compiten por
lo mismo.

## Las cámaras están locked off

Todos los prompts de movimiento llevan:

```
The camera is completely locked off: no pan, no zoom, no push in, no parallax.
```

Sin eso, Veo mueve la cámara y tiene que inventar lo que entra en cuadro —
que es donde se rompen los carteles y la arquitectura.

## Coherencia con el resto del vídeo

Las semillas son las imágenes de `prueba-literal/`, y los prompts de movimiento
copian **literalmente** las descripciones de `biblia-visual.md`.

Cuando el banco central vuelva a salir en el minuto 1, el 2 y el 7, será el
mismo: cuatro columnas, tres puertas verdes, emblema redondo y el cartel
BANCO CENTRAL en dorado.

## Corrección de color del clip 4

Medida, no a ojo:

```
ffmpeg -ss 1 -i clipN.mp4 -frames:v 1 \
  -vf "signalstats,metadata=print:key=lavfi.signalstats.SATAVG:file=-" -f null -
```

| Clip | Saturación original | Final |
|---|---|---|
| 1 la calle | 4,35 | 4,35 |
| 2 banco central | 2,01 | 2,01 |
| 3 los mástiles | 5,33 | 5,33 |
| 4 la competencia | **7,97** | **5,69** |

El centro de datos salía turquesa y rompía la paleta gris de los otros tres. Se
corrige con `eq=saturation=0.66` en el montaje, que es gratis, en vez de
regenerar la imagen.

**Lo que no funcionó:** añadir `colorbalance=bm=-0.10:gm=-0.06` para quitar azul
y verde. Al restar esos dos canales mete un tinte cálido que **vuelve a subir**
la saturación: 7,97 bajaba solo a 7,36 en vez de a 5,7. Los dos filtros se
peleaban. Con `eq=saturation` a secas basta.

## Estado de los cuatro clips

| Clip | Resultado |
|---|---|
| 1 la calle | Impecable. El edificio no se mueve, solo la gente y el ciclista |
| 2 banco central | Micro-zoom pese al *locked off*, pero el cartel BANCO CENTRAL aguanta legible |
| 3 los mástiles | Impecable. Las banderas ondean, el gráfico no se deforma |
| 4 la competencia | Las dos colas convergen bien, aunque al final se amontonan y tapan parte de la caja |

## Coste

| | Créditos |
|---|---|
| Imagen 4b regenerada (colas distinguibles) | 1 |
| Imagen 4c descartada | 1 |
| Cuatro clips de Veo 3.1 Lite | 32 |
| **Total** | **34** |

Más los 36 de la versión metafórica que se descartó entera.
