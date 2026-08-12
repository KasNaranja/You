# El Mundo en Piezas

Canal de divulgación en español. [@mundoenpiezas](https://www.youtube.com/@mundoenpiezas)

Una carpeta por vídeo, con todo lo necesario para republicarlo o retocarlo sin
empezar de cero: el guion, las imágenes, la voz, el montaje y los textos de
publicación.

```
Video 1/
  guion.md              el guion con sus notas editoriales
  prompt-imagenes.md    el plan de generación
  video.mp4             el montaje final
  audio/voz.mp3         la voz sola, para remontar
  imagenes/             una por marca de tiempo + index.txt
  miniaturas/           las candidatas, con la elegida marcada
  produccion/           ficha, escenas y los prompts realmente usados
  publicacion/          título y descripción listos para pegar
```

## Cómo se produce un vídeo

1. **Guion** — frases cortas, segunda persona, cada dato con una comparación
   física al lado. Una marca de tiempo cada 3-4 segundos.
2. **Imágenes** — una por marca de tiempo. FLUX.2 `pro` a 1k y 16:9 desde la
   CLI de Higgsfield, en una sesión local. Estilo de dibujo cutre de MS Paint.
3. **Voz** — edge-tts en local, gratis y sin clave. Se recorta el silencio
   propio de cada clip y se calibra la velocidad línea a línea hasta que cabe
   en su hueco, de modo que cada frase arranca en el segundo que dice el guion.
4. **Montaje** — ffmpeg. Cada imagen dura lo que el guion asigna a su frase.
   No hace falta CapCut para el montaje base.

El detalle de cada paso, con los fallos que costaron encontrarse, está en
`Video 1/produccion/ficha.md`.

## Referencias de estilo

Los vídeos que se estudiaron para construir el formato están archivados en
`Transcriptions/`: Zenn (`5/`) para el tono y Los Ecomonos (`6/`) para la
estructura narrativa y la paleta de color de las miniaturas.

## Peso

Del orden de 90 MB por vídeo, casi todo imágenes. A diez vídeos toca plantearse
Git LFS; la palanca sería `imagenes/`, que es lo que más pesa y lo que menos se
consulta.
