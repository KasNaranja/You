# You

Almacén central del proyecto **You**.

Este repositorio recoge el material del proyecto de forma acumulativa: lo que se
trabaja en cada sesión se guarda aquí, de modo que el histórico de git sirva
como registro de la evolución del proyecto.

## Estructura

| Carpeta | Qué va dentro |
|---|---|
| `Transcriptions/` | Un vídeo archivado por carpeta numerada: audio, fotogramas y transcripción |
| `herramientas/` | Utilidades propias y sus skills, y copias auditadas del código de terceros con la versión fijada en un `PROCEDENCIA.md` |
| `auditorias/` | Informes de seguridad de cada herramienta antes de instalarla |

`CLAUDE.md` en la raíz recoge las reglas de trabajo del repositorio.

La estructura crecerá según entre material nuevo. Cada carpeta se añade cuando
hay algo real que meter dentro, no por adelantado.

## Herramientas

### guardar-video.py

Utilidad propia. Archiva un vídeo en `Transcriptions/` — carpeta numerada,
audio, fotogramas, transcripción y `metadata.json` — y lo sube a `main`.

```
python herramientas/guardar-video.py <url> --push
```

Si el vídeo no trae subtítulos nativos, lo transcribe **en local** con Whisper
(`pip install faster-whisper`): gratis, sin claves ni cuotas, y el audio no sale
de la máquina. Detalles en `Transcriptions/README.md`.

### skill `guardar-video`

`herramientas/skills/guardar-video/SKILL.md` — la copia **canónica** de la skill
que envuelve al script: cuándo se dispara, qué hacen los flags y por qué están
en el valor que están, qué comprobar antes de dar un archivado por bueno.

Se instala copiándola a `~/.claude/skills/guardar-video/SKILL.md`. Si tocas una,
sincroniza la otra.

### claude-video (`/watch`)

Le da a Claude la capacidad de ver vídeo: descarga de YouTube, TikTok, Loom, X,
Instagram y cientos de sitios más, extrae fotogramas y obtiene la transcripción.

- **Código auditado:** `herramientas/claude-video/` (v0.2.0, commit `83da59f`)
- **Informe:** `auditorias/claude-video-0.2.0.md` — apto, sin malware
- **Ojo:** la transcripción del skill **no es local**. Si el vídeo no trae
  subtítulos nativos, el audio se sube a Groq o a OpenAI y hace falta API key.
  Es la diferencia con `guardar-video.py`, que transcribe en la propia máquina.

Instalación, en la máquina donde se vaya a usar:

```
/plugin marketplace add bradautomates/claude-video
/plugin install watch@claude-video
```

Después, `python3 <ruta-del-skill>/scripts/setup.py` instala `ffmpeg` y `yt-dlp`
y crea `~/.config/watch/.env`. **Escribir ahí la API key a mano**, no dictársela
al agente.
