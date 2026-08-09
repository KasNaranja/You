# Procedencia de esta copia

Copia literal y auditada del plugin `claude-video`, guardada aquí para que el
código que se ejecuta en local esté también versionado en este repositorio.

## Origen

| | |
|---|---|
| Repositorio | https://github.com/bradautomates/claude-video |
| Autor | Bradley Bonanno (`bradautomates`) |
| Licencia | MIT (ver `LICENSE`) |
| Versión del plugin | 0.2.0 |
| **Commit fijado** | `83da59fa78c3eee9e20f515fe75c438bb5166efd` |
| Fecha del commit | 2026-06-30 |
| Fecha de la copia | 2026-08-09 |

**Esta es la versión auditada.** El informe está en
`auditorias/claude-video-0.2.0.md`. Cualquier versión posterior **no está
auditada**: antes de actualizar, comparar el diff contra este commit.

Para ver qué ha cambiado desde la versión auditada:

```bash
git clone https://github.com/bradautomates/claude-video /tmp/cv
git -C /tmp/cv diff 83da59fa78c3eee9e20f515fe75c438bb5166efd..HEAD
```

## Modificaciones respecto al original

Solo una, y no afecta al funcionamiento:

- **`CLAUDE.md` → `CLAUDE.md.original`.** El fichero original contenía
  `@AGENTS.md`, que hace que las instrucciones de desarrollo del plugin se
  carguen automáticamente en cualquier sesión que trabaje en este directorio.
  Son instrucciones de un tercero entrando solas en el contexto del agente, así
  que se renombra para que no se cargue. El contenido se conserva íntegro.

El resto es idéntico al original, incluida la licencia.

## Nota sobre `.github/workflows/release.yml`

La copia incluye el workflow de release del proyecto original. **No se ejecuta:**
GitHub Actions solo lee workflows de `.github/workflows/` en la raíz del
repositorio, y aquí está anidado. Se conserva por fidelidad con el original.

## Incidencias conocidas

### `-vsync` eliminado en ffmpeg 8+ (rompe la extracción de fotogramas)

**Detectado:** 2026-08-09, en la primera ejecución real con ffmpeg 9.0.

`skills/watch/scripts/frames.py` invoca ffmpeg con `-vsync vfr` en dos sitios:

| Línea | Ruta afectada |
|---|---|
| 256 | selección por escenas (`balanced`, `token-burner`) |
| 615 | keyframes rápidos (`efficient`) |

`-vsync` se eliminó de ffmpeg en la versión 8; su sustituto es `-fps_mode`. Con
ffmpeg 9.0 **ambas llamadas fallan**, así que el plugin no extrae fotogramas por
ninguno de sus modos. El vídeo se descarga bien; lo que rompe es el paso de
fotogramas.

**Arreglo** (sustitución literal, misma semántica):

```
"-vsync", "vfr"   →   "-fps_mode", "vfr"
```

Aplicado sobre la instalación local en Windows:

```powershell
$f = "$env:USERPROFILE\.claude\plugins\cache\claude-video\watch\0.2.0\skills\watch\scripts\frames.py"
Copy-Item $f "$f.bak"
$c = [System.IO.File]::ReadAllText($f)
$c = $c.Replace('"-vsync", "vfr"', '"-fps_mode", "vfr"')
[System.IO.File]::WriteAllText($f, $c, (New-Object System.Text.UTF8Encoding $false))
Select-String -Path $f -Pattern "vsync|fps_mode"
```

**Consecuencias a tener en cuenta:**

- El parche **cambia el hash** de `frames.py`, así que dejará de coincidir con
  las huellas de `auditorias/claude-video-0.2.0.md`. Es esperado: el único
  cambio es esa sustitución, verificable con `Select-String`.
- Una actualización del plugin **pisa el parche**. Habrá que reaplicarlo, o
  esperar a que lo arreglen aguas arriba.
- La copia de este repositorio **se deja sin parchear** a propósito, para que
  siga siendo el reflejo exacto del commit auditado.

### Descarga de subtítulos limitada por YouTube (HTTP 429)

También en la primera ejecución. YouTube limita la descarga de subtítulos por
volumen de peticiones. No es un fallo del plugin. Reintentar más tarde, o tener
configurada una clave de Whisper para que caiga en la transcripción por audio.

## Esta copia no es la instalación

El plugin se instala aparte, en la máquina donde se use:

```
/plugin marketplace add bradautomates/claude-video
/plugin install watch@claude-video
```

Lo de aquí es el **registro de qué código se auditó**, para poder comparar más
adelante. No se ejecuta desde este repositorio.
