# Cuadre ECI (Mirakl) vs Business Central

Script `cuadre_eci_bc.py`: cruza el log del conector Mirakl → Business Central
(las líneas de pedido que BC ha recibido de El Corte Inglés, con su estado de
proceso) contra el export de pedidos del portal de vendedor de ECI (Mirakl), y
genera un Excel en colores con las líneas y pedidos que coinciden, lo que BC ha
hecho con cada uno y las devoluciones. Es el hermano de
`channelengine-cuadre`, adaptado a que aquí todo va **por línea de pedido**.

La copia que se ejecuta vive en la carpeta de trabajo
`T:\Online\Oriol\ERP\BC\ECI` (con los datos, que no se suben aquí: llevan
nombres, direcciones y teléfonos de clientes). Esta es la copia versionada.

## Entradas

| Fichero | Contenido |
|---|---|
| `Mirakl Orders Import.xlsx` | log del conector BC: una fila por línea (`Mirakl Line Id`), con `Order ID`, `Created Date` (UTC), `Order State`, `Line State`, `SKU` (EAN), `Quantity`, `Total Price`, `Processing Status` (Processed / Error / Pending), `BC Sales Order No.`, `Error Message`, `Return Status`, `Return Processing Status`, `BC Return Order No.`, `Reason Code`, `Refund Id`, `Refund Amount`… |
| `pedidos <año>.xlsx` | export de pedidos de Mirakl (hoja `orders`): una fila por línea (`N.º de asiento de pedido`), `Número de pedido`, `Fecha de creación` (hora de Madrid), `Estado` (Recibido, Reembolsado, Incidencia abierta, Rechazado, Cancelado…), `Motivo`, `Importe`, reembolsos, comisiones, talones de ECI (venta, cumplimentación, abono, recogida), fechas de envío y entrega, y datos del cliente (que el script no copia) |

Clave de cruce: `N.º de asiento de pedido` = `Mirakl Line Id`
(`<pedido>-A-<n>`); el pedido es `Número de pedido` = `Order ID` (`<pedido>-A`).
`Created Date` del log viene en UTC y se pasa a hora de Madrid, que es como
exporta Mirakl; el propio número de pedido lleva la fecha local.

## Uso

```
python cuadre_eci_bc.py --bc "Mirakl Orders Import.xlsx" --mirakl "pedidos 2026.xlsx" --periodo 2026-08
```

`--periodo` (AAAA-MM) por defecto es el mes anterior al de la última línea del
log; `--salida` por defecto `Cuadre_ECI_vs_BC_<periodo>.xlsx` junto al log.
`CUADRAR.bat` en la carpeta de trabajo coge el `Mirakl Orders Import*.xlsx` y
el `pedidos*.xlsx` más recientes y ejecuta lo mismo. Leer el export (20 MB)
tarda cerca de un minuto.

Requiere `openpyxl` y `pandas` (3.x). Las fórmulas se calculan al abrir el
Excel (`fullCalcOnLoad`).

## Salida

| Hoja | Qué hay |
|---|---|
| `Resumen` | periodo, fechas de extracción de cada fuente, líneas/pedidos/importes, qué hizo BC (Processed / Error / Pending), resultado por categoría, devoluciones, y el log completo por mes |
| `Cruce líneas` | una fila por línea de pedido (unión del export y del log en el periodo). Columnas H en adelante son fórmulas sobre `Export Mirakl` y `Log BC`. Color por `Resultado`; `Devolución` en lila |
| `Cruce pedidos` | una fila por pedido, agregando `Cruce líneas` con fórmulas (líneas, importes, devueltas, nº pedido BC, `Resultado pedido`) |
| `Devoluciones` | líneas reembolsadas o con incidencia de devolución, con importe reembolsado, talón y fecha de abono y de recogida de ECI, datos del log BC y `Situación en BC` |
| `Export Mirakl` | export del periodo, solo columnas de negocio |
| `Log BC` | log del periodo, sin nombre del cliente, con los estados traducidos |

### Resultado (color de fila)

| Resultado | Color | Significa |
|---|---|---|
| Coincide: pedido BC creado | verde | en el export y BC creó el pedido (Processed) con el mismo importe |
| Coincide con diferencia de importe | amarillo | en ambos con pedido BC, importe distinto |
| Devolución con pedido BC (comprobar abono) | lila | reembolsada o con incidencia en Mirakl y BC había creado el pedido |
| Pendiente en BC (sin procesar) | amarillo claro | en el log con `Processing Status` = Pending: BC no ha creado nada |
| Error BC (sin pedido BC) | naranja claro | el conector falló (`Error Message`) |
| No es venta: cancelado / rechazado en Mirakl | azul claro | línea cancelada por el cliente o rechazada por la tienda |
| Revisar: pedido BC creado para línea cancelada/rechazada | ámbar | BC creó pedido de una línea que no es venta |
| Solo en export Mirakl (falta en el log BC) | naranja | el conector no la ha recibido |
| Solo en log BC (no está en el export) | rojo | en el log y no en el export |

## Lo que se vio en el primer cuadre (agosto 2026)

- Export y log coinciden línea a línea: 2.538 líneas, 2.203 pedidos,
  145.528,56 € en los dos, mismo EAN, cantidad y fecha.
- Todas las líneas de agosto están **Pending** en el log: BC no había creado
  ningún pedido de venta de ECI. En junio y julio el conector solo procesó 430
  líneas y falló en 4.685, casi todas por «Grupo registro cliente debe tener un
  valor en Cliente: Nº=C0001883», «No puede asignar números nuevos de la serie
  V-DEV» (devoluciones) y «missing SKU/barcode mapping».
- El log se extrajo el 1/9 y el export el 22/9, así que muchos estados han
  cambiado entre medias (Recibido → Reembolsado). La columna «Estado cambiado
  desde el log» lo marca.
- Devoluciones en Mirakl van por línea: `Reembolsado` con `Importe total
  reembolsado` (completo salvo líneas de 2 unidades con 1 devuelta),
  `Incidencia abierta` con motivo `Devolución` es una devolución en curso.
  ECI documenta cada paso con un talón (venta, cumplimentación, abono,
  recogida) que el export trae con su fecha.
