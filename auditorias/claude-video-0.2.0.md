# Auditoría de seguridad — claude-video (`/watch`) v0.2.0

**Fecha:** 2026-08-09
**Commit auditado:** `83da59fa78c3eee9e20f515fe75c438bb5166efd`
**Origen:** https://github.com/bradautomates/claude-video · MIT
**Alcance:** 10 scripts Python, hook de sesión, manifiestos de plugin, `SKILL.md`

## Veredicto

**Apto para instalar.** No se ha encontrado código malicioso. El código está
bien escrito, con separación clara de responsabilidades y 11 ficheros de tests.

Quedan riesgos reales, ninguno de ellos malware — están en la sección
"Riesgos residuales".

## Qué se buscó y no está

| Vector | Resultado |
|---|---|
| `eval` / `exec` / código dinámico | No aparece |
| `shell=True` en subprocess | No aparece — siempre listas de argumentos |
| Telemetría, analytics, llamadas a casa | Ninguna |
| Acceso a `~/.ssh`, `~/.aws`, llaveros | Ninguno |
| Acceso a correo, contactos, navegador | Ninguno |
| Ejecución con `sudo` | Nunca — es política explícita del instalador |
| Descarga de código en tiempo de ejecución | Ninguna |

Las únicas conexiones salientes del código son `api.groq.com` y
`api.openai.com`, ambas para transcripción. No hay ningún otro destino.

## Permisos que declara

```yaml
allowed-tools: Bash, Read, AskUserQuestion
```

Estrecho y coherente con la función. No pide herramientas de red ni de web.

## Buenas prácticas encontradas

- **`--` antes de la URL** en las llamadas a `yt-dlp`. Impide que una URL que
  empiece por `-` se interprete como opción. Es defensa deliberada contra
  inyección de argumentos.
- **Fichero de secretos a `0600`**, y el hook **avisa** si los permisos están
  flojos, sugiriendo el `chmod`.
- **Instalador sin `sudo`.** En macOS usa Homebrew; en Linux y Windows solo
  *imprime* los comandos para que los ejecute el usuario.
- **Solo instala `ffmpeg` y `yt-dlp`.** Nada más.
- Lee `.env` del directorio de trabajo, pero **solo extrae `GROQ_API_KEY` y
  `OPENAI_API_KEY` por nombre exacto**. No vuelca el fichero entero.

## Hook de sesión

`hooks/hooks.json` registra un `SessionStart` que ejecuta
`hooks/scripts/check-setup.sh` con timeout de 5 s.

Revisado línea a línea: lee la configuración local, comprueba si `ffmpeg` y
`yt-dlp` están presentes, e imprime una línea de estado. **No accede a la red.**
Lee las claves solo para comprobar si existen; no las imprime ni las transmite.

## Discrepancias con lo que se anunció

La ficha de la idea afirmaba dos cosas **falsas**:

| Se decía | Realidad |
|---|---|
| "Transcribe el audio **en local**" | **No hay Whisper local.** El audio se sube a Groq o a OpenAI |
| "Gratis y **sin API key**" | **Necesita API key** salvo que el vídeo traiga subtítulos nativos |

El flujo real de transcripción es:

1. Si el vídeo tiene **subtítulos nativos** → los descarga. Nada sale de la
   máquina más allá de la propia petición a la plataforma.
2. Si no los tiene → extrae el audio a mp3 mono 16 kHz, lo trocea en fragmentos
   de 24 MB y **los sube** a `api.groq.com` o `api.openai.com`.
3. Sin clave y sin subtítulos → devuelve solo fotogramas, sin transcripción.

## Riesgos residuales

### 1. Inyección de prompt (el más serio)

El `SKILL.md` **no advierte en ningún momento** de que la transcripción es dato
no fiable. Se buscó expresamente y no aparece.

Un vídeo puede llevar, hablado o escrito en pantalla, instrucciones dirigidas al
agente. Esas instrucciones entran en el contexto con el mismo aspecto que una
petición legítima del usuario.

