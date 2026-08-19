# Proceso de producción

Cómo se hace un vídeo del canal, en orden. Actualizado con los cambios del
vídeo 5.

## Los diez pasos

| # | Paso | Coste | Tiempo |
|---|---|---|---|
| 1 | **Guion** con marcas cada 3-5 s | 0 | ~2 h |
| 2 | **Verificar** nombres, cifras y fechas | 0 | — |
| 3 | **Biblia visual**: los objetos recurrentes, descritos una vez | 0 | ~20 min |
| 4 | **Escenas**: una por marca, usando la biblia literalmente | 0 | ~2 h |
| 5 | **Gancho**: audio de un tirón, y medir dónde cae cada frase | 0 | 5 min |
| 6 | **Clips** de los primeros 30 s, sembrados de sus imágenes | ~32 cr | 15 min |
| 7 | **Imágenes** del resto | ~140 cr | 15 min |
| 8 | **Voz** del cuerpo, calibrada a las marcas | 0 | 15 min |
| 9 | **Montaje**: clips + imágenes + voz | 0 | 12 min |
| 10 | **Miniaturas, título, descripción** y guardar en el repo | ~6 cr | — |

**Total: ~180 créditos y unas 5 horas**, de las que cuatro son escribir.

---

## Lo que cambió en el vídeo 5

### 1. El gancho ya no se corta

**Antes:** una locución por marca de tiempo, y silencio de relleno hasta la
siguiente. En el cuerpo del vídeo funciona, pero en el gancho se oían
micro-parones entre frases.

**Ahora:** el gancho se genera como **un solo bloque continuo** de edge-tts, sin
uniones. Los tiempos de cada frase se sacan de los subtítulos que emite el propio
motor:

```
python -m edge_tts --voice es-ES-AlvaroNeural --rate +15% --text "<gancho>" \
  --write-media hook.mp3 --write-subtitles hook.srt
```

El `.srt` da el segundo exacto en que arranca cada frase. **Las imágenes se atan
a esos tiempos**, no al revés.

Es la inversión importante del método: en el gancho manda el audio; en el cuerpo
sigue mandando el guion.

### 2. Los primeros 30 segundos van animados

Clips de Veo 3.1 Lite, uno por bloque de la narración, cada uno sembrado con
`--start-image` desde la imagen que ya existe para ese tramo.

**Nunca `--end-image`.** Fue lo que rompió la continuidad en el vídeo 2: obliga
al modelo a transformar un objeto en otro a mitad de plano.

Encadenar por fotograma puente solo si es **un plano continuo**. Si son escenas
distintas, corte normal.

### 3 y 4. La biblia visual

El cambio de fondo. Cada objeto que sale más de una vez se describe **una sola
vez, palabra por palabra**, en `produccion/biblia-visual.md`. Todas las escenas
que lo usen copian esa frase literal, sin reformular.

Incluye también una descripción del mundo —altura de cámara, luz, paleta, línea
de horizonte— que va delante de todos los prompts, en imágenes y en clips.

**Por qué arregla la coherencia entre clip e imagen:** el clip hereda el aspecto
de su `--start-image`, pero en cuanto la cámara se mueve el modelo tiene que
inventar lo que entra en cuadro. Sin la descripción literal, inventa otro objeto.
Con ella, lo que inventa se parece a lo que ya había.

**Regla:** si un objeto sale más de una vez, entra en la biblia **antes** de
escribir ninguna escena. Añadirlo después obliga a regenerar lo anterior.

### 5. Literal antes que metafórico

La primera versión del gancho del vídeo 5 era una metáfora —un depósito de acero
remachado lleno de monedas como «el ahorro del mundo»— y se descartó entera
después de gastar 36 créditos.

**Si la voz dice «banco central», se ve un banco central con su cartel.** Si dice
«Estados Unidos, Reino Unido, Japón y Europa», se ven cuatro mástiles con sus
banderas. La metáfora obliga al espectador a descifrar antes de entender, y en
los primeros segundos de un vídeo eso es exactamente lo que no hay tiempo de
hacer.

### 6. El modelo sí sabe escribir carteles

Regla derogada. Durante cinco vídeos los prompts llevaron «absolutely no text».
No hacía falta: `BANCO CENTRAL` y `SE VENDE` salieron perfectos a la primera.

**Condiciones:** mayúsculas, sin tildes, dos o tres palabras como mucho, y en un
sitio donde iría un rótulo de verdad —un friso, una fachada, un poste—. Nada de
párrafos, cifras ni etiquetas flotantes: ahí sigue fallando.

Esto abre rótulos de ministerio, nombres en mapas y etiquetas de eje.

### 7. Dos cámaras, y el cambio significa algo

| Escena | Cámara |
|---|---|
| Instituciones | Alzado frontal, a la altura de la calle |
| Vida cotidiana | Isométrica desde arriba, a 3/4 |

Alternarlas al azar parece de dos autores. Usarlas por tipo de escena convierte
el corte en argumento: cuando el vídeo pasa de tu calle al edificio donde se
decide, la cámara lo dice sin una palabra.

### 8. Cámara fija en todos los clips

```
The camera is completely locked off: no pan, no zoom, no push in, no parallax.
```

En cuanto Veo mueve la cámara tiene que inventar lo que entra en cuadro, y ahí
es donde se deforman los carteles y la arquitectura. Con la cámara clavada, solo
se mueve lo que se le pide: banderas, gente, luces.

---

## Las trampas, todas juntas

**Silencios** — el `.srt` de edge-tts marca frases, no pausas. Dentro de una
frase hay huecos mayores que entre dos. Para saber dónde cortar de verdad:

```
ffmpeg -i hook.mp3 -af "silencedetect=n=-40dB:d=0.15" -f null -
```

Y **edge-tts deja ~0,85 s de silencio al final**. Si no se corta con `-t`, el
gancho termina con casi un segundo de nada. Se nota.

**Escenas** — nada de ausencias ni negaciones. El pixel art dibuja muy bien lo
que hay; no puede dibujar «el camino que no tomaste». Cada escena es una relación
física entre objetos presentes.

**Cantidades** — nunca pedir números exactos. «Nueve de cada diez cuadrados» dio
ocho. Describir el concepto y dejar las cifras para la voz.

**Generación** — desde PowerShell, nunca desde Python. El proceso de Python no ve
el directorio global de npm donde vive la CLI.

**Revisión** — mirar el `index.txt`, no el número de imágenes. Así se descubrió
que 9 de 11 caían en el mismo minuto.

**Voz** — montar en WAV. Concatenar MP3 arrastra ~60 ms por unión: en 300 trozos
son 17 segundos de deriva, y no lo delata ningún error.

**Montaje** — `-shortest` obligatorio, o el vídeo dura más que el audio. Y CRF 14,
no 20: en color plano, un origen pobre hace que el reencodeo de YouTube saque
bandas alrededor de las líneas negras.

**Miniaturas** — generar a 1k, no a 2k. A 2k salen 1920×1088, que ni siquiera es
16:9 exacto, y superan el límite de 2 MB de YouTube.

---

## Las herramientas

```
herramientas/generar-imagenes.ps1   reanudable, no cobra dos veces
herramientas/generar-voz.py         calibrada a las marcas, montaje en WAV
herramientas/montar-video.py        specs de YouTube
```

Las tres son genéricas: reciben el fichero de escenas y las rutas por parámetro.
