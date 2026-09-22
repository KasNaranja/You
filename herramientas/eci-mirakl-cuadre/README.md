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

## Cuadre de las liquidaciones de ECI con los pedidos

Script `cuadre_liquidacion_eci.py`: lee las liquidaciones «Explotaciones
directas» de un mes (los `.xlsx` de España con hoja `Data`, los `.XLS` de
Portugal, que son texto UTF-16 con tabuladores, y la subcarpeta `corners`) y
las cuadra con el export de Mirakl.

```
python cuadre_liquidacion_eci.py --mirakl "pedidos 2026.xlsx" --liquidaciones "8 - AGOST" --periodo 2026-08
```

Salida `Cuadre_liquidacion_ECI_<periodo>.xlsx` en la carpeta de liquidaciones:
`Resumen` (cada línea de liquidación frente a lo que sale de Mirakl, totales por
país y departamento, posibles causas de diferencia), `Líneas mes` (todas las
líneas de Mirakl con cumplimentación, abono o recogida en el mes, con su venta y
abono en liquidación por fórmula y una columna `Revisar`) y `Liquidación ECI`
(las líneas tal cual, con el nº de factura del fichero «total» si existe).

### Cómo liquida ECI (deducido con agosto 2026, 28 de 37 líneas al céntimo)

- Una línea de liquidación por **centro** y **departamento (UNECO)**. El centro
  va codificado en el número de pedido de Mirakl, posiciones 4 a 7: `0090` venta
  a distancia España, `0143` Portugal, `0005` Bilbao, `0011` Vigo… Las tiendas
  son pedidos hechos desde la tienda, no las recogidas en tienda.
- El departamento sale del producto: mujer o unisex → `0601`, hombre → `0602`,
  niños → `0696` (el script lo infiere de la descripción).
- **Venta bruta del mes** = importe de las líneas con `Fecha de cumplimentación`
  en el mes, menos el `Importe total reembolsado` de las líneas con `Fecha de
  abono 1` en el mes que tengan cumplimentación. Los reembolsos de líneas nunca
  entregadas no restan. Un centro con neto negativo sale en una «liquidación
  negativa» aparte (Vigo hombre, −45 € en agosto).
- Participación ECI 30 % en España (IVA 21 % en la factura) y 29 % en Portugal
  (IVA 23 % dentro de la venta, factura sin IVA). Los corners (UNECO 0598, 34 %)
  son venta física y no se cruzan; gastos de envío y gestión de espacios tampoco.

Quedó sin explicar en agosto: venta a distancia España +386 € sobre 71.103 €
(0,5 %), Valderas +65 € (devolución recogida en agosto y abonada en Mirakl en
septiembre) y Portugal +702 € sobre 6.006 €. La columna `Revisar` marca las
líneas candidatas.
