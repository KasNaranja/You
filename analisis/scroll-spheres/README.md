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


---

# Cruce con @Tengri1337 — dónde está el hueco

`cruce-tengri.py` empareja los dos catálogos y deja `hueco-vs-tengri.xlsx`
con tres hojas: el catálogo entero marcando lo cogido, los libres que pasaron
del millón, y qué le rindió a Tengri cada adaptación.

Tengri no se inspira en Scroll Spheres: **lo traduce uno a uno.** De sus 39
shorts he localizado el original de 33. Los otros 6 quedan anotados en el
script por si vienen de otra fuente.

## Lo que hay que saber antes de elegir vídeo

**1. El catálogo de Scroll Spheres es 94 % relleno.** De los 1.758 shorts,
1.476 no llegan a 100.000 visitas y la mediana está en 25.000. Los 100 mejores
se llevan el **87 %** de los mil millones de visitas del canal. Copiar del
montón no lleva a ninguna parte: la hoja «Libres +1M» son las 108 filas que
importan.

**2. Las visitas del original predicen poco.** Los tres shorts de 39 millones
que Tengri adaptó le rindieron un 2,6 %, un 0,7 % y un 0,6 %. En cambio
*Transporter 2*, que en Scroll Spheres se quedó en 26.000, le hizo 468.000; y
*Anton Chigurh*, con 43.000 de origen, le hizo 352.000. La mediana de
conversión es del **1,9 %**, pero el reparto no tiene nada que ver con el
tamaño del original.

Con cuidado: parte de las cifras bajas de Tengri son de shorts recién
publicados. Aun así, entre los más antiguos hay tanto 4,7 millones como 1.400
visitas, así que la varianza es real y no solo cuestión de antigüedad.

**3. Lo que sí se repite en sus aciertos** es que la escena se entiende sola,
sin conocer la película: un tío que baja diez pisos en rappel, un sicario al
que le vacían el cargador, un especialista que se juega el cuello. Sus
fracasos son datos de aficionado —qué pistola lleva, cuánto cobró por
palabra—, que en inglés funcionan porque el canal ya tiene público y en frío
no le importan a nadie.

## Cómo se rehace

```
python analisis/scroll-spheres/cruce-tengri.py
```

Vuelve a pedir el catálogo de Tengri (son 39 shorts, tarda segundos) y
reutiliza el de Scroll Spheres que hay en esta carpeta. Si Tengri publica
nuevas adaptaciones hay que añadirlas a mano al diccionario `ADAPTADOS`: los
títulos traducidos no coinciden literalmente y no hay forma automática fiable
de emparejarlos.

## La criba: 33 candidatas en verde

`potencial.py` puntúa las 107 candidatas libres que pasaron del millón. El
criterio no es una intuición: sale de mirar qué le funcionó a Tengri y qué no.

Cuatro preguntas por vídeo:

1. ¿Se entiende en los tres primeros segundos, sin haber visto la película?
2. ¿Hay algo físico que ver, o es un dato que hay que contar?
3. ¿Sobrevive a la traducción? Los acentos, los juegos de palabras y las frases
   míticas en inglés se mueren en castellano, y más con el doblaje.
4. ¿La película o el actor significan algo en España?

Las cuatro a favor es «alto» y va en **verde**. Una en contra, «medio». Dos o
más, «bajo». La hoja «Criterio» del libro lo explica ahí mismo, para que la
criba se pueda discutir en vez de tener que creérsela.

**Colores del libro**

| | |
|---|---|
| verde | libre y de potencial alto — por aquí se empieza |
| gris | lo tiene Tengri: se puede hacer igual, pero compites de frente |
| azul | ya lo hemos preparado nosotros |
| sin color | libre, de potencial medio o bajo |

## Lo que hemos hecho hasta ahora

De los **12** shorts que hemos adaptado, **8 los tiene Tengri también**: el
secuaz de John Wick 2, el Marquis, Anne Hathaway, Ledger, Kylo Ren, Jackie Chan
bajando diez pisos, el narrador de El club de la lucha y el conteo de balas de
John Wick 2. Es decir, dos de cada tres los estamos peleando de frente contra
un canal que lleva meses de ventaja en el mismo nicho.

Los cuatro que sí eran nuestros —*The Accident That Made The Final Cut*,
*It Follows*, *Bullet Train* y *Shutter Island*— salieron de mirar el canal por
encima, no de una lista. Con el Excel delante eso ya no hace falta.

Si alguno de esos 12 se quedó sin publicar, se quita de `TUYOS` en
`potencial.py` y vuelve a la lista de libres.
