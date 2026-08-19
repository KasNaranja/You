# Biblia visual — Vídeo 5

Los objetos que se repiten a lo largo del vídeo, descritos **una sola vez y
palabra por palabra**. Cada escena que use uno de estos elementos copia su
descripción literal, sin reformular.

Es lo que hace que las imágenes y los clips parezcan del mismo vídeo en vez de
140 dibujos sueltos. Sin esto, el modelo reinventa el depósito en cada plano.

## El mundo

Va delante de todo, en clips y en imágenes por igual:

```
A single continuous industrial world seen from a fixed low camera height, like a
side-on stage. Overcast grey daylight, no sun, no shadows on the ground. Muted
palette: concrete grey, steel blue, brass, dark green, warm coin gold. Same
horizon line in every shot.
```

## Los elementos recurrentes

### EL DEPÓSITO — el ahorro disponible

```
a huge riveted steel reservoir with a domed top and a brass rim, filled to the
brim with gold coins, with one single arched service window at its base
```

Es el protagonista. Aparece en el gancho, en el bloque de la década pasada, en
el de las dos colas y en el cierre. **Siempre el mismo**: mismos remaches, misma
ventanilla única, misma cúpula.

Su estado cambia, su forma no:
- Década pasada: lleno hasta arriba, ventanilla abierta, nadie delante
- Ahora: igual de lleno, pero con dos colas
- Cierre: el nivel de monedas más bajo

### LA COLA DE LA IA — el sector privado

```
a queue of figures in dark blue overalls, each carrying a black server rack unit
under one arm
```

Siempre de **azul oscuro** y siempre con el rack negro. Es lo que permite
distinguirla de la otra de un vistazo, sin rótulos.

### LA COLA DEL ESTADO — los gobiernos

```
a queue of figures in long grey coats, each carrying a stack of paper document
boxes
```

Siempre de **gris** y siempre con las cajas de papel.

### EL BANCO CENTRAL

```
a small stone building with four columns and a large brass lever mounted on its
front wall
```

La palanca es la clave: es lo que se baja mientras el dial sube.

### EL DIAL DEL MERCADO

```
a large round brass gauge on a steel post, with a single black needle
```

Nunca lleva números —el prompt prohíbe texto— así que lo que comunica es la
**posición de la aguja**: abajo a la izquierda o arriba a la derecha.

### LA RUEDA — la espiral de la deuda

```
a large iron wheel on a machine frame, with a leather belt running from its rim
back into its own axle
```

## Cómo se usa

En cada escena, el prompt se compone así:

```
<EL MUNDO> + <descripción literal de los elementos que salen> + <qué hace la cámara o qué cambia>
```

Ejemplo real de una escena:

> A single continuous industrial world seen from a fixed low camera height…
> **a huge riveted steel reservoir with a domed top and a brass rim, filled to the
> brim with gold coins, with one single arched service window at its base**, with
> nobody standing at the window and empty floor in front of it.

Y el clip animado del mismo momento usa **exactamente la misma frase** para el
depósito, cambiando solo lo que se mueve.

## Por qué esto arregla la coherencia entre clip e imagen

El clip se genera desde la imagen como `--start-image`, así que hereda su
aspecto. Pero en cuanto la cámara se mueve, el modelo tiene que inventar lo que
entra en cuadro — y sin la descripción literal, inventa otro depósito.

Con la biblia, lo que inventa se parece a lo que ya había.

## Regla

**Si un objeto sale más de una vez, entra en esta biblia antes de escribir
ninguna escena.** Añadirlo después obliga a regenerar todo lo anterior.
