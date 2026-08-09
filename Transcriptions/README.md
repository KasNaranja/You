# Transcriptions

Un vídeo por carpeta, numeradas correlativamente. Las crea
`herramientas/guardar-video.py`; no hay que numerarlas a mano.

```
Transcriptions/
  1/
    audio/        audio.mp3 (mono 16 kHz)
    frames/       frame_001.jpg… + index.txt (imagen → segundo del vídeo)
    transcript/   .vtt originales + transcript.txt con marcas de tiempo
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