El plugin por sí solo no accede a nada sensible; el riesgo es que **sirva de
canal** para dar órdenes a un agente que sí tiene accesos conectados (GitHub,
Google Drive, etc.).

**Mitigación aplicada:** regla explícita en el `CLAUDE.md` de este repositorio.

### 2. Privacidad del audio

Vídeos sin subtítulos → el audio sale a un tercero. Aceptable para contenido
público; **a valorar** para material interno de empresa.

**Mitigación disponible si hace falta:** añadir Whisper local como alternativa.
No implementado — se hará solo si aparece la necesidad.

### 3. La clave puede pasar por la conversación

El `SKILL.md` instruye al agente a escribir la API key en
`~/.config/watch/.env`. Funciona, pero la clave atraviesa el contexto del chat.

**Mitigación:** escribir la clave a mano en ese fichero.

### 4. Versiones futuras

Instalar por marketplace implica confiar también en actualizaciones posteriores.
Esta auditoría cubre **solo** el commit `83da59f`.

**Mitigación:** versión fijada y copia guardada en `herramientas/claude-video/`
para poder comparar el diff antes de actualizar.

### 5. Condiciones de uso de las plataformas

Descargar vídeos de YouTube incumple sus términos de servicio. Sin relevancia
práctica para uso personal, pero conviene saberlo.

## Huellas de verificación

Instalación verificada el 2026-08-09 en Windows: coincidencia exacta por dos
vías independientes.

**Vía 1 — commit del marketplace:**

```powershell
git -C "$env:USERPROFILE\.claude\plugins\marketplaces\claude-video" rev-parse HEAD
# → 83da59fa78c3eee9e20f515fe75c438bb5166efd
```

**Vía 2 — SHA256 de los ficheros ejecutables.**

Ojo: git convierte LF a CRLF al descargar en Windows, así que **los hashes
difieren según el sistema aunque el contenido sea idéntico**. Por eso van las
dos columnas. Comparar contra la que corresponda.

| Fichero | SHA256 (LF, Linux/macOS) | SHA256 (CRLF, Windows) |
|---|---|---|
| `SKILL.md` | `10dc8e56699e99a9…` | `1cb6fca53bf444fe…` |
| `config.py` | `a672f1b3b888ee90…` | `377db1bd524e6537…` |
| `download.py` | `e3db8c8418a0372a…` | `018c43434b4377e8…` |
| `frames.py` | `ad317574facd619f…` | `c6cf760d2d86b253…` |
| `setup.py` | `c8d2906fc4e80479…` | `b4bc14748bc01871…` |
| `transcribe.py` | `f9736e126d3f3c41…` | `9260a2c8b4375dd0…` |
| `watch.py` | `22a617de94978106…` | `f8f27db11d9a6f22…` |
| `whisper.py` | `4845e95d7467b1d4…` | `b00a7cd8dd57e0cf…` |

Para recalcular las tuyas en Windows:

```powershell
Get-ChildItem "$env:USERPROFILE\.claude\plugins\cache\claude-video\watch\0.2.0\skills\watch" -Recurse -Include *.py,SKILL.md |
  Get-FileHash -Algorithm SHA256 |
  ForEach-Object { "{0}  {1}" -f $_.Hash.ToLower(), (Split-Path $_.Path -Leaf) } | Sort-Object
```

**Si alguna huella no coincide con ninguna de las dos columnas, no usar el
plugin** hasta revisar qué ha cambiado.

## Cómo repetir esta auditoría

```bash
git clone --depth 1 https://github.com/bradautomates/claude-video /tmp/cv
cd /tmp/cv

# Red y ejecución
grep -rn "requests\.\|urllib\|http://\|https://\|socket" --include="*.py" .
grep -rn "eval(\|exec(\|os\.system\|shell=True" --include="*.py" .

# Telemetría
grep -rniE "telemetry|analytics|posthog|sentry|mixpanel" .

# Acceso a ficheros sensibles
grep -rnE "Path\.home\(\)|os\.environ|\.ssh|\.aws" --include="*.py" .

# Hook que se ejecuta solo
cat hooks/hooks.json && cat hooks/scripts/*.sh
```
