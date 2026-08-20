# @Scroll-Spheres — catálogo completo de Shorts

Volcado del canal `UCo1mpfrgH4N3kmPY_MdOphA` a 20/08/2026.

| | |
|---|---|
| Shorts | **1.758** (únicos, sin repetidos) |
| Vídeos largos | ninguno: el canal no tiene pestaña de vídeos |
| Visitas acumuladas | **1.036.640.521** |
| Primero | 24/08/2025 |
| Ritmo | ~4-5 shorts al día durante 12 meses |

## Ficheros

| Fichero | Qué es |
|---|---|
| `shorts-scrollspheres.xlsx` | Título, visitas y fecha. Tres columnas, filtro y fila fija. |
| `shorts-scrollspheres.csv` | Lo mismo en texto plano, separado por `;` y en UTF-8 con BOM. |
| `shorts-scrollspheres-catalogo.json` | El catálogo en bruto, con el identificador de cada vídeo. |

Las filas van del más reciente al más antiguo, que es el orden en que YouTube
devuelve la pestaña. **Ese orden es cronológico exacto aunque falte la fecha.**

## Cómo se completa la columna de fecha

El mosaico de Shorts no muestra la fecha en ninguna forma —ni siquiera un «hace
3 semanas»—, así que hay que pedir la ficha de cada vídeo uno a uno. Eso solo
funciona **desde una conexión doméstica**: desde un centro de datos Google
responde con un captcha a las pocas decenas de peticiones.

Desde el PC, en la raíz del repositorio:

```
pip install openpyxl
python herramientas/shorts-canal.py https://www.youtube.com/@Scroll-Spheres --salida "analisis/scroll-spheres/shorts-scrollspheres"
```

Tarda cosa de una hora. Va guardando el avance en `…-avance.json`, así que se
puede cerrar y volver a lanzar el mismo comando: retoma donde iba. De paso
sustituye las visitas redondeadas de YouTube (2.700) por las exactas (2.789).

Si no quiere volver a recorrer el canal, se reutiliza el catálogo de aquí
añadiendo `--catalogo "analisis/scroll-spheres/shorts-scrollspheres-catalogo.json"`.
La contrapartida es que no recogerá los shorts publicados desde el 20/08/2026.

La otra vía es la API oficial con `--clave`: 36 peticiones en vez de 1.758 y sí
funciona desde la nube, pero hay que darse de alta una clave en Google Cloud.
