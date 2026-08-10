# Transcriptions

Un vídeo por carpeta, numeradas correlativamente. Las crea
`herramientas/guardar-video.py`; no hay que numerarlas a mano.

```
Transcriptions/
  1/
    audio/        audio.mp3 (mono 16 kHz)
    frames/       frame_001.jpg… + index.txt (imagen → segundo del vídeo)
    transcript/   .vtt originales, transcript.txt con marcas de tiempo y
                  transcript-anotado.txt con los cortes de escena intercalados
    metadata.json título, canal, duración, URL, fecha
    README.md     resumen de la ficha
  2/
  …
```

## Cómo añadir uno

Desde una sesión **local** (Desktop o terminal), basta con pegar la URL y pedir
que se guarde. O a mano:

```
python3 herramientas/guardar-video.py <url> --push
```

Opciones de `--detail`: `efficient` (50 fotogramas), `balanced` (100, por
defecto) o `token-burner` (sin tope).

**Un fotograma por cada cambio de escena.** Cada imagen guardada corresponde a
un momento en que el vídeo cambia de verdad, no a una rejilla arbitraria.
`--umbral` ajusta la sensibilidad (0.3 por defecto; más bajo, más cortes).

Con una red de seguridad: si pasan más de `--hueco-max` segundos (30 por
defecto) sin ningún corte, se fuerza un fotograma igualmente. Hace falta porque
la densidad de cortes depende del montaje y no se sabe de antemano — un vídeo de
animación de 8 min dio 165, y uno de 28 min de charla a cámara dio 11, dejando
23 minutos sin una sola imagen.

Cuenta **50–90 KB por imagen** según lo movido que sea el vídeo.

`--alto-max` limita la resolución de origen (1080 por defecto). Los fotogramas
se escalan a 1280 px de ancho, así que bajar 4K no mejora el resultado: solo
multiplica por cuatro la descarga y la decodificación. El mismo vídeo de 28 min
pasó de 779 MB y >25 min a 204 MB y 3 min.

## Dos avisos

**No funciona desde sesiones en la nube.** YouTube bloquea las IPs de centros de
datos. Tiene que ser una sesión que corra en la máquina del usuario.

**Esto engorda el repositorio.** Fotogramas y audio ocupan; calcula del orden de
5–15 MB por vídeo corto. Si algún día pesa demasiado, las opciones son mover los
binarios a Git LFS o dejar de versionar `audio/` y quedarse con transcripción y
fotogramas.

## Si un vídeo no tiene subtítulos

Se transcribe **en local** con Whisper (`faster-whisper`): gratis, sin claves ni
cuotas de API, y el audio no sale de la máquina. Requiere `pip install
faster-whisper` una vez; el modelo se descarga solo la primera vez.

El modelo se elige con `--modelo`: `small` por defecto, `medium` o `large-v3`
afinan más a cambio de tardar más, y `no` desactiva la transcripción local.

`metadata.json` deja constancia de la vía en el campo `transcripcion`:
`subtitulos`, `whisper-local` o `ninguna`.

Solo si no hay subtítulos **y** falla o se desactiva Whisper aparece
`transcript/SIN-SUBTITULOS.txt`. El audio sigue en `audio/audio.mp3` para
transcribirlo por otra vía.
