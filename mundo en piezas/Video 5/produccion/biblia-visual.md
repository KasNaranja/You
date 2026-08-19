# Biblia visual — Vídeo 5

Los objetos que se repiten a lo largo del vídeo, descritos **una sola vez y
palabra por palabra**. Cada escena que use uno de ellos copia su descripción
literal, sin reformular.

Es lo que hace que 146 imágenes parezcan el mismo vídeo. Sin esto, el modelo
reinventa el edificio en cada plano.

## El enfoque: literal, no metafórico

La primera versión de este vídeo era metafórica —un depósito de acero remachado
lleno de monedas como «el ahorro del mundo»— y se descartó entera. Si la voz
dice «banco central», se ve un banco central con su cartel. Si dice «Estados
Unidos, Reino Unido, Japón y Europa», se ven cuatro mástiles con sus banderas.

**El modelo sí sabe escribir carteles cortos.** «BANCO CENTRAL» y «SE VENDE»
salieron perfectos. La condición es: mayúsculas, sin tildes, dos o tres palabras
como mucho, y en un sitio donde iría un rótulo de verdad. Nada de párrafos, ni
cifras, ni etiquetas flotantes.

## El mundo

Va delante de todos los prompts, en imágenes y en clips:

```
Colorful digital illustration with pixel art influence, crisp clean pixel
rendering. Flat overcast grey sky, diffuse daylight, no sun, no harsh cast
shadows. Muted palette: concrete grey, cool steel blue, brass and gold accents,
dark green, warm beige stone. Figures are small and anonymous, no facial
detail. Serious documentary mood, no whimsy, no cartoon exaggeration.
```

## Las dos cámaras

El cambio de cámara significa algo. No se alterna al azar.

| Tipo de escena | Cámara | Cuándo |
|---|---|---|
| **Instituciones** | Alzado frontal, plano, a la altura de la calle | Banco central, ministerios, edificios con banderas |
| **Vida cotidiana** | Isométrica desde arriba, esquina a 3/4 | Calles, oficinas, gente, centros de datos |

```
FRONTAL:    straight-on frontal elevation, camera at street level, symmetrical composition, no perspective distortion
ISOMETRICA: high isometric three-quarter view looking down at about 40 degrees, clean orthogonal grid
```

El salto de una a otra marca que cambia el plano de la historia: de tu calle al
sitio donde se decide.

## Los elementos recurrentes

### LA CALLE — el dinero como lo vives tú

```
a grey concrete corner block, its ground floor a small bank branch with a
plain dark sign and one wall-mounted cash machine, apartments with iron
balconies and potted plants above, a green-awning grocery next door,
pedestrians and a cyclist on the pavement, parked cars at the kerb
```

Cámara **isométrica**. Es el plano de apertura y vuelve cada vez que la voz baja
al bolsillo del espectador: hipoteca, compra del mes, supermercado.

### EL BANCO CENTRAL — el tipo a corto

```
a massive grey stone neoclassical building with four fluted columns, three tall
dark green bronze doors, a wide stone staircase, a round brass emblem above the
central door, two ornate black street lamps flanking the steps, and the words
BANCO CENTRAL in gold capital letters carved across the frieze
```

Cámara **frontal**. Es el que la voz dice que **no** manda. Siempre idéntico:
mismas cuatro columnas, mismas tres puertas verdes, mismo emblema redondo.

### LOS MÁSTILES — los países

```
five tall brass flagpoles in a row on a stone plaza, flying the flags of the
United States, the United Kingdom, Japan and the European Union, in front of a
wide modern government building whose facade carries a large dark line chart
climbing steadily from bottom left to top right
```

Cámara **frontal**. La línea del gráfico sube siempre a la derecha, nunca baja,
y nunca lleva números.

### LA CÁMARA ACORAZADA — el ahorro disponible

```
a huge round brass and steel bank vault door standing open, its spoked wheel
turning outwards, revealing stacked bundles of banknotes inside
```

Sustituye al depósito de la versión metafórica. El **nivel de fajos** es lo que
cambia con el relato —llena en la década pasada, más vacía al final— pero la
puerta, los remaches y la rueda son siempre los mismos.

### EL MINISTERIO — los gobiernos

```
a white classical government building with a columned portico, a sculpted
pediment and gold-framed doors
```

Siempre a la **izquierda** del encuadre cuando comparte plano con el centro de
datos. Blanco, para distinguirlo del banco central, que es gris piedra.

### EL CENTRO DE DATOS — la inteligencia artificial

```
a modern glass-walled data centre with a flat dark roof, rows of black server
racks visible through the glass, small green and blue indicator lights blinking
inside
```

Siempre a la **derecha**. Cristal y negro, nunca piedra.

### LA COLA DEL ESTADO

```
a queue of figures in long grey coats, each carrying a stack of pale document
boxes
```

### LA COLA DE LA IA

```
a queue of figures in dark blue work overalls, each carrying a black server
rack unit under one arm
```

