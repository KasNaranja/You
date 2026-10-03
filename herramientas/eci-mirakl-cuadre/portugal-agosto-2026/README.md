# Motivos del descuadre de la liquidación ECI de Portugal (agosto 2026)

Análisis del informe de BC «Liquidación mensual ECI» (líneas EDI de ECI frente a
tramos de Mirakl) para Portugal, con los PDF de liquidación de ECI, el export de
pedidos de Mirakl y el log del conector. Los datos se quedan en
`T:\Online\Oriol\ERP\BC\ECI` (llevan datos de clientes); aquí solo los scripts.

- `reconstruccion_pt.py <scratchpad>`: reconstruye desde Mirakl cada línea EDI de
  agosto (venta finalizada, devolución, en proceso, rescisión), su centro y si BC
  la puede vincular, con las reglas comprobadas.
- `excel_motivos_pt.py <scratchpad> <salida.xlsx>`: Excel de detalle (resumen por
  fila de BC con fórmulas, líneas reconstruidas, pendientes, comisión e IVA,
  preguntas para IT y ECI).
- `informe_motivos_pt.js <salida.docx>`: informe Word de 7 páginas (`npm install docx`).

## Reglas de ECI comprobadas en Portugal

- Venta finalizada: talón de cumplimentación del mes; las líneas rechazadas no
  cuentan aunque lleven el talón (va por pedido).
- Devolución: talón de abono del mes sobre una línea entregada y realmente
  devuelta, por las unidades devueltas, aunque Mirakl no haya reembolsado
  (Incidencia abierta). Las hermanas «Recibido» que comparten talón no cuentan.
- En proceso: pedidos del mes por fecha de cobro, con cierre de día hacia las
  23:30 hora peninsular. Rescisión: rechazadas y canceladas del mes y abonos o
  reembolsos de líneas nunca entregadas. Ninguna de las dos se liquida.
- Centro: venta, en proceso y rescisión van al centro del pedido (0143). La
  devolución va a la caja del abono: 4 primeros dígitos del talón (0247, 0359,
  0558-0561 Lisboa 0140; 0260, 0265, 0266, 0269, 0617 Gaia 0142; 9xxxxxxx online).
- El PDF de ECI de Portugal solo trae 0143 y es la suma de 0140 + 0142 + 0143.

## Motivos encontrados

1. BC calcula la comisión al 29 % sobre el importe con IVA y el neto esperado con
   IVA; ECI la calcula sobre la neta sin el 23 % y se factura sin IVA: 807,22 € de
   neto de más en BC. En España BC usa 29 % en 696 y ECI 30 %.
2. Líneas sin vincular: ventas de pedidos anteriores al conector (01/06) y
   devoluciones de pedidos creados hasta el 28/06, que el conector dejó de actualizar.
3. Tramos sin procesar (siempre devoluciones, cuentan 0 en Mirakl): 4 devoluciones
   por 299,80 € que ECI liquida en agosto sin abono de agosto en Mirakl.
4. Devoluciones en tienda: BC las pone en 0140/0142 y ECI las liquida en 0143.
