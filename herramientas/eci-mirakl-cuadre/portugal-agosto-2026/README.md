# Motivos del descuadre de la liquidación ECI de Portugal (agosto 2026)

Análisis del informe de BC «Liquidación mensual ECI» (líneas EDI de ECI frente a
tramos de Mirakl) para Portugal, con los PDF de liquidación de ECI, el export de
pedidos de Mirakl, el log del conector y el detalle de la comparación operativa de
BC. Los datos se quedan en `T:\Online\Oriol\ERP\BC\ECI` (llevan datos de clientes);
aquí solo los scripts.

- `reconstruccion_pt.py <scratchpad>`: reconstruye desde Mirakl cada línea EDI de
  agosto (venta finalizada, devolución, en proceso, rescisión), su centro y si BC
  la puede vincular, con las reglas comprobadas.
- `excel_motivos_pt.py <scratchpad> <salida.xlsx> <carpeta ECI>`: Excel de detalle
  (resumen por fila de BC con fórmulas, líneas reconstruidas, líneas identificadas
  con el detalle de BC, devoluciones en tienda con los mensajes R01-R03, comisión e
  IVA, preguntas para IT y ECI). Lee de la carpeta ECI el detalle de la comparación
  operativa exportado de BC (`detalle gaia.xlsx` = 0142/601, `detalle gaia 143.xlsx` =
  0143/601, `143 602.xlsx` = 0143/602), añade las 5 líneas que no salen de las reglas y
  comprueba que cada línea del detalle casa con una sola línea reconstruida. La hoja
  «PDF vs BC» la añade `hoja_pdf_vs_bc.py`: cada columna de los PDF de Portugal frente
  al campo de BC equivalente, con fórmulas.
- `resumen_liquidacion_bc.js <salida.pptx> <apply_theme.js de la skill pptx>`: presentación
  «RESUMEN LIQUIDACION BC» de 8 diapositivas (la primera, el cuadro PDF vs BC); necesita
  `npm install pptxgenjs` y NODE_PATH apuntando a ese node_modules.
- `informe_motivos_pt.js <salida.docx>`: informe Word de 8 páginas (la 2, apaisada, con el cuadro PDF vs BC) (`npm install docx`).

## Reglas de ECI comprobadas en Portugal

- Venta finalizada: recepción del mes, que normalmente es la fecha del talón de
  cumplimentación. Si la recepción se confirma después del cierre del día (31/08 a
  las 23:52), Mirakl fecha el talón al día siguiente pero ECI la liquida ese día.
  Las líneas rechazadas no cuentan aunque lleven el talón (va por pedido).
- Devolución: talón de abono del mes sobre una línea entregada y realmente
  devuelta, por las unidades devueltas, aunque Mirakl no haya reembolsado
  (Incidencia abierta). Las hermanas «Recibido» que comparten talón no cuentan.
- En proceso: pedidos del mes por fecha de cobro, con cierre de día hacia las
  23:30 hora peninsular. Rescisión: rechazadas y canceladas del mes y abonos o
  reembolsos de líneas nunca entregadas. Ninguna de las dos se liquida.
- Centro: venta, en proceso y rescisión van al centro del pedido (0143). La
  devolución va a la caja del abono: 4 primeros dígitos del talón (0247, 0257, 0358,
  0359, 0558-0561 Lisboa 0140; 0250, 0253, 0260, 0265, 0266, 0269, 0616, 0617 Gaia
  0142; 9xxxxxxx online).
- El PDF de ECI de Portugal solo trae 0143 y es la suma de 0140 + 0142 + 0143.

## Devoluciones en tienda: R01, R02 y R03

- R01, devolución en tienda: abono por TPV y talón de abono. ECI la liquida en ese
  mes. Mirakl abre una incidencia con reembolso 0 y BC ya puede crear la devolución.
- R02: la mercancía llega al almacén de MRW (en agosto, de 5 a 7 semanas después).
- R03: Toni Pons la recoge y Mirakl crea el reembolso (motivo REFUND_04, a la misma
  hora que la R03, por lotes en los días de recogida).

## Motivos encontrados

1. BC calcula la comisión al 29 % sobre el importe con IVA y el neto esperado con
   IVA; ECI la calcula sobre la neta sin el 23 % y se factura sin IVA: 807,22 € de
   neto de más en BC. En España BC usa 29 % en 696 y ECI 30 %.
2. Líneas sin vincular: ventas de pedidos anteriores al conector (01/06), una venta
   de un pedido del 15/06 sin talón de cumplimentación en el conector, y
   devoluciones de pedidos creados hasta el 28/06, que el conector dejó de actualizar.
3. Tramos sin procesar (siempre devoluciones, cuentan 0 en Mirakl): 4 devoluciones
   por 299,80 € que ECI abona y que no existen en Mirakl (3 líneas de un pedido
   devuelto en Gaia y 1 línea online). BC las vincula por el talón de venta y no
   puede crear el documento.
4. Devoluciones en tienda: BC las pone en 0140/0142 y ECI las liquida en 0143.
