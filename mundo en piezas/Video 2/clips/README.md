# Clips del arranque

Los 16 primeros segundos del vídeo van en movimiento en vez de imagen fija.

```
clip1.mp4    0:00 - 0:08   la locomotora a plena potencia
puente.png                 último fotograma del clip 1
clip2.mp4    0:08 - 0:16   frena hasta pararse
```

**Modelo:** Google Veo 3.1 Lite · 8 s · 16:9 · **8 créditos cada uno**

Se versionan aunque el `.gitignore` bloquee los `.mp4`. El montaje final se
puede rehacer desde las imágenes y la voz; un clip no: la generación de vídeo no
es determinista y no vuelve a salir igual.

## La receta que funciona

**Encadenar por fotograma puente.** El clip 2 arranca en el último fotograma del
clip 1, extraído así:

```
ffmpeg -sseof -0.1 -i clip1.mp4 -frames:v 1 puente.png
```

Y ese PNG se pasa como `--start-image` del siguiente. La unión es invisible.

**No usar `--end-image`.** Fue el error del primer intento: se le puso
`0-13.png` como fin, un dibujo generado aparte con otra locomotora. El modelo no
tuvo más remedio que transformar una máquina en otra a mitad de plano, y se
notaba muchísimo.

Sin imagen de fin, el clip mantiene su propia locomotora de principio a fin.

**No hace falta aterrizar en una imagen concreta.** Basta con que el corte
siguiente cambie de encuadre. Aquí se pasa de plano general a un primer plano de
la rueda (`0-16.png`) y nadie nota dónde acaba el vídeo generado.

## Qué cuesta escalar esto

16 segundos costaron 24 créditos, contando el clip 2 rehecho. El vídeo entero en
clips serían unos 520 créditos, contra los 142 que costó en estático: casi cuatro
veces más, y con el modelo más barato.

Por eso los clips van solo donde compran retención: el arranque, y como mucho el
giro narrativo.

## Imágenes que quedan sin usar

`0-00`, `0-03`, `0-07`, `0-10` y `0-13` no aparecen en el montaje final —los
clips cubren ese tramo—, pero se conservan en `imagenes/` por si algún día se
vuelve a la versión estática.
