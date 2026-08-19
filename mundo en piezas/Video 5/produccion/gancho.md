# Gancho — Vídeo 5

Los 26,33 primeros segundos. **Audio de un solo bloque, sin uniones.**

## Texto

> Hay algo que está encareciendo el dinero en todo el mundo, y probablemente
> terminará afectando a tu hipoteca, a tus inversiones y a lo que pagas por casi
> todo. Y lo extraño es que no son los bancos centrales. Mientras Estados Unidos,
> Reino Unido, Japón y Europa ven cómo suben sus tipos de interés a largo plazo,
> está ocurriendo algo mucho más importante detrás: los gobiernos necesitan cada
> vez más dinero, y la inteligencia artificial también. Y ambos están compitiendo
> por la misma cosa.

## Cómo se genera

```
python -m edge_tts --voice es-ES-AlvaroNeural --rate +15% --text "<el texto>" \
  --write-media hook.mp3 --write-subtitles hook.srt
```

**26,33 s** a +15%. A +10% son 27,53 s y a +20%, 25,22 s.

Un solo fichero, sin recortes ni silencios de relleno. Por eso no tiene parones.

## Dónde cae cada frase

Medido del `.srt` que emite el propio motor:

| Segundo | Frase |
|---|---|
| 0,10 | Hay algo que está encareciendo el dinero… |
| 7,98 | Y lo extraño es que no son los bancos centrales. |
| 11,00 | Mientras Estados Unidos, Reino Unido, Japón y Europa… |
| 23,41 | Y ambos están compitiendo por la misma cosa. |

## Los cuatro clips

Duraciones elegidas para que los cortes caigan **entre frases**, nunca encima de
una palabra.

| Clip | Tramo | Qué se ve | Frase que suena |
|---|---|---|---|
| 1 | 0,00 – 8,00 | EL DEPÓSITO en plano general. La cámara se acerca muy despacio. Nadie en la ventanilla | «Hay algo que está encareciendo el dinero…» |
| 2 | 8,00 – 12,00 | EL BANCO CENTRAL. Una mano baja la palanca de latón hasta abajo. Nada más se mueve | «…no son los bancos centrales.» |
| 3 | 12,00 – 20,00 | EL DIAL DEL MERCADO junto al banco central. La aguja sube sola hacia la derecha mientras la palanca sigue abajo | «Mientras Estados Unidos, Reino Unido…» |
| 4 | 20,00 – 26,33 | EL DEPÓSITO otra vez, ahora con LA COLA DE LA IA y LA COLA DEL ESTADO convergiendo hacia la misma ventanilla | «…compitiendo por la misma cosa.» |

El clip 4 se genera de 8 s y se recorta a 6,33.

## Por qué este orden funciona

El clip 1 es **deliberadamente tranquilo** mientras la voz habla de tu hipoteca:
un depósito lleno y una ventanilla sin nadie. El espectador aún no sabe qué está
mirando.

El clip 2 responde a «no son los bancos centrales» enseñando literalmente la
palanca bajando. Y el 3 mantiene esa palanca abajo mientras el dial sube solo —
**la paradoja del vídeo entera en un plano**, sin una palabra de explicación.

El 4 revela las dos colas justo cuando la voz dice que compiten por lo mismo. La
imagen y la frase aterrizan a la vez.

## Coherencia con el resto del vídeo

Los cuatro clips se siembran con `--start-image` desde las imágenes fijas de esos
mismos tramos, y sus prompts copian **literalmente** las descripciones de
`biblia-visual.md`.

Cuando en el minuto 3 vuelva a aparecer el depósito, será el mismo depósito:
mismos remaches, misma cúpula, misma ventanilla única.
