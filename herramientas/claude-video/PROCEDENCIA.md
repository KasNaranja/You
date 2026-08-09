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

## Esta copia no es la instalación

El plugin se instala aparte, en la máquina donde se use:

```
/plugin marketplace add bradautomates/claude-video
/plugin install watch@claude-video
```

Lo de aquí es el **registro de qué código se auditó**, para poder comparar más
adelante. No se ejecuta desde este repositorio.
