const fs = require('fs');
const { Document, Packer, Paragraph, TextRun, HeadingLevel, Table, TableRow, TableCell, WidthType, AlignmentType,
        BorderStyle, ShadingType, LevelFormat, PageNumber, Footer, VerticalAlign, TableLayoutType } = require('docx');

const OUT = process.argv[2];
const AZUL = '1F4E78', GRIS = 'F2F2F2', BORDE = 'BFBFBF', font = 'Arial';
const b = { style: BorderStyle.SINGLE, size: 4, color: BORDE };
const borders = { top: b, bottom: b, left: b, right: b };
const W1 = 2900, W2 = 6738, W = W1 + W2;

const run = (text, o = {}) => new TextRun({ text, font, size: 20, ...o });
const par = (children, o = {}) => new Paragraph({ spacing: { after: 120, line: 276 }, ...o,
  children: Array.isArray(children) ? children : [run(children)] });
const cp = (children) => new Paragraph({ spacing: { after: 0 }, children: Array.isArray(children) ? children : [run(children)] });
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
const paso = (t) => new Paragraph({ numbering: { reference: 'pasos', level: 0 }, spacing: { after: 40, line: 276 }, children: [run(t)] });
const h1 = (t) => new Paragraph({ heading: HeadingLevel.HEADING_1, children: [run(t, { size: 28, bold: true, color: AZUL })] });
const h2 = (t) => new Paragraph({ heading: HeadingLevel.HEADING_2, children: [run(t, { size: 22, bold: true, color: AZUL })] });

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
    { reference: 'pasos', levels: [{ level: 0, format: LevelFormat.DECIMAL, text: '%1.', alignment: AlignmentType.START, style: { paragraph: { indent: { left: 500, hanging: 300 } } } }] },
  ] },
  sections: [{
    properties: { page: { margin: { top: 1134, bottom: 1134, left: 1134, right: 1134 } } },
    footers: { default: new Footer({ children: [new Paragraph({ alignment: AlignmentType.RIGHT, children: [
      run('Errores conector Channel Engine · página ', { size: 16, color: '808080' }),
      new TextRun({ children: [PageNumber.CURRENT], font, size: 16, color: '808080' }) ] })] }) },
    children: [
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
        ['Estado en Channel Engine', [run('RETURNED', { bold: true })]],
        ['Línea', 'VERDI-V_CRU_40 · EAN 8434530369818 · Espadrilles · 1 unidad'],
        ['Importe', '74,95 € IVA incluido (61,94 € + 13,01 € de IVA al 21 %) · gastos de envío 0,00 €'],
        ['Devolución', 'RET-1415710880 (id 2395) · motivo OTHER · «Returned to About You - no return reason info known»'],
      ]),
      par('', { spacing: { after: 80 } }),
      kvTable('Qué hizo Business Central (log del conector)', [
        ['Estado del proceso', [run('Skipped', { bold: true })]],
        ['Mensaje del conector', [run('«Skipped because ChannelEngine status RETURNED is not processable for BC sales order creation.»', { italics: true })]],
        ['Nº de pedido BC', 'Ninguno: no se creó pedido de venta'],
        ['Importe registrado en el log', '74,95 € (coincide con Channel Engine)'],
      ]),

      h2('Cronología'),
      paso('31/08 18:48 — el cliente hace el pedido en About You Países Bajos.'),
      paso('01/09 14:34 — About You lo envía desde su propio stock (FbAY); Toni Pons no interviene en el envío.'),
      paso('Entre el 01/09 y el 03/09 — el cliente lo devuelve a About You.'),
      paso('03/09 00:49 — la importación nocturna lo da de alta en Channel Engine ya en estado RETURNED (alta y cierre en el mismo segundo).'),
      paso('Business Central lo lee, ve el estado RETURNED y lo descarta: no crea pedido de venta ni abono.'),

      h2('Consecuencia'),
      par('Ni la venta de 74,95 € ni su devolución existen en Business Central. El efecto neto es cero y por eso el conector lo trata así por diseño, ' +
          'pero la operación no queda registrada. Los pedidos de About You entran en Channel Engine entre 1 y 12 días después de la fecha de pedido, ' +
          'así que cualquiera devuelto en ese plazo llega ya como RETURNED y se descarta. Si se quiere que estas ventas devueltas consten en BC (venta más abono), ' +
          'hay que cambiar la regla del conector, no corregir pedido a pedido. Los 22 casos de agosto están en la hoja «Cruce pedidos» del cuadre, en azul claro.'),
    ],
  }],
});
Packer.toBuffer(doc).then((buf) => { fs.writeFileSync(OUT, buf); console.log('Escrito', OUT, buf.length, 'bytes'); });
