const fs = require('fs');
const { Document, Packer, Paragraph, TextRun, HeadingLevel, Table, TableRow, TableCell, WidthType, AlignmentType,
        BorderStyle, ShadingType, LevelFormat, PageNumber, Footer, VerticalAlign, TableLayoutType, PageBreak } = require('docx');

const OUT = process.argv[2];
const AZUL = '1F4E78', GRIS = 'F2F2F2', BORDE = 'BFBFBF', font = 'Arial';
const b = { style: BorderStyle.SINGLE, size: 4, color: BORDE };
const borders = { top: b, bottom: b, left: b, right: b };
const W1 = 2900, W2 = 6738, W = W1 + W2;

const run = (text, o = {}) => new TextRun({ text, font, size: 20, ...o });
const par = (children, o = {}) => new Paragraph({ spacing: { after: 120, line: 276 }, ...o,
  children: Array.isArray(children) ? children : [run(children)] });
const cp = (children, size = 20) => new Paragraph({ spacing: { after: 0 },
  children: Array.isArray(children) ? children : [run(children, { size })] });
const cell = (children, width, o = {}) => new TableCell({
  width: { size: width, type: WidthType.DXA }, borders, verticalAlign: VerticalAlign.CENTER,
  margins: { top: 40, bottom: 40, left: 80, right: 80 }, ...o, children });
const shade = (fill) => ({ type: ShadingType.CLEAR, fill, color: 'auto' });

function kvTable(title, rows) {
  return new Table({
    width: { size: W, type: WidthType.DXA }, columnWidths: [W1, W2], layout: TableLayoutType.FIXED,
    rows: [
      new TableRow({ tableHeader: true, children: [
        cell([cp([run(title, { bold: true, color: 'FFFFFF' })])], W, { columnSpan: 2, shading: shade(AZUL) }) ] }),
      ...rows.map(([k, v]) => new TableRow({ children: [
        cell([cp([run(k, { bold: true })])], W1, { shading: shade(GRIS) }),
        cell([cp(typeof v === 'string' ? [run(v)] : v)], W2) ] })),
    ],
  });
}
// tabla con cabecera de columnas; rows = arrays de string (o de TextRun[]); size en medios puntos
function gridTable(headers, rows, widths, size = 18, margins = { top: 30, bottom: 30, left: 60, right: 60 }) {
  const total = widths.reduce((a, c) => a + c, 0);
  const mk = (v, w, o = {}) => new TableCell({ width: { size: w, type: WidthType.DXA }, borders, margins, verticalAlign: VerticalAlign.CENTER, ...o,
    children: [new Paragraph({ spacing: { after: 0 }, children: typeof v === 'string' ? [run(v, { size, ...(o.runOpts || {}) })] : v })] });
  return new Table({
    width: { size: total, type: WidthType.DXA }, columnWidths: widths, layout: TableLayoutType.FIXED,
    rows: [
      new TableRow({ tableHeader: true, children: headers.map((h, i) => mk(h, widths[i], { shading: shade(AZUL), runOpts: { bold: true, color: 'FFFFFF' } })) }),
      ...rows.map((r) => new TableRow({ children: r.map((v, i) => mk(v, widths[i])) })),
    ],
  });
}
const numbered = (ref) => (t) => new Paragraph({ numbering: { reference: ref, level: 0 }, spacing: { after: 40, line: 276 },
  children: Array.isArray(t) ? t : [run(t)] });
const bullet = (t) => new Paragraph({ numbering: { reference: 'vinetas', level: 0 }, spacing: { after: 40, line: 276 },
  children: Array.isArray(t) ? t : [run(t)] });
const h1 = (t, brk = false) => new Paragraph({ heading: HeadingLevel.HEADING_1, pageBreakBefore: brk, children: [run(t, { size: 28, bold: true, color: AZUL })] });
const h2 = (t) => new Paragraph({ heading: HeadingLevel.HEADING_2, children: [run(t, { size: 22, bold: true, color: AZUL })] });
const h1P = (t) => h1(t, true);  // título de sección que empieza en página nueva
const sep = () => par('', { spacing: { after: 80 } });
const B = (t) => run(t, { bold: true });

