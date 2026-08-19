# Gancho — Vídeo 5

Los 27,8 primeros segundos, animados. **Audio de un solo bloque, con la voz
clonada del autor** (ElevenLabs, voz «You», `hjCyEOhV6mCX4KFzbMDQ`).

## Texto

> Hay algo que está encareciendo el dinero en todo el mundo, y probablemente
> terminará afectando a tu hipoteca, a tus inversiones y a lo que pagas por casi
> todo. Y lo extraño es que no son los bancos centrales. Mientras Estados Unidos,
> Reino Unido, Japón y Europa ven cómo suben sus tipos de interés a largo plazo,
> está ocurriendo algo mucho más importante detrás: los gobiernos necesitan cada
> vez más dinero, y la inteligencia artificial también. Y ambos están compitiendo
> por la misma cosa.

## Cómo se genera el audio

Con `herramientas/generar-voz-eleven.py`, que llama al endpoint
`with-timestamps`: devuelve el audio y el segundo exacto en que arranca cada
carácter. Ajustes: `eleven_multilingual_v2`, stability 0,45, similarity 0,75.

490 caracteres = 490 créditos por tirada.

**27,82 s** y, al contrario que edge-tts, **sin cola de silencio al final**: la
voz acaba exactamente donde acaba el fichero.

## Dónde están las pausas de verdad

```
ffmpeg -i crudo.mp3 -af "silencedetect=n=-38dB:d=0.15" -f null -
```

| Segundo | Silencio | Qué separa |
|---|---|---|
| 8,91 – 9,25 | 0,34 s | …casi todo. ‖ Y lo extraño… |
| 11,74 – 12,01 | 0,27 s | …bancos centrales. ‖ Mientras… |
| 20,79 – 20,97 | 0,18 s | …más importante detrás: ‖ los gobiernos… |
| 25,30 – 25,52 | 0,22 s | …también. ‖ Y ambos… |

**Los cortes de imagen caen dentro de esos huecos**, nunca encima de una palabra.

## Los cuatro clips

| Clip | Tramo | Dura | Ajuste | Qué se ve | Cámara |
|---|---|---|---|---|---|
| 1 | 0,00 – 9,05 | 9,05 | ralentizado ×1,131 | LA CALLE. Un ciclista pasa, la gente camina | isométrica |
| 2 | 9,05 – 11,85 | 2,80 | recortado de 4 s | EL BANCO CENTRAL, casi inmóvil | frontal |
| 3 | 11,85 – 20,88 | 9,03 | ralentizado ×1,129 | LOS MÁSTILES. Las banderas ondean | frontal |
| 4 | 20,88 – 27,82 | 6,94 | recortado de 8 s + `eq=saturation=0.66` | MINISTERIO y CENTRO DE DATOS, las dos colas | isométrica |

La voz clonada habla más pausada que edge-tts al +15% (27,8 s contra 25,5), así
que los tramos 1 y 3 pasaron de ~8 a ~9 s. Los clips son de 8: se ralentizan un
13% con `setpts`, invisible en escenas de ambiente. **No se regeneró ningún
clip**: son los mismos cuatro de Veo, con los cortes movidos a las pausas nuevas.

## Por qué este orden funciona

El clip 1 empieza en **tu calle**: un banco de barrio, un cajero, gente andando.
El espectador se reconoce antes de entender el tema.

El corte al banco central llega en «**no** son los bancos centrales», y con él
cambia la cámara: de isométrica a frontal. El cambio de plano es el argumento.

El 3 enseña los cuatro países como banderas y una línea que sube. El 4 revela a
los dos competidores justo cuando la voz dice que compiten por lo mismo.

## Las cámaras están locked off

Todos los prompts de movimiento llevan:

```
The camera is completely locked off: no pan, no zoom, no push in, no parallax.
```

Sin eso, Veo mueve la cámara y tiene que inventar lo que entra en cuadro — que
es donde se rompen los carteles y la arquitectura.

## Corrección de color del clip 4

El centro de datos salía turquesa (saturación media 7,97 contra 2–5,3 de los
otros). Se corrige con `eq=saturation=0.66` en el montaje → 5,69. Añadir
`colorbalance` encima **empeora**: mete tinte cálido y la vuelve a subir.

## Coherencia con el resto del vídeo

Las semillas son las imágenes de `prueba-literal/` y los prompts copian
literalmente `biblia-visual.md`. Cuando el banco central vuelva a salir en los
minutos 1, 2 y 7, será el mismo edificio.

## Coste acumulado del gancho

| | |
|---|---|
| Higgsfield: semillas + 4 clips Veo | 34 créditos |
| Higgsfield: versión metafórica descartada | 36 créditos |
| ElevenLabs: esta tirada | 490 caracteres |
