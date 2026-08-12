# Ficha de producción — Vídeo 1

**La isla del tamaño de Andalucía que decide el precio de tu móvil**

Primer vídeo producido del canal. Sin publicar en el momento de archivarlo.

El guion y su registro editorial están en `../guion.md`; el plan de generación
previo, en `../prompt-imagenes.md`. Aquí queda lo que se ejecutó de verdad, que
difiere del plan: salieron **145 imágenes**, no las ~165 previstas.

- **Duración:** 8:32 (511,81 s)
- **Formato:** 1920×1080, 30 fps, H.264 + AAC 192k
- **Imágenes:** 145, una por cada timestamp del guion
- **Voz:** edge-tts `es-ES-AlvaroNeural`, calibrada y masterizada a −16 LUFS
- **Producido:** 2026-08-12

## Qué hay aquí

```
../video.mp4              el vídeo montado, listo para subir
../audio/voz.mp3          la voz sola, por si hay que remontar
../imagenes/              las 145, nombradas por su marca de tiempo
    index.txt             imagen → segundo → frase que suena
../miniaturas/
    A-recomendada.png     la buena: círculo rojo sobre el este de Asia
    B-alternativa.png     más limpia, pero la flecha va al revés que la historia
    C-descartada.png      el círculo caía sobre Oriente Medio
  escenas.txt             qué se dibuja en cada marca de tiempo
  prompts.json            los 135 prompts exactos, para regenerar cualquiera
../publicacion/
    titulo.txt            título elegido, alternativas y por qué
    descripcion.txt       descripción con capítulos, lista para pegar
```

## Sincronía

Cada frase arranca en el segundo que dice el guion. **Desviación máxima medida:
0,003 s** en todo el vídeo.

No salió a la primera. Concatenar 289 MP3 con copia directa arrastra unos 60 ms
de relleno del codificador en cada unión: 17 segundos de deriva acumulada, con
cada frase llegando más tarde que la anterior. No lo delata ningún error — el
fichero se genera y suena bien. Solo salta comparando la duración total con la
esperada. Se arregló montando en WAV, que no tiene ese relleno.

## Cómo se hizo

1. **Imágenes** — FLUX.2 `pro`, 16:9, 1k, vía CLI de Higgsfield. Estilo de
   dibujo cutre de MS Paint: contorno negro grueso, colores planos, monigotes.
   El prompt prohíbe texto explícitamente, porque el modelo se inventaba
   palabras.
2. **Voz** — edge-tts, gratis y sin clave. Se recorta el silencio propio de
   cada clip (~0,23 s delante, ~0,85 s detrás) y se calibra la velocidad línea
   a línea hasta que cabe en su hueco. Solo 4 de las 145 hubo que acelerar.
3. **Montaje** — ffmpeg. Cada imagen dura lo que el guion asigna a su frase.

## Coste

| | |
|---|---|
| 145 imágenes | 136 créditos |
| 3 miniaturas (2k, 1,5 c/u) | 4,5 créditos |
| Voz y montaje | 0 € |
| **Total** | **140,5 créditos** |

Plan Plus de Higgsfield. Las miniaturas a 2k cuestan 1,5 en vez de 1: conviene
saberlo antes de generarlas en tandas.

## Pendiente

- Revisar las 145 imágenes una a una. Están verificadas en número y sincronía,
  no en calidad artística. En una tanda previa salió un 22% con defectos —texto
  inventado, cantidades mal contadas—, y aunque el prompt se endureció después,
  no se ha comprobado imagen por imagen.
- Añadir el texto a la miniatura A. Propuesta: **EL 90% SALE DE AQUÍ**, arriba a
  la izquierda, negro grueso sobre el cian.
- Rotular los tres actos en pantalla. La estructura está en el guion pero no se
  señaliza.
