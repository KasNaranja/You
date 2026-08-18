# Qué hay que respaldar a mano

Dos cosas del canal **no están en GitHub** y se pierden si borras la carpeta o
cambias de máquina.

| Qué | Dónde | Si se pierde |
|---|---|---|
| Los `.mp4` montados | `Video N/video.mp4` | Se remonta **gratis** en 12 min |
| Las imágenes generadas | `Video N/imagenes/` | Se regeneran, pero **cuestan créditos** |

La diferencia importa: perder un montaje es perder tiempo; perder las imágenes
es perder dinero. Unos 145 créditos por vídeo.

## Qué copiar

```
C:\Users\oriol\You\mundo en piezas\Video 1\imagenes\    54 MB
C:\Users\oriol\You\mundo en piezas\Video 2\imagenes\   170 MB
C:\Users\oriol\You\mundo en piezas\Video 4\imagenes\   156 MB
C:\Users\oriol\You\mundo en piezas\Video 1\video.mp4    47 MB
C:\Users\oriol\You\mundo en piezas\Video 2\video.mp4   213 MB
C:\Users\oriol\You\mundo en piezas\Video 4\video.mp4   181 MB
```

Un disco externo o cualquier nube sirve. Lo que no vale es dejarlo solo aquí.

## Qué sí está a salvo en GitHub

Todo lo que no se puede regenerar automáticamente: los guiones, las escenas, los
prompts exactos, las miniaturas, los textos de publicación, los estilos y las
herramientas. Eso es el trabajo de verdad.

## Cómo regenerar las imágenes si hiciera falta

```
powershell -File herramientas\generar-imagenes.ps1 ^
  -Plan "mundo en piezas\Video 4\produccion\plan.json" ^
  -Destino "mundo en piezas\Video 4\imagenes"
```

Salta las que ya existan, así que también sirve para completar una carpeta a
medias. Cuesta un crédito por imagen.

Ojo: no saldrán idénticas. La generación no es determinista, así que un vídeo
remontado con imágenes regeneradas **no será el mismo vídeo**. Por eso conviene
la copia, y no confiar en poder rehacerlas.
