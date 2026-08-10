# configuracion

Copia versionada de la configuración de Claude Code que vive fuera del repo, en
`~/.claude/`. No se carga desde aquí: aquí está para que quede en el histórico y
se pueda restaurar.

| Fichero | Copia viva |
|---|---|
| `CLAUDE.md` | `~/.claude/CLAUDE.md` |

Las skills van aparte, en `herramientas/skills/`, porque son herramienta y no
configuración.

## Por qué

`~/.claude/CLAUDE.md` es lo que hace que pegar una URL de vídeo dispare el
archivado sin explicar nada. Sin él, el repo sobrevive pero la automatización
no. Es el tipo de fichero que se toca una vez, se olvida, y se echa de menos al
cambiar de máquina.

## Sincronizar

Son copias, no enlaces: Windows no permite enlaces simbólicos sin activar el
modo desarrollador. Si tocas una, copia a la otra y súbelo.

```
Copy-Item C:\Users\oriol\.claude\CLAUDE.md C:\Users\oriol\You\configuracion\CLAUDE.md
Copy-Item C:\Users\oriol\You\herramientas\skills\guardar-video\SKILL.md C:\Users\oriol\.claude\skills\guardar-video\SKILL.md
```