// ---------------------------------------------------------------- datos página 3: los 27 SKU sin mapear
const SKUS = [
  ['DAGO-TC_GRIS_46', '8434530794009', 'aygr-686-393050126', 'About You', '11/08', '68,26'],
  ['DALLAS_MARI_43', '8434530221802', 'aybn-558-395147727', 'About You', '25/08', '69,95'],
  ['DALLAS_MARI_47', '8434530221840', 'ayou-139-395093168', 'About You', '24/08', '69,95'],
  ['DALLAS_TORRAT_42', '8434530242210', 'aysk-586-392893487', 'About You', '10/08', '68,81'],
  ['DUSTIN_MARI_43', '8434530793453', 'aybn-558-395048796', 'About You', '24/08', '74,95'],
  ['ELLA_LAVANDA_39', '8434530856400', 'aygr-686-393429937', 'About You', '14/08', '73,13'],
  ['ETNA_CUIRO_39', '8434530002265', 'ayou-139-391594818', 'About You', '04/08', '74,95'],
  ['ETNA_PLATI_37', '8434530002203', 'ayro-594-395383279', 'About You', '30/08', '75,06'],
  ['LAILA-P_BLANC_34', '8434530718753', 'C000D03LH5', 'Bol.com', '14/08', '95,00'],
  ['MINO_MARI_43', '8434530867147', 'C000CHM40K', 'Bol.com', '05/08', '89,95'],
  ['MONTGRI_CAQUI_39', '8434530024762', 'aypt-685-392025384', 'About You', '02/08', '58,98'],
  ['MONTGRI_CRU_46', '8434530025097', 'ayro-594-392447554', 'About You', '06/08', '60,04'],
  ['MONTGRI_MARI_39', '8434530024755', 'aypt-685-392025384', 'About You', '02/08', '58,98'],
  ['MONTGRI_MARI_40', '8434530024809', 'aypl-550-392074229', 'About You', '03/08', '60,13'],
  ['MONTGRI_MARI_43', '8434530024953', 'ayse-655-392011378', 'About You', '02/08', '58,59'],
  ['MONTGRI_MARI_44', '8434530025004', 'ayou-139-393564735', 'About You', '15/08', '59,95'],
  ['MONTGRI_MARI_45', '8434530025059', 'ayou-139-393564735', 'About You', '15/08', '59,95'],
  ['MONTGRI_TEXA_40', '8434530721029', 'aypl-550-392074229', 'About You', '03/08', '60,13'],
  ['MONZA-A_MENTA_41 *', '8434530578494', 'C000CW0N43', 'Bol.com', '12/08', '99,95'],
  ['MOSUL-BD_PEDRA_37', '8434530534674', 'ayou-139-392990813', 'About You', '11/08', '44,95'],
  ['MOSUL-BD_PEDRA_38', '8434530534681', 'ayou-139-394502060', 'About You', '21/08', '44,95'],
  ['MOSUL-BD_PEDRA_42', '8434530534728', 'aysi-617-395295539', 'About You', '26/08', '44,58'],
  ['NEO-FR_MARI_43', '8434530535701', 'ayou-139-394846561', 'About You', '23/08', '44,95'],
  ['NIL-UM_MARI_45', '8434530425668', 'C000DMH45T', 'Bol.com', '29/08', '55,00'],
  ['SIDNEY_NATURAL_41', '8434530788398', 'C000CW0N43', 'Bol.com', '12/08', '119,95'],
  ['VERDI-V_MARI_39', '8434530216334', 'ayou-139-395027866', 'About You', '24/08', '74,95'],
  ['VERDI-V_MARI_41', '8434530216358', 'ayou-139-394468095', 'About You', '21/08', '74,95'],
];

