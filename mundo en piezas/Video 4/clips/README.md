# Clips del gancho

Los 32 primeros segundos del vídeo van en movimiento en vez de imagen fija.

```
clip1.mp4   0:00 - 0:08   acercamiento a la ciudad tranquila
clip2.mp4   0:08 - 0:16   travelling por la valla con la multitud
clip3.mp4   0:16 - 0:24   el cruce a nado, de noche
clip4.mp4   0:24 - 0:32   la valla vacía al amanecer
```

**Modelo:** Google Veo 3.1 Lite · 8 s · 16:9 · **8 créditos cada uno**

Se versionan aunque el `.gitignore` bloquee los `.mp4`. El montaje se rehace
desde las imágenes y la voz; un clip no, porque la generación de vídeo no es
determinista y no vuelve a salir igual.

## Por qué aquí no se encadenan

En el vídeo 2 los dos clips iban unidos por fotograma puente, porque eran **un
solo plano continuo**: la locomotora frenando.

Aquí no aplica. El gancho son cuatro escenas distintas, así que el corte entre
ellas es lo normal. Cada clip arranca desde la imagen que ya existía para ese
tramo (`0-00`, `0-10`, `0-19`, `0-31`) y no lleva `--end-image`, que fue lo que
rompió la continuidad en el vídeo 2.

## La idea del montaje

El clip 1 es **deliberadamente tranquilo** —una ciudad cualquiera, gaviotas, no
pasa nada— mientras la voz suelta el 72.000 sobre 80.000. El contraste entre lo
que se oye y lo que se ve es lo que sostiene el gancho.

Y el clip 4 cierra con la valla intacta y desierta justo cuando el narrador dice
que no la paró nadie. La imagen dice la tesis antes que las palabras.

## Imágenes sin usar

`0-00`, `0-05`, `0-10`, `0-15`, `0-19`, `0-23`, `0-28` y `0-31` no aparecen en
el montaje final —los clips cubren ese tramo— pero se conservan en `imagenes/`
por si se vuelve a la versión estática.
