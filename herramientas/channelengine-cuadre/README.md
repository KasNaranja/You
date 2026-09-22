# Cuadre ChannelEngine vs Business Central

Script `cuadre_ce_bc.py`: cruza el log de la integración ChannelEngine → Business
Central (los pedidos que BC ha recibido de CE en un mes, con su estado de proceso)
contra el informe de pedidos descargado del backoffice de ChannelEngine, y genera
un Excel en colores con los pedidos que coinciden, los que faltan en un lado o en
otro y las devoluciones.

La copia que se ejecuta vive en la carpeta de trabajo
`T:\Online\Oriol\ERP\BC\Channel Engine` (con los datos, que no se suben aquí:
llevan nombres y direcciones de clientes). Esta es la copia versionada.

## Entradas

| Fichero | Contenido |
|---|---|
| `Cruce_pedidos_ChannelEngine_<mes>.xlsx` | log de BC, hoja `Cruce pedidos`: una fila por pedido con `Channel Order No`, `Merchant Order No`, `Marketplace`, `Estado CE`, `Fecha pedido` (UTC), `Total BC`, `Estado proceso BC` (Processed / Error / Skipped), `Error BC`, `Nº pedido BC` |
| `orders-report-<guid>.csv` | export de pedidos de ChannelEngine (Orders → Export). Separador `;`, primera línea `sep=;`, **una fila por línea de pedido**, con las columnas `Order.*`, `Line.*`, `Return.*`, `Shipment.*` |

Clave de cruce: `Channel Order No` (Bol.com `C000…`, About You `ayou-139-…`),
que está siempre relleno en los dos lados. `Merchant Order No` solo lo traen
los pedidos de Bol.com.

Las fechas del export vienen con zona horaria (About You `+00:00`, Bol.com
`+02:00`); el script las pasa a UTC, que es como las guarda el log de BC.

## Uso

```
python cuadre_ce_bc.py --bc "Cruce_pedidos_ChannelEngine_agosto_2026.xlsx" --ce "orders-report-xxx.csv" --periodo 2026-08
```

`--periodo` (AAAA-MM) por defecto es el mes del primer pedido del log BC;
`--salida` por defecto `Cuadre_CE_vs_BC_<periodo>.xlsx` junto al log.
`CUADRAR.bat` en la carpeta de trabajo coge el `Cruce_pedidos_*.xlsx` y el
`orders-report-*.csv` más recientes de la carpeta y ejecuta lo mismo.

Requiere `openpyxl` y `pandas` (3.x). Las fórmulas se calculan al abrir el
Excel (`fullCalcOnLoad`), así que no hace falta recalcular a mano.

## Salida

| Hoja | Qué hay |
|---|---|
| `Resumen` | parámetros (periodo, cobertura del export), aviso si el export no cubre el mes, contadores y importes por resultado y de devoluciones, leyenda de colores |
| `Cruce pedidos` | una fila por pedido (unión del log BC y del export CE dentro del periodo). Columnas E en adelante son fórmulas sobre `Pedidos CE` y `Log BC`. Color de fila por `Resultado`; la columna `Devolución` se marca en lila |
| `Devoluciones` | pedidos con `Devolución` = Sí / Parcial / Posible, con nº de devolución, motivo y líneas devueltas del export, y `Situación` (con pedido BC → comprobar abono; omitido; error) |
| `Pedidos CE` | export agregado a nivel pedido (total, líneas, devoluciones) |
| `Líneas CE` | líneas del export, solo columnas de negocio (sin datos personales) |
| `Log BC` | el log de BC tal cual |

### Resultado (color de fila)

| Resultado | Color | Significa |
|---|---|---|
| Coincide | verde | en el export CE y BC creó el pedido con el mismo importe |
| Coincide con diferencia de importe | amarillo | en ambos, total BC ≠ total CE |
| Devolución con pedido BC | lila | CE lo da como devuelto (RETURNED, o CLOSED con líneas devueltas) y BC había creado el pedido: comprobar abono/devolución en BC |
| Devolución omitida en BC (sin pedido) | azul claro | CE lo da como devuelto y BC lo omitió (ya estaba RETURNED al procesarlo) |
| Omitido en BC (sin pedido) | azul claro | BC lo omitió por estado CLOSED / MANCO |
| Error BC (sin pedido BC) | naranja claro | está en CE pero BC no pudo crear el pedido (p. ej. `Order has product mapping errors`) |
| Solo en CE (falta en BC) | naranja | en el export CE y no en el log BC |
| Solo en BC (no está en el export CE) | rojo | en el log BC, con fecha dentro de la cobertura del export, pero el export no lo trae |
| Sin datos CE (anterior al export) | gris | pedido BC anterior al primer pedido del export: no comprobable con ese export |

## Ojo con el export de ChannelEngine

El informe de pedidos de CE se descarga con el filtro de fechas que tenga la
pantalla de Orders en ese momento, y ese filtro va por **fecha de creación en
CE**, no por fecha de pedido. Un export "por defecto" trae las últimas semanas
(en el primer cuadre de agosto 2026 el CSV empezaba el 31/08 de creación,
25/08 de fecha de pedido). Antes de cuadrar un mes, filtrar en CE por fecha de
pedido del 1 al último día del mes; la celda `Export CE: primera fecha de
creación en CE` del Resumen delata el problema.

En el export, `Order.Status = CLOSED` con `Return.Id` en alguna línea es una
devolución parcial (una línea devuelta y otra no). `RETURNED` es devolución
completa. `Line.RefundAmount*` viene siempre vacío; el importe devuelto se toma
de `Line.LineTotalInclVat` de las líneas con `Return.Id`.
