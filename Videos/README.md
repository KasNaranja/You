# Videos

Vídeos **producidos** para el canal, una carpeta numerada por vídeo. No
confundir con `Transcriptions/`, que archiva vídeos de terceros descargados de
YouTube para estudiarlos.

```
Videos/
  1/
    video.mp4          el montaje final
    audio/             la voz sola
    imagenes/          una por timestamp + index.txt
    miniaturas/        las candidatas, con la elegida marcada
    guion/             texto, escenas y prompts exactos
    publicacion/       título y descripción listos para pegar
    README.md          ficha, coste y qué queda pendiente
```

## Por qué se guarda todo

El vídeo montado no basta. Si dentro de tres meses hay que rehacer una imagen o
cambiar una frase, hacen falta los prompts exactos, el mapeo de timestamps y la
voz por separado. Eso es lo que permite retocar en vez de empezar de cero.

`imagenes/index.txt` relaciona cada imagen con su segundo y con la frase que
suena en ese momento. Es el fichero que hay que abrir para localizar algo.

## Peso

Cuentan del orden de 90 MB por vídeo: 53 MB de imágenes, 21 de vídeo, 12 de
audio. A este ritmo, unos diez vídeos llenan el giga donde GitHub empieza a
recomendar Git LFS. Cuando toque, la palanca es `imagenes/`, que es lo que más
pesa y lo que menos se consulta.

## Cómo se produce uno

El proceso está descrito en `1/README.md`. En corto: imágenes con FLUX.2 vía
CLI de Higgsfield, voz con edge-tts en local y gratis, montaje con ffmpeg
atando cada imagen a la duración medida de su frase.
