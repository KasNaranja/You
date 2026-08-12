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

Son copias. Si tocas una, copia a la otra y súbelo.

Corrección (2026-08-12): aquí decía que Windows no permite enlaces sin modo
desarrollador. Eso solo vale para los **enlaces simbólicos**; las **junctions**
de directorio sí funcionan sin permisos de administrador — comprobado. O sea que
`~/.claude/skills/guardar-video` podría ser una junction al repo y dejar de
depender de que alguien se acuerde de copiar. Para `CLAUDE.md` no sirve: es un
fichero suelto, y ahí la junction no aplica.

```
Copy-Item C:\Users\oriol\.claude\CLAUDE.md C:\Users\oriol\You\configuracion\CLAUDE.md
Copy-Item C:\Users\oriol\You\herramientas\skills\guardar-video\SKILL.md C:\Users\oriol\.claude\skills\guardar-video\SKILL.md
```