// la lista de 27 SKU en dos columnas (14 + 13 filas)
const S3 = SKUS.map((r) => [r[0], r[1], r[2]]);
const mitad = Math.ceil(S3.length / 2);
const SKUS2 = [];
for (let i = 0; i < mitad; i++) SKUS2.push([...S3[i], ...(S3[i + mitad] || ['', '', ''])]);

const numCfg = (ref) => ({ reference: ref, levels: [{ level: 0, format: LevelFormat.DECIMAL, text: '%1.', alignment: AlignmentType.START,
  style: { paragraph: { indent: { left: 500, hanging: 300 } } } }] });

const doc = new Document({
  creator: 'Oriol Terradas', title: 'Errores conector Channel Engine',
  styles: {
    default: { document: { run: { font, size: 20 } } },
    paragraphStyles: [
      { id: 'Title', name: 'Title', basedOn: 'Normal', next: 'Normal', run: { font, size: 44, bold: true, color: AZUL }, paragraph: { spacing: { after: 40 } } },
      { id: 'Heading1', name: 'Heading 1', basedOn: 'Normal', next: 'Normal', quickFormat: true, run: { font, size: 28, bold: true, color: AZUL }, paragraph: { spacing: { before: 240, after: 120 }, outlineLevel: 0 } },
      { id: 'Heading2', name: 'Heading 2', basedOn: 'Normal', next: 'Normal', quickFormat: true, run: { font, size: 22, bold: true, color: AZUL }, paragraph: { spacing: { before: 200, after: 80 }, outlineLevel: 1 } },
    ],
  },
  numbering: { config: [
    numCfg('pasos1'), numCfg('pasos2'), numCfg('pasos4'), numCfg('pasos5'),
    { reference: 'vinetas', levels: [{ level: 0, format: LevelFormat.BULLET, text: '•', alignment: AlignmentType.START,
      style: { paragraph: { indent: { left: 500, hanging: 300 } } } }] },
  ] },
  sections: [{
    properties: { page: { margin: { top: 1134, bottom: 1134, left: 1134, right: 1134 } } },
    footers: { default: new Footer({ children: [new Paragraph({ alignment: AlignmentType.RIGHT, children: [
      run('Errores conector Channel Engine · página ', { size: 16, color: '808080' }),
      new TextRun({ children: [PageNumber.CURRENT], font, size: 16, color: '808080' }) ] })] }) },
    children: [
      // ======================================================================= página 1
      new Paragraph({ heading: HeadingLevel.TITLE, children: [run('Errores conector Channel Engine', { size: 44, bold: true, color: AZUL })] }),
      par([run('Integración ChannelEngine → Business Central (UATS TONIPONS) · cuadre de agosto de 2026 · 22/09/2026', { size: 18, color: '595959' })], { spacing: { after: 200 } }),

      h1('1. Pedido descartado por su estado en Channel Engine'),
      par('El conector solo crea pedidos de venta en Business Central para pedidos que están en un estado procesable en Channel Engine. ' +
          'Si en el momento de procesarlo el pedido ya figura como RETURNED, CLOSED, MANCO o CANCELED, el conector lo descarta (estado de proceso «Skipped») y no crea nada en BC. ' +
          'En agosto de 2026 ha pasado con 22 pedidos por 1.985,84 €: 19 ya devueltos (18 de About You y 1 de Bol.com) y 3 cancelados de Bol.com (MANCO en el log, CANCELED ahora en CE).'),

      h2('Ejemplo: pedido aynl-545-396292446 (About You NL)'),
      kvTable('Datos del pedido en Channel Engine (export orders-report, horas en UTC)', [
        ['Channel Order No', 'aynl-545-396292446   (Id CE 4028, sin Merchant Order No)'],
        ['Marketplace', 'About You (Dropshipment), tienda ABOUT YOU [NL]'],
        ['Fecha de pedido', '31/08/2026 18:48'],
        ['Fecha de envío', '01/09/2026 14:34, desde el stock «About You (FbAY) AKU-115-OfferableStock» (origen DE, destino NL)'],
        ['Alta en Channel Engine', '03/09/2026 00:49 (importación nocturna de About You, 2,3 días después del pedido)'],
        ['Cierre en Channel Engine', '03/09/2026 00:49, el mismo segundo que el alta'],
        ['Estado en Channel Engine', [B('RETURNED')]],
        ['Línea', 'VERDI-V_CRU_40 · EAN 8434530369818 · Espadrilles · 1 unidad'],
        ['Importe', '74,95 € IVA incluido (61,94 € + 13,01 € de IVA al 21 %) · gastos de envío 0,00 €'],
        ['Devolución', 'RET-1415710880 (id 2395) · motivo OTHER · «Returned to About You - no return reason info known»'],
      ]),
      sep(),
      kvTable('Qué hizo Business Central (log del conector)', [
        ['Estado del proceso', [B('Skipped')]],
        ['Mensaje del conector', [run('«Skipped because ChannelEngine status RETURNED is not processable for BC sales order creation.»', { italics: true })]],
        ['Nº de pedido BC', 'Ninguno: no se creó pedido de venta'],
        ['Importe registrado en el log', '74,95 € (coincide con Channel Engine)'],
      ]),

      h2('Cronología'),
      numbered('pasos1')('31/08 18:48 — el cliente hace el pedido en About You Países Bajos.'),
      numbered('pasos1')('01/09 14:34 — About You lo envía desde su propio stock (FbAY); Toni Pons no interviene en el envío.'),
      numbered('pasos1')('Entre el 01/09 y el 03/09 — el cliente lo devuelve a About You.'),
      numbered('pasos1')('03/09 00:49 — la importación nocturna lo da de alta en Channel Engine ya en estado RETURNED (alta y cierre en el mismo segundo).'),
      numbered('pasos1')('Business Central lo lee, ve el estado RETURNED y lo descarta: no crea pedido de venta ni abono.'),

      h2('Consecuencia'),
      par('Ni la venta de 74,95 € ni su devolución existen en Business Central. El efecto neto es cero y por eso el conector lo trata así por diseño, ' +
          'pero la operación no queda registrada. Los pedidos de About You entran en Channel Engine entre 1 y 12 días después de la fecha de pedido, ' +
          'así que cualquiera devuelto en ese plazo llega ya como RETURNED y se descarta. Si se quiere que estas ventas devueltas consten en BC (venta más abono), ' +
          'hay que cambiar la regla del conector, no corregir pedido a pedido. Los 22 casos de agosto están en la hoja «Cruce pedidos» del cuadre, en azul claro.'),

      // ======================================================================= página 2
      h1P('2. Pedido CLOSED con devolución parcial descartado entero'),
      par('En Channel Engine, CLOSED es el estado final de un pedido cuyas líneas han acabado en estados distintos. En agosto los 20 pedidos CLOSED del export ' +
          'tienen una línea devuelta y otra que el cliente se ha quedado. El conector trata CLOSED como no procesable, igual que RETURNED: si el pedido ya está CLOSED ' +
          'cuando BC lo lee, se descarta entero, y con él la venta de la línea entregada. De los 20, 18 tienen pedido en BC porque aún estaban SHIPPED al procesarlos, ' +
          '1 falló por mapeo de producto y 1, este, se descartó.'),

      h2('Ejemplo: pedido ayat-200-394497726 (About You AT)'),
      kvTable('Datos del pedido en Channel Engine (export orders-report, horas en UTC)', [
        ['Channel Order No', 'ayat-200-394497726   (Id CE 3918)'],
        ['Marketplace', 'About You (Dropshipment), tienda ABOUT YOU [AT]'],
        ['Fecha de pedido', '21/08/2026 17:03'],
        ['Fecha de envío', '21/08/2026 20:48, desde el stock «About You (FbAY)» (origen DE, destino AT)'],
        ['Alta y cierre en Channel Engine', '24/08/2026 00:50 las dos: entró en CE ya cerrado'],
        ['Estado en Channel Engine', [B('CLOSED')]],
        ['Línea 1 (devuelta)', 'ETNA_PLATA_38 · EAN 8434530691476 · 75,58 € · devolución RET-1410340351, motivo OTHER'],
        ['Línea 2 (entregada)', 'ETNA_PLATI_38 · EAN 8434530002241 · 75,58 € · sin devolución: el cliente se la ha quedado'],
        ['Importe del pedido', '151,16 € IVA incluido · gastos de envío 0,00 €'],
      ]),
      sep(),
      kvTable('Qué hizo Business Central (log del conector)', [
        ['Estado del proceso', [B('Skipped')]],
        ['Mensaje del conector', [run('«Skipped because ChannelEngine status CLOSED is not processable for BC sales order creation.»', { italics: true })]],
        ['Nº de pedido BC', 'Ninguno: no se creó pedido de venta para ninguna de las dos líneas'],
        ['Importe registrado en el log', '151,16 € (coincide con Channel Engine)'],
      ]),

      h2('Cronología'),
      numbered('pasos2')('21/08 17:03 — el cliente pide dos pares de ETNA en About You Austria.'),
      numbered('pasos2')('21/08 20:48 — About You envía los dos desde su stock (FbAY).'),
      numbered('pasos2')('Antes del 24/08 — el cliente devuelve uno (ETNA_PLATA_38) y se queda el otro (ETNA_PLATI_38).'),
      numbered('pasos2')('24/08 00:50 — la importación nocturna lo da de alta en Channel Engine ya en estado CLOSED.'),
      numbered('pasos2')('Business Central lo lee, ve CLOSED y lo descarta entero.'),

      h2('Consecuencia y propuesta'),
      par('La venta de ETNA_PLATI_38 (75,58 €) es real: About You la ha enviado, el cliente se la ha quedado y About You la liquidará, pero en BC no existe. ' +
          'La regla «CLOSED no procesable» es correcta para la línea devuelta y no para la entregada. A diferencia de los RETURNED descartados (página 1), aquí no hay neto cero.'),
      bullet([B('Propuesta: '), run('tratar CLOSED línea a línea: crear el pedido de venta con las líneas no devueltas (o crear el pedido completo y el abono de las devueltas).')]),
      bullet([B('Para IT: '), run('confirmar cómo distingue el conector las líneas de un pedido CLOSED y si puede leer el campo Return.Id de cada línea, que es lo que marca cuál se ha devuelto.')]),

      // ======================================================================= página 3
      h1P('3. Error de mapeo de producto («Order has product mapping errors»)'),
      par('23 pedidos enviados, 19 de About You y 4 de Bol.com, por 1.840,99 €, quedaron en estado Error con el mensaje «Order has product mapping errors.» ' +
          'BC no creó el pedido de venta, así que son ventas reales que faltan en BC. Se reparten por todo el mes (del 2 al 30 de agosto): no es un incidente puntual.'),

      h2('Ejemplo: pedido ayou-139-393564735 (About You DE)'),
      kvTable('Datos del pedido y respuesta del conector (horas en UTC)', [
        ['Fecha de pedido · estado CE', '15/08/2026 13:27 · SHIPPED (enviado por About You el 17/08 a las 14:36; alta en CE el 19/08 a las 00:49)'],
        ['Líneas', 'MONTGRI_MARI_45 · EAN 8434530025059 · 59,95 €   |   MONTGRI_MARI_44 · EAN 8434530025004 · 59,95 €'],
        ['Importe del pedido', '119,90 € IVA incluido'],
        ['Estado del proceso en BC', [B('Error'), run('   «Order has product mapping errors.»   · nº de pedido BC: ninguno')]],
      ]),

      h2('Qué se ve en los 23 pedidos'),
      bullet('Fallan 27 SKU distintos, y ninguno de ellos aparece en un pedido procesado bien (salvo MONZA-A_MENTA_41, que va en un pedido con otro SKU sin mapear). El fallo va por variante concreta, no por pedido ni por canal.'),
      bullet('De 19 de los 27 SKU sí hay otras tallas o colores del mismo modelo procesados sin problema (MONTGRI, ETNA, VERDI-V, DALLAS, ELLA…): lo que falta en BC son variantes talla/color, no modelos enteros.'),
      bullet('Todas las líneas llevan EAN de 13 dígitos, sin bundles ni caracteres raros: el conector tiene con qué mapear.'),
      gridTable(['SKU', 'EAN', 'Pedido', 'SKU', 'EAN', 'Pedido'], SKUS2, [1800, 1250, 1769, 1800, 1250, 1769], 15),
      par([run('Pedidos C000… = Bol.com, ay… = About You; fechas e importes de cada uno en la hoja «Cruce pedidos» del cuadre. ' +
               '(*) MONZA-A_MENTA_41 sí está mapeado (aparece en otro pedido procesado): el pedido C000CW0N43 falla, probablemente, por SIDNEY_NATURAL_41.', { size: 16, color: '595959' })], { spacing: { before: 60, after: 80 } }),

      h2('Para IT'),
      bullet('¿El mapeo va por SKU o por EAN? ¿Qué falta exactamente en BC para estas 27 variantes: el artículo, la variante o el código de barras?'),
      bullet('¿Se reprocesan solos al dar de alta la variante o hay que relanzarlos uno a uno? Hoy el log no tiene acción de reprocesar.'),
      bullet('El mensaje debería decir qué SKU o EAN falla: hoy hay que buscarlo a mano en Channel Engine.'),

      // ======================================================================= página 4
      h1P('4. Pedidos MANCO / CANCELED de Bol.com'),
      par('En Channel Engine, MANCO es el estado que toma un pedido cuando el stock disponible en CE no cubre alguna línea: el pedido no se puede preparar y acaba cancelado en Bol.com. ' +
          'En agosto ha pasado con 3 pedidos de Bol.com (224,90 €). El conector los descartó correctamente, porque no hubo venta, pero cada uno es una venta perdida y una cancelación ' +
          'que Bol.com penaliza al vendedor.'),

      h2('Los tres pedidos'),
      gridTable(['Pedido', 'Artículo (SKU · EAN)', 'Fecha de pedido (hora local)', 'Alta en CE (UTC)', 'Cancelado en CE (UTC)', 'Importe'], [
        ['C000CLL9CF', 'SABA-RG_MULTI_38 · 8434530859104', '08/08/2026 13:05', '08/08 11:08, acuse de recibo 11:13', '11/08 13:08 (3 días después)', '89,95 €'],
        ['C000D49N89', 'NEO-FR_MARI_44 · 8434530535718', '18/08/2026 17:29', '18/08 15:38:26, sin acuse de recibo', '18/08 15:38:27 (1 segundo después)', '45,00 €'],
        ['C000D4N152', 'BERNIA-P_LEO_41 · 8434530883956', '18/08/2026 22:47', '18/08 20:53, acuse de recibo 20:58', '24/08 14:46 (6 días después)', '89,95 €'],
      ], [1400, 2500, 1500, 1750, 1550, 938], 17),
      sep(),
      kvTable('Qué hizo Business Central (log del conector), igual en los tres', [
        ['Estado del proceso', [B('Skipped')]],
        ['Mensaje del conector', [run('«Skipped because ChannelEngine status MANCO is not processable for BC sales order creation.»', { italics: true })]],
        ['Estado CE en el log · hoy en CE', 'MANCO · CANCELED (el estado cambió después de que BC lo leyera)'],
        ['Nº de pedido BC', 'Ninguno, y es correcto: no se ha enviado nada'],
      ]),

      h2('Qué revisar'),
      par('No es un error del conector. Lo que hay que revisar es por qué Bol.com tenía stock publicado de esas tallas cuando Channel Engine no lo tenía. ' +
          'El caso C000D49N89 es el más claro: entró en CE y quedó en MANCO en el mismo segundo, es decir, CE ya sabía que no había stock cuando Bol.com aceptó el pedido. ' +
          'Y las cancelaciones tardan: una se comunicó a los 3 días y otra a los 6.'),
      bullet([B('Para IT: '), run('¿de dónde sale el stock que CE publica en Bol.com (BC, almacén, ambos) y cada cuánto se actualiza? ¿Se descuenta el stock reservado por pedidos pendientes?')]),
      bullet([B('Para IT: '), run('¿quién cancela en Bol.com un pedido MANCO y con qué plazo? Bol.com mide el porcentaje de cancelaciones del vendedor.')]),

      // ======================================================================= página 5
      h1P('5. Corte de mes: hora UTC en BC frente a hora local en Channel Engine'),
      par('Channel Engine muestra y filtra las fechas de pedido en hora local: About You las envía en UTC y Bol.com en hora de Ámsterdam (+02:00 en verano). ' +
          'El log de BC guarda la fecha de pedido en UTC. Entre las 22:00 y las 24:00 UTC los dos sistemas asignan el pedido a días distintos y, a final de mes, a meses distintos.'),

      h2('Los dos pedidos afectados en el corte de julio a agosto'),
      gridTable(['Pedido', 'Fecha de pedido (UTC)', 'Hora peninsular', 'Artículos', 'Importe', 'Estado CE'], [
        ['ayou-139-391740367', '31/07/2026 22:12', '01/08/2026 00:12', 'ELLA_TURQUESA_41 y ELLA_CACAU_41 (About You DE)', '149,90 €', 'CLOSED (una línea devuelta)'],
        ['ayou-139-391741025', '31/07/2026 22:17', '01/08/2026 00:17', 'DIXON_MARRO_44 (About You DE)', '74,95 €', 'RETURNED'],
      ], [1900, 1500, 1400, 2700, 900, 1238], 17),
      sep(),
      par('El export de Channel Engine de agosto (filtro del 01/08 al 31/08) los incluye; el log de agosto de BC no, porque su primer pedido es del 01/08 a las 10:02 UTC. ' +
          'Deberían estar en el log de julio de BC (pendiente de confirmar). Importe afectado: 224,85 €. Los dos entraron en CE el 03/08 ya devueltos o cerrados, ' +
          'así que el conector los habría descartado igualmente; el problema no es este par de pedidos, sino que la regla no está definida.'),
      par('A final de agosto no hay pedidos entre las 22:00 y las 24:00 UTC del día 31, así que el corte de salida del mes no se ve afectado esta vez. En cualquier mes puede haberlos.'),

      h2('Propuesta'),
      numbered('pasos5')('Fijar una sola regla de fecha de pedido para todo: la recomendación es hora peninsular (Europe/Madrid), que es la que ven Channel Engine, los marketplaces y sus liquidaciones.'),
      numbered('pasos5')('Que BC convierta la fecha de pedido de UTC a hora peninsular al crear el pedido de venta, y que el log del conector guarde las dos.'),
      numbered('pasos5')('Adaptar el cuadre mensual a la misma regla (hoy trabaja en UTC porque es lo que hay en el log).'),
      bullet([B('Para IT: '), run('¿qué fecha usa BC como fecha de pedido y fecha de registro, la UTC de CE tal cual o convertida? ¿Y la fecha de envío y de factura?')]),
    ],
  }],
});
Packer.toBuffer(doc).then((buf) => { fs.writeFileSync(OUT, buf); console.log('Escrito', OUT, buf.length, 'bytes'); });