**Las dos colas nunca visten igual.** Gris con cajas de papel contra azul con
racks negros. Es lo que permite distinguirlas de un vistazo sin un solo rótulo,
y es la razón de que la imagen 4 del gancho se regenerara: en la primera versión
las dos colas iban vestidas igual y no se leía quién era quién.

## Cómo se compone un prompt

```
<EL MUNDO> + <LA CÁMARA> + <descripción literal de los elementos> + <qué hace la cámara o qué cambia>
```

El clip animado de un momento usa **exactamente las mismas frases** que la
imagen fija, cambiando solo lo que se mueve.

## Por qué esto arregla la coherencia entre clip e imagen

El clip hereda el aspecto de su `--start-image`. Pero en cuanto algo se mueve, el
modelo tiene que inventar lo que entra en cuadro — y sin la descripción literal,
inventa otro edificio.

## Regla

**Si un objeto sale más de una vez, entra en esta biblia antes de escribir
ninguna escena.** Añadirlo después obliga a regenerar todo lo anterior.

---

# Ampliación para el cuerpo (146 escenas)

## Regla de oro

**Lo que ya salió en el gancho no se toca.** El banco central tiene cuatro
columnas, tres puertas verdes y emblema redondo para siempre. La cámara
acorazada tiene su rueda de radios para siempre. Las colas visten como visten.
Los elementos nuevos de abajo quedan igual de congelados desde su primera
aparición.

## Banderas y logos

Cuando el guion nombra un país, aparece **su bandera real**, fiel: EE. UU.,
Reino Unido, Japón y la UE ya están establecidas en LOS MÁSTILES y se replican
idénticas. Alemania (cierre) con su tricolor real. Si un guion futuro nombra
una marca, su logo real, lo más fidedigno que el modelo permita.

## Elementos nuevos

### EL PARQUÉ — el mercado de deuda
```
a large open trading hall seen in high isometric view, rows of dark wooden
desks with small dark monitors, small anonymous figures at them, and on the
far wall one huge dark display board showing a single dark line chart
```
La línea del TABLÓN es el estado del mercado: hundida, plana o subiendo.

### LA SALA — donde se decide el tipo a corto
```
a grand interior room with tall windows, a long dark wooden table with
anonymous figures seated around it, and the round brass emblem of the central
bank mounted on the stone wall behind
```
El emblema es el mismo del frontispicio del BANCO CENTRAL.

### EL CAMINO — el largo plazo
```
a long straight empty road receding to the horizon across a flat plain, with
evenly spaced small stone milestones along its edge
```

### LA FÁBRICA — la inversión que retorna
```
a red brick factory with a single tall chimney and a sawtooth roof
```
En obras: `wrapped in wooden scaffolding, with a small crane beside it`.

### EL PISO — la hipoteca
```
a beige apartment building with iron balconies, and a large white sign with
the words SE VENDE in dark capital letters by its entrance
```

### LA IMPRENTA — imprimir dinero
```
a heavy dark green industrial printing press with brass fittings, feeding out
a long sheet of pale banknotes onto a roller table
```

### LA RUEDA — la espiral de la deuda
```
a large iron wheel mounted on a dark machine frame, with a leather belt
running from its rim back into its own axle
```
La voz dice literalmente «es una rueda que gira sola»: aquí es literal.

### EL DESPACHO — la factura de intereses
```
a wooden desk with a brass lamp inside a grand stone room, piled with tall
stacks of pale paper bills
```
La altura de las pilas es el estado de la factura.

### EL AGUJERO — el déficit
```
a dark round hole in a stone floor, with gold coins spilling over its edge and
falling inside
```

### LA BÁSCULA — el precio de prestar
```
an old brass balance scale on a dark wooden table
```

### EL SUPERMERCADO
Es **la tienda de toldo verde de LA CALLE**, la misma esquina del gancho. No se
inventa un supermercado nuevo.

## Gramática de efectos

Cada escena lleva uno de tres efectos, elegido por lo que dice la frase:

| Efecto | Cuándo |
|---|---|
| `in` (zoom lento hacia dentro) | La frase estrecha el foco: un problema, un detalle, una amenaza que crece |
| `out` (zoom lento hacia fuera) | La frase abre el plano: revelación, contexto, consecuencia grande |
| `fijo` | Afirmaciones y remates. Y **siempre** al abrir un bloque nuevo del argumento |

Reglas duras:

- **Nunca tres movimientos seguidos.** Después de dos `in`/`out`, toca `fijo`.
- Los pares de contraste (A contra B) van los dos `fijo`, mismo encuadre, para
  que el corte seco sea el que habla.
- Máximo 4 s por imagen. Entre 4,0 y 4,5 s se tolera solo con movimiento.
- Las líneas de menos de ~1,8 s se fusionan con su vecina **solo si forman un
  mismo pensamiento visual**; si son un remate, se quedan solas como corte seco.

## El montaje manda el audio

Las duraciones reales salen de `audio/cuerpo/tramos.json` (alineación carácter
a carácter de la voz clonada), no de las marcas escritas del guion. La media
real es 2,5 s por línea. El cuerpo dura 5:24; el vídeo completo, ~5:52.
