# Pantalla de cierre del canal

**La elegida: `6-engranaje.png`** — el engranaje es el nombre del canal (El
Mundo en Piezas) haciendo de botón de suscripción.

Diseñada para el layout de pantallas finales de YouTube «1 vídeo + 1 botón de
suscripción»:

| Zona | Elemento | Qué superpone YouTube |
|---|---|---|
| Izquierda | Marco dorado rectangular 16:9, interior gris plano | El vídeo recomendado |
| Derecha | El hueco del engranaje, interior gris plano | El botón redondo del canal |
| Arriba | SUSCRIBETE en rojo con campana y flecha | — |

## Cómo se usa en cada vídeo

1. Copiarla como imagen de la última marca del guion (`imagenes/<marca>.png`)
2. Darle **~8 s en pantalla**: la voz acaba y la imagen aguanta con cola de
   silencio (`apad=pad_dur=6` sobre la voz). Menos de 5 s no da tiempo a clicar
3. Efecto `fijo` — nada de zoom sobre la plantilla
4. En YouTube Studio, colocar los elementos de pantalla final sobre los huecos

## Las descartadas

`1-boton`, `2-friso`, `3-palanca`, `4-camara`, `5-final`, `7-moneda`,
`8-marco` — se guardan por si algún día se quiere variar. La 8 salió con el
letrero duplicado.
