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

## Lo que dicen las fechas

Ya están las 1.758, con visitas exactas: **1.055.801.922 visitas en 362 días**,
del 24/08/2025 al 20/08/2026. La hoja «Ritmo» del libro lo resume mes a mes.

**Scroll Spheres ha abandonado el volumen.** Subió de 1,9 shorts al día hasta
**10 al día en enero de 2026** y desde entonces ha bajado a 3,8. Lo que importa
es la mediana de visitas durante ese recorrido:

| Mes | Shorts/día | Mediana |
|---|---:|---:|
| ene 2026 | 10,0 | 31.785 |
| abr 2026 | 7,6 | **11.471** |
| jul 2026 | 3,6 | 39.799 |
| ago 2026 | 3,8 | 165.530 |

Abril fue su mes de más acumulado y el peor por vídeo. Publicando menos de la
mitad, su suelo se ha multiplicado. Agosto está inflado porque el mes va por la
mitad y los shorts recientes siguen sumando, pero la tendencia de mayo a julio
ya es clara por sí sola.

**Un short madura en una semana.** La mayoría de las visitas llegan en los
primeros siete días. A partir de ahí ya se puede juzgar si uno ha funcionado; no
hace falta esperar un mes para decidir si el enfoque valía.

**La criba aguanta.** Ordenando por «× mediana del mes» —que corrige la ventaja
de lo antiguo y el crecimiento del canal— los 60 primeros son exactamente los
mismos vídeos que ya estaban por encima del millón. El corte no dejaba fuera
ningún outlier escondido.

## El plan

La primera hoja del libro, «Plan», es lo único que hay que leer para ponerse a
trabajar: los 34 verdes en orden, con el día que toca cada uno y por qué va en
esa posición. El orden vive en `plan.py`.

**No está ordenado por visitas.** Un canal que empieza no tiene suscriptores, así
que todo lo que entra viene del feed de Shorts, delante de gente que no lo conoce
de nada. Eso pesa más que el número del original. Deciden tres cosas:

- **Reconocimiento inmediato en España.** En frío ganan las marcas que cualquiera
  identifica en medio segundo.
- **Lo que ya está probado.** Jackie Chan es el nombre con mejor conversión de
  todo el cruce: los dos mayores éxitos de Tengri salen de ahí, y queda uno libre.
  Va el primero aunque su original no sea de los más vistos.
- **No repetir saga seguida.** Dos de Piratas pegados se comen el uno al otro.

**Dos al día, diecisiete días.** El ritmo tampoco es un capricho: cuando Scroll
Spheres subía diez al día su mediana cayó a 11.471 visitas, y ahora que publica
3,8 va por encima de 165.000. Dos son tiros suficientes para que el algoritmo
encuentre el canal sin bajar la calidad de cada uno.

**Al séptimo día hay que parar y mirar.** Un short madura en una semana, así que
para entonces los catorce primeros ya se pueden juzgar. Lo que haya funcionado
dice por dónde seguir, y el resto de la lista se reordena con eso — para eso el
orden está en un fichero aparte y no clavado en el Excel.

### Corrección de una errata

Ocho títulos de `POTENCIAL` tenían comas convertidas en puntos: se colaron al
copiarlos de una salida de terminal que formateaba miles. No casaban con el
catálogo y se quedaban sin puntuar. Corregidos, los verdes pasan de 33 a 34 —el
que faltaba era el de *Crepúsculo*—. Si se vuelven a copiar títulos de una
salida con `.replace(",", ".")`, ojo con esto.

### La columna de enlaces

La hoja «Plan» lleva el enlace completo al original de cada short, no un «ver»:
es la URL que hay que copiar para pedir la portada, los títulos, la descripción
y las etiquetas.

Un aviso: algunos vídeos del canal tienen el incrustado desactivado —suele pasar
con los que llevan música con derechos— y ahí oEmbed responde 401 y no da el
título. El primero del plan, el de Jackie Chan, es uno de ellos. `short-fuente.py`
lo resuelve solo tirando del catálogo de esta carpeta; el fotograma se descarga
igual.
