const fs = require('fs');
const { Document, Packer, Paragraph, TextRun, HeadingLevel, Table, TableRow, TableCell, WidthType, AlignmentType,
        BorderStyle, ShadingType, LevelFormat, PageNumber, Footer, VerticalAlign, TableLayoutType, PageOrientation } = require('docx');

const OUT = process.argv[2];
const AZUL = '1F4E78', GRIS = 'F2F2F2', BORDE = 'BFBFBF', font = 'Arial';
const VERDE = 'C6EFCE', AMARILLO = 'FFEB9C';
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
const B = (t) => run(t, { bold: true });
const I = (t) => run(t, { italics: true });

function kvTable(title, rows) {
  return new Table({
    width: { size: W, type: WidthType.DXA }, columnWidths: [W1, W2], layout: TableLayoutType.FIXED,
    rows: [
      new TableRow({ tableHeader: true, children: [cell([cp([run(title, { bold: true, color: 'FFFFFF' })])], W, { columnSpan: 2, shading: shade(AZUL) })] }),
      ...rows.map(([k, v]) => new TableRow({ children: [
        cell([cp([run(k, { bold: true })])], W1, { shading: shade(GRIS) }),
        cell([cp(typeof v === 'string' ? [run(v)] : v)], W2) ] })),
    ],
  });
}
// rows: array de arrays de string o de TextRun[]; fills opcional por fila
function grid(headers, rows, widths, size = 17, fills = []) {
  const total = widths.reduce((a, c) => a + c, 0);
  const m = { top: 30, bottom: 30, left: 60, right: 60 };
  const mk = (v, w, o = {}) => new TableCell({ width: { size: w, type: WidthType.DXA }, borders, margins: m, verticalAlign: VerticalAlign.CENTER, ...o,
    children: [new Paragraph({ spacing: { after: 0 }, alignment: o.align || AlignmentType.LEFT,
      children: typeof v === 'string' ? [run(v, { size, ...(o.runOpts || {}) })] : v })] });
  return new Table({
    width: { size: total, type: WidthType.DXA }, columnWidths: widths, layout: TableLayoutType.FIXED,
    rows: [
      new TableRow({ tableHeader: true, children: headers.map((h, i) => mk(h, widths[i], { shading: shade(AZUL), runOpts: { bold: true, color: 'FFFFFF' } })) }),
      ...rows.map((r, ri) => new TableRow({ children: r.map((v, i) => mk(v, widths[i], fills[ri] ? { shading: shade(fills[ri]) } : {})) })),
    ],
  });
}
const numbered = (ref) => (t) => new Paragraph({ numbering: { reference: ref, level: 0 }, spacing: { after: 40, line: 276 },
  children: Array.isArray(t) ? t : [run(t)] });
const bullet = (t) => new Paragraph({ numbering: { reference: 'vinetas', level: 0 }, spacing: { after: 40, line: 276 },
  children: Array.isArray(t) ? t : [run(t)] });
const h1 = (t, brk = false) => new Paragraph({ heading: HeadingLevel.HEADING_1, pageBreakBefore: brk, children: [run(t, { size: 28, bold: true, color: AZUL })] });
const h2 = (t) => new Paragraph({ heading: HeadingLevel.HEADING_2, children: [run(t, { size: 22, bold: true, color: AZUL })] });
const sep = () => par('', { spacing: { after: 60 } });
const numCfg = (ref) => ({ reference: ref, levels: [{ level: 0, format: LevelFormat.DECIMAL, text: '%1.', alignment: AlignmentType.START,
  style: { paragraph: { indent: { left: 500, hanging: 300 } } } }] });


const pie = () => ({ default: new Footer({ children: [new Paragraph({ alignment: AlignmentType.RIGHT, children: [
  run('Liquidación ECI Portugal · agosto 2026 · página ', { size: 16, color: '808080' }),
  new TextRun({ children: [PageNumber.CURRENT], font, size: 16, color: '808080' })] })] }) });
const MARGEN = { top: 1134, bottom: 1134, left: 1134, right: 1134 };
const PDFBC = [
  ['Venta total con IVA', 'VENDA TOTAL', 'Importe liquidable', '4.922,72', '4.922,72', '0,00', '981,56', '981,56', '0,00', '101,87', '101,87', '0,00', '6.006,15', '6.006,15', '0,00'],
  ['Venta neta sin IVA', 'NETA', 'Base imponible comisión', '4.002,21', '4.888,76', '+886,55', '798,02', '981,56', '+183,54', '82,82', '101,87', '+19,05', '4.883,05', '5.972,19', '+1.089,14'],
  ['IVA de la venta (23 %)', 'IVA (23.00)', 'no existe en BC', '920,51', '—', '—', '183,54', '—', '—', '19,05', '—', '—', '1.123,10', '—', '—'],
  ['% participación ECI', '%', 'Comisión esperada / base', '29 %', '29,00 %', '0', '29 %', '29,00 %', '0', '29 %', '29,01 %', '+0,01', '29 %', '29,00 %', '0'],
  ['Participación ECI', 'PARTICIP.ECI EUROS', 'Comisión esperada', '1.160,64', '1.417,74', '+257,10', '231,43', '284,68', '+53,25', '24,02', '29,55', '+5,53', '1.416,09', '1.731,97', '+315,88'],
  ['Importe a facturar', 'A FACTURAR IMPORTE', 'Importe neto esperado', '2.841,57', '3.504,98', '+663,41', '566,59', '696,88', '+130,29', '58,80', '72,32', '+13,52', '3.466,96', '4.274,18', '+807,22'],
  ['IVA a facturar (0 %)', 'IVA (0.00)', 'IVA comisión esperado', '0,00', '0,00', '0,00', '0,00', '0,00', '0,00', '0,00', '0,00', '0,00', '0,00', '0,00', '0,00'],
  ['Total factura', 'TOTAL FRA', 'Importe neto esperado', '2.841,57', '3.504,98', '+663,41', '566,59', '696,88', '+130,29', '58,80', '72,32', '+13,52', '3.466,96', '4.274,18', '+807,22'],
];
const FILL_PDFBC = [VERDE, AMARILLO, GRIS, VERDE, AMARILLO, AMARILLO, VERDE, AMARILLO];
const SECCION_PDF_BC = {
  properties: { page: { size: { width: 11906, height: 16838, orientation: PageOrientation.LANDSCAPE }, margin: MARGEN } },
  footers: pie(),
  children: [
    h1('Cuadro: columnas del PDF de ECI frente a BC'),
    par('Cada fila es una columna de los PDF de liquidación de Portugal. A su lado, el campo de BC que le corresponde y la diferencia (BC − PDF). Los valores de BC son la suma de las filas de Portugal del informe (centros 0140 + 0142 + 0143), porque ECI liquida todo en 0143.'),
    grid(['Columna del PDF', 'Nombre en el PDF', 'Campo en BC', '601 PDF', '601 BC', '601 dif.', '602 PDF', '602 BC', '602 dif.', '696 PDF', '696 BC', '696 dif.', 'Total PDF', 'Total BC', 'Total dif.'],
      PDFBC.map((r, i) => (i === 7 ? r.map((v) => [run(v, { bold: true, size: 15 })]) : r)), [1550, 1300, 1450, 830, 830, 800, 780, 780, 760, 720, 720, 700, 870, 870, 820], 15, FILL_PDFBC),
    sep(),
    bullet([B('Venta con IVA: '), run('coincide al céntimo en los tres departamentos.')]),
    bullet([B('Venta neta: '), run('BC no quita el IVA. Su base de comisión es el importe con IVA, y además deja fuera las líneas sin vincular (601: 4.922,72 − 4.888,76 = 33,96 €).')]),
    bullet([B('IVA de la venta: '), run('BC no lo calcula ni lo muestra en este informe.')]),
    bullet([B('Porcentaje: '), run('el mismo 29 % en los dos. La diferencia está en la base sobre la que se aplica.')]),
    bullet([B('Participación, importe a facturar y total factura: '), run('BC sale por encima en todos: 315,88 € más de comisión y 807,22 € más de neto que lo que se factura a ECI (facturas 260007291, 260007292 y 260007293, 3.466,96 €).')]),
    bullet([B('IVA a facturar: '), run('vale 0 en los dos, pero no es el mismo concepto. En el PDF es el IVA de la factura de Toni Pons, 0 % porque Portugal se factura sin IVA. En BC es el IVA de la comisión.')]),
    par([run('Verde: coincide. Amarillo: diferencia. Gris: BC no tiene el dato. El mismo cuadro, con fórmulas y el detalle por centro de BC, está en la hoja «PDF vs BC» del Excel.', { size: 18, color: '595959' })], { spacing: { before: 120 } }),
  ],
};

const doc = new Document({
  creator: 'Oriol Terradas', title: 'Liquidación ECI Portugal agosto 2026: motivos',
  styles: {
    default: { document: { run: { font, size: 20 } } },
    paragraphStyles: [
      { id: 'Title', name: 'Title', basedOn: 'Normal', next: 'Normal', run: { font, size: 40, bold: true, color: AZUL }, paragraph: { spacing: { after: 40 } } },
      { id: 'Heading1', name: 'Heading 1', basedOn: 'Normal', next: 'Normal', quickFormat: true, run: { font, size: 28, bold: true, color: AZUL }, paragraph: { spacing: { before: 240, after: 120 }, outlineLevel: 0 } },
      { id: 'Heading2', name: 'Heading 2', basedOn: 'Normal', next: 'Normal', quickFormat: true, run: { font, size: 22, bold: true, color: AZUL }, paragraph: { spacing: { before: 200, after: 80 }, outlineLevel: 1 } },
    ],
  },
  numbering: { config: [numCfg('n1'), numCfg('n2'), numCfg('n3'), numCfg('n6'),
    { reference: 'vinetas', levels: [{ level: 0, format: LevelFormat.BULLET, text: '•', alignment: AlignmentType.START,
      style: { paragraph: { indent: { left: 500, hanging: 300 } } } }] }] },
  sections: [{
    properties: { page: { margin: { top: 1134, bottom: 1134, left: 1134, right: 1134 } } },
    footers: pie(),
    children: [
      // ================================================================== 1. resumen
      new Paragraph({ heading: HeadingLevel.TITLE, children: [run('Liquidación ECI Portugal, agosto 2026: motivos de las diferencias', { size: 40, bold: true, color: AZUL })] }),
      par([run('Informe «Liquidación mensual ECI» de Business Central (02/10/2026) frente a los PDF de liquidación de ECI, el export de pedidos de Mirakl (21/09), el log del conector (01/09) y el detalle de la comparación operativa de BC de las filas 0142 / 601, 0143 / 601 y 0143 / 602 · actualizado el 05/10/2026', { size: 18, color: '595959' })], { spacing: { after: 200 } }),

      h1('Resumen'),
      par([B('Los importes de liquidación que BC ha importado de EDI son correctos. '), run('Sumando los tres centros portugueses del informe de BC, cada departamento da exactamente el total del PDF de ECI:')]),
      grid(['Departamento', 'Liquidable BC 0140 + 0142 + 0143', 'Total venta del PDF de ECI', 'Diferencia'], [
        ['601 mujer', '6.318,44 − 622,80 − 772,92 = 4.922,72 €', '4.922,72 €', '0,00'],
        ['602 hombre', '981,56 €', '981,56 €', '0,00'],
        ['696 niños', '137,83 − 35,96 = 101,87 €', '101,87 €', '0,00'],
      ], [1800, 3900, 2400, 1538], 18, [VERDE, VERDE, VERDE]),
      sep(),
      par('Los avisos del informe no son errores de importe de venta. Salen de la comparación de cada línea EDI con su tramo de Mirakl y de lo que BC ha convertido en documento. Además, BC calcula mal la comisión de Portugal (cuadro de la página 2). En total hay cinco motivos:'),
      grid(['Motivo', 'Filas afectadas', 'Importe', 'Página'], [
        ['1. BC calcula la comisión y el neto sobre el importe con IVA', 'todas', '807,22 € de neto de más', '3'],
        ['2. Líneas EDI sin vincular: pedidos anteriores al conector o que el conector dejó de actualizar', '0143 mujer (6), 0142 Gaia (1)', '7 líneas, neto 33,96 €', '4'],
        ['3. Tramos sin procesar: devoluciones que ECI abona y que no existen en Mirakl', '0142 Gaia (3), 0143 mujer (1)', '4 devoluciones, 299,80 €', '5'],
        ['4. Devoluciones hechas en tienda: BC las pone en 0140 y 0142, ECI las liquida en 0143', '0140, 0142', '23 líneas, 1.431,68 €', '6'],
        ['5. Reglas de ECI que hacen que EDI y Mirakl no coincidan línea a línea', '0143', 'explica el resto', '7'],
      ], [4600, 2200, 2000, 838], 17),
      sep(),
      grid(['Fila BC', 'Estado', 'Qué hay detrás'], [
        ['0140 / 601', 'Cuadrado', '9 devoluciones en la tienda de Lisboa, todas vinculadas y procesadas.'],
        ['0140 / 696', 'Cuadrado', '1 devolución de niños en Lisboa (35,96 €), en Incidencia abierta en Mirakl.'],
        ['0142 / 601', 'Aviso', '9 devoluciones en Gaia procesadas, 7 de ellas con la incidencia aún abierta en Mirakl; 1 sin vincular (34,95 €, pedido de junio); 3 sin procesar (219,85 €): el pedido 00401430751578320260801170207, devuelto en Gaia según ECI y sin devolución en Mirakl.'],
        ['0143 / 601', 'Aviso', '6 líneas sin vincular (neto +68,91 €); 1 devolución sin procesar (79,95 €, línea 00401430764858020260717201700_1-A-1, sin reembolso en Mirakl); 1 producto sin relacionar.'],
        ['0143 / 602', 'Cuadrado', 'Todo vinculado y procesado. Incluye una venta de 65 € recepcionada el 31/08 a las 23:52, que Mirakl fecha el 01/09 (página 7).'],
        ['0143 / 696', 'Cuadrado', 'Todo vinculado y procesado.'],
      ], [1400, 1200, 7038], 17, [VERDE, VERDE, AMARILLO, AMARILLO, VERDE, VERDE]),
      par([run('El detalle línea a línea está en el Excel «Motivos liquidación ECI Portugal agosto 2026 (v2)». Reconstruye desde Mirakl todas las líneas EDI y, con las 5 líneas identificadas en el detalle de BC, reproduce cada fila del informe. Todas las líneas de Portugal están identificadas; solo queda sin localizar el «producto sin relacionar» de 0143 / 601.', { size: 18, color: '595959' })], { spacing: { before: 120 } }),

    ],
  }, SECCION_PDF_BC, {
    properties: { page: { margin: MARGEN } },
    footers: pie(),
    children: [
      // ================================================================== 2. comisión
      h1('1. BC calcula la comisión y el neto sobre el importe con IVA'),
      par('ECI cobra una participación del 29 % en Portugal. La calcula sobre la venta neta, después de quitar el IVA portugués del 23 %. Toni Pons factura a ECI Portugal el resto sin IVA. BC, en cambio, aplica el 29 % al importe con IVA y da como «Importe neto esperado» el importe con IVA menos esa comisión.'),
      grid(['Departamento', 'Venta ECI (con IVA)', 'Neta sin IVA', 'Participación ECI', 'A facturar (ECI)', 'Comisión esperada BC', 'Neto esperado BC', 'Neto BC de más'], [
        ['601', '4.922,72', '4.002,21', '1.160,64', '2.841,57', '1.417,74', '3.504,98', '663,41'],
        ['602', '981,56', '798,02', '231,43', '566,59', '284,68', '696,88', '130,29'],
        ['696', '101,87', '82,82', '24,02', '58,80', '29,55', '72,32', '13,52'],
        [[B('Total')], [B('6.006,15')], [B('4.883,05')], [B('1.416,09')], [B('3.466,96')], [B('1.731,97')], [B('4.274,18')], [B('807,22')]],
      ], [1250, 1250, 1150, 1250, 1200, 1250, 1150, 1138], 17),
      sep(),
      par([run('Los 3.466,96 € coinciden con las facturas 260007291, 260007292 y 260007293 del fichero «total agost». La diferencia de 807,22 € es el IVA portugués que BC no descuenta (1.123,10 €) menos la comisión que BC calcula de más al aplicarla sobre el importe con IVA (315,88 €).')]),
      h2('Otros puntos de la comisión'),
      bullet([B('En España hay otro error en niños. '), run('BC aplica el 29 % a las filas 696 de España y ECI aplica el 30 % (PDF 0090/696). En mujer y hombre BC usa el 30 %, que es correcto. Como en España el IVA de la venta y el de la factura son el mismo 21 %, el problema del IVA no se nota allí.')]),
      bullet([B('Las líneas sin vincular no tienen comisión. '), run('BC las deja fuera de la base de comisión, pero las suma enteras en el neto esperado. En Portugal son 33,96 € netos en 601.')]),
      bullet([B('«Comisión real Mirakl» vale 0 en todas las filas. '), run('Es lo esperable: ECI no carga su participación en Mirakl, donde las 27.730 líneas del export tienen comisión 0. La cobra en la liquidación mensual, así que esa columna no sirve para ECI.')]),
      bullet([B('Céntimos. '), run('La comisión esperada de BC difiere del 29 % exacto en 1 a 3 céntimos por fila (602: 284,68 frente a 284,65). Ninguna fórmula de redondeo probada reproduce todas las filas a la vez.')]),
      h2('Petición para IT'),
      par('Calcular la comisión esperada sobre la venta neta del IVA del país y, en Portugal, el neto esperado sin IVA: neta − 29 % de la neta. Revisar el porcentaje de 696 en España.'),

      // ================================================================== 3. sin vincular
      h1('2. Líneas EDI sin vincular: pedidos antiguos o congelados en el conector', true),
      par('BC vincula cada línea EDI con un tramo de Mirakl, es decir, con una venta o una devolución que haya traído el conector. Si el conector no tiene ese tramo, la línea EDI queda sin vincular y fuera de la base de comisión. En Portugal hay 7. Todas son de pedidos creados antes de julio, por dos causas distintas.'),
      h2('Causa A: ventas de pedidos antiguos que ECI cumplimenta en agosto'),
      par('BC vincula las ventas por el talón de cumplimentación. ECI sigue cumplimentando y liquidando en agosto entregas de pedidos de hace meses. Tres son de antes del arranque del conector (01/06/2026), se registraron en SAP y BC no tiene ningún tramo para ellas. La cuarta es de un pedido del 15/06 que BC tiene como venta 124836 desde junio. Lo más probable es que no se vincule por la causa B: el conector dejó de actualizar ese pedido y no tiene el talón de cumplimentación del 25/08. Está por confirmar con IT.'),
      grid(['Línea de Mirakl', 'Pedido creado', 'Talón de cumplimentación', 'Importe'], [
        ['00401430766493020260112191028_1-A-1', '12/01/2026', '94593123 (25/08)', '26,96 €'],
        ['00401430762747320260220131747_1-A-2', '20/02/2026', '92259699 (05/08)', '63,96 €'],
        ['00401430760456120260512181250_1-A-1', '12/05/2026', '91948254 (03/08)', '69,95 €'],
        ['00401430752499520260615175342_1-A-1 (venta BC 124836)', '15/06/2026', '94593704 (25/08)', '59,95 €'],
        [[B('Ventas sin vincular en 0143 / 601')], '', '', [B('220,82 €')]],
      ], [4300, 1500, 2300, 1538], 17),
      h2('Causa B: pedidos de junio que el conector dejó de actualizar'),
      par('En el log del conector, todos los pedidos creados hasta el 28/06 quedaron con el estado que tenían el 29-30/06. Desde entonces no reciben entregas, incidencias ni reembolsos, aunque ya tengan pedido de venta en BC. En Portugal no se ha perdido ningún evento de los pedidos creados desde el 29/06 (0 de 345 líneas); en España, solo 6 de 6.346, frente a 837 de 4.068 antes del corte. Si un cliente devuelve uno de esos pedidos, el conector no se entera, no crea el tramo de devolución y la línea EDI queda sin vincular.'),
      grid(['Línea de Mirakl', 'Pedido creado / venta BC', 'Talón de abono', 'Fila BC', 'Importe'], [
        ['00401430758314520260624160644_1-A-1', '24/06 · 124883', '92013281 online (03/08)', '0143 / 601', '−79,95 €'],
        ['00401430753352420260626123836_1-A-1', '26/06 · 124846', '93831013 online (18/08)', '0143 / 601', '−71,96 €'],
        ['00401430750680520260627151042_1-A-2', '27/06 · 124828', '02655092 Gaia (13/08)', '0142 / 601', '−34,95 €'],
      ], [3500, 1900, 2100, 1100, 1038], 17),
      par([run('En el log las tres siguen como enviadas, sin devolución detectada y con reembolso 0, aunque en Mirakl están reembolsadas. Neto sin vincular: 0143 / 601 = 220,82 − 151,91 = +68,91 €, que es justo la diferencia entre liquidable y base de comisión de BC (6.318,44 − 6.249,53). En 0142 es −34,95 € (−772,92 + 737,97).')], { spacing: { before: 120 } }),
      h2('Consecuencia y petición para IT'),
      bullet('Esto seguirá pasando: en julio hay al menos 12 devoluciones más de pedidos congelados, que saldrán sin vincular en la liquidación de julio.'),
      bullet('Preguntar a IT por qué el conector dejó de refrescar los pedidos creados hasta el 28/06 y forzar una relectura. Si no se puede, registrar esas devoluciones a mano.'),
      bullet('Definir cómo se registran en BC las entregas que ECI liquida de pedidos de SAP (antes del 01/06).'),

      // ================================================================== 4. sin procesar
      h1('3. Tramos sin procesar: 4 devoluciones que ECI abona y Mirakl no tiene', true),
      par('BC solo puede crear el documento de devolución si la devolución existe en Mirakl. Estas 4 líneas están en el EDI de ECI como devoluciones, BC las ha vinculado con su pedido de Mirakl, pero en Mirakl esas líneas no tienen devolución, incidencia ni reembolso. Por eso BC no las procesa y cuentan 0 € en el lado Mirakl. Se han identificado con el detalle de la comparación operativa de BC.'),
      grid(['Línea de Mirakl', 'Fila BC', 'Fecha EDI', 'EAN', 'Importe', 'En Mirakl'], [
        ['00401430751578320260801170207_1-A-1', '0142 / 601', '10/08', '8434530939677', '−59,95 €', 'Recibido, sin devolución'],
        ['00401430751578320260801170207_2-A-1', '0142 / 601', '10/08', '8434530688612', '−69,95 €', 'Recibido, sin devolución'],
        ['00401430751578320260801170207_2-A-2', '0142 / 601', '10/08', '8434530872639', '−89,95 €', 'Recibido, sin devolución'],
        ['00401430764858020260717201700_1-A-1', '0143 / 601', '05/08', '8434530946972', '−79,95 €', 'Recibido, sin reembolso'],
        [[B('Total')], '', '', '', [B('−299,80 €')], ''],
      ], [3600, 1000, 800, 1450, 1050, 1738], 17),
      h2('Gaia: pedido 00401430751578320260801170207 (219,85 €)'),
      par('Tres pares de alpargatas de mujer, pedidos el 01/08 y entregados en casa de la clienta el 07/08. Según el EDI (informe 20260811035705067032352), los tres se devolvieron en la tienda de Gaia el 10/08 y ECI los abonó. En Mirakl el pedido sigue «Recibido»: no tiene devolución, incidencia, talón de abono ni mensajes. BC lo encuentra por el talón de venta 07515783, porque no hay talón de abono con el que vincularlo.'),
      h2('Online: línea 00401430764858020260717201700_1-A-1 (79,95 €)'),
      par('Pedido del 17/07 con dos pares de menorquinas de mujer, entregado el 22/07. El EDI del 05/08 (informe 20260806042406067032352) abona las dos líneas. En Mirakl solo está devuelta y reembolsada la otra línea, la 2-A-1 de 75 € (talón de abono 92363569), que BC tiene procesada (documento 6245). La 1-A-1 sigue «Recibido», sin reembolso.'),
      h2('Qué hay que pedir a ECI'),
      par('Si las devoluciones se hicieron, el talón de abono de cada una y registrarlas en Mirakl, para que Toni Pons pueda recoger la mercancía y BC crear el documento. Si no se hicieron, regularizar los 299,80 € en la liquidación.'),
      par([B('Lo que queda descartado. '), run('Las 7 devoluciones de Gaia con la incidencia abierta en Mirakl (talones 02695702, 02654478, 06171499, 02655550, 02655611 y 02667327) sí están procesadas en BC, cada una con su documento. Tampoco son devoluciones de julio liquidadas tarde: ninguna de las candidatas de julio está en el detalle de agosto.')]),

      // ================================================================== 5. tiendas
      h1('4. Devoluciones hechas en las tiendas de Lisboa y Gaia', true),
      par('Un cliente puede devolver en una tienda física un pedido online de Portugal. EDI y BC ponen esa devolución en el centro de la tienda donde se hizo el abono: 0140 Lisboa o 0142 Gaia. ECI, en cambio, la liquida dentro del centro de venta a distancia 0143. Por eso los PDF solo traen 0143 y cuadran con la suma de los tres centros de BC.'),
      grid(['Centro BC', 'Departamento', 'Líneas', 'Importe', 'Cómo se reconoce en Mirakl'], [
        ['0140 Lisboa', '601', '9', '−622,80 €', 'talón de abono de las cajas 0247, 0558, 0559 y 0561'],
        ['0140 Lisboa', '696', '1', '−35,96 €', 'talón 03594705 (caja 0359)'],
        ['0142 Gaia', '601', '13', '−772,92 €', '10 con talón de las cajas 0265, 0266, 0269 y 0617; 3 del pedido 00401430751578320260801170207, sin talón de abono en Mirakl (página 5)'],
        ['0143 online', '601 y 602', '11', '−657,08 €', '10 con talón de abono que empieza por 9; 1 (00401430764858020260717201700_1-A-1) sin talón de abono en Mirakl (página 5)'],
      ], [1500, 1400, 900, 1300, 4538], 17),
      sep(),
      par([B('Cómo se sabe qué caja es de qué tienda. '), run('El centro lo marcan los 4 primeros dígitos del talón de abono, que son la caja, no los 2 primeros. Hay dos pruebas independientes. Los 5 pedidos creados en Gaia llevan talones de venta de las cajas 0260, 0265, 0266 y 0269. Además, en las recogidas en tienda el código postal de entrega es el de la tienda: Lisboa 10xx y Gaia 44xx.')]),
      par([B('Solo las devoluciones van a la tienda. '), run('Las ventas finalizadas y las rescisiones van siempre al centro del pedido, aunque se hagan en una caja de tienda. Por ejemplo, el abono 05590623 (65 €) de una recogida en tienda nunca entregada cuenta como rescisión de 0143.')]),
      h2('Cuándo registra cada sistema una devolución en tienda'),
      par('Mirakl informa de la devolución en tienda con tres mensajes. Cada sistema la registra en un momento distinto:'),
      bullet([B('R01, devolución en tienda: '), run('el cliente devuelve en una tienda de ECI y le abonan por el TPV. Mirakl abre una incidencia con reembolso 0. ECI la liquida en el mes de la R01, que es la fecha del talón de abono. BC puede crear la devolución desde este momento, cuando procesa la incidencia.')]),
      bullet([B('R02, mercancía en el almacén: '), run('llega al almacén de MRW en San Fernando de Henares. En las devoluciones de agosto en Gaia tardó entre 5 y 8 semanas, y en tres todavía no ha llegado.')]),
      bullet([B('R03, devolución cerrada: '), run('Toni Pons recoge la mercancía. En ese momento Mirakl crea el reembolso, a la misma hora que la R03.')]),
      par([B('Pruebas. '), run('Las 7 incidencias de Gaia de agosto no tienen R03 y están en el EDI de agosto y procesadas en BC. Tres devoluciones de Lisboa con la R01 en julio y la R03 en agosto no están en el EDI de agosto. El reembolso de tienda de Mirakl (motivo REFUND_04) se crea por lotes en los días de recogida: 26/06, 24/07, 31/07 y 31/08. Ejemplo en Gaia (talón 02652811): el pedido 00401430750813420260714121528 tiene la R01 el 27/07, la R02 el 24/08 y la R03 el 31/08; Mirakl lo reembolsa el 31/08, pero no está en la liquidación de agosto.')]),
      par([B('Riesgos para IT. '), run('BC crea la devolución antes de que exista el reembolso, así que todavía no sabe el importe que se devolverá al final. Y a 01/09 BC no tenía ninguna devolución de Portugal procesada: todas se procesaron entre el 01/09 y el 02/10.')]),
      h2('Consecuencias'),
      bullet('Las filas de BC por centro no se pueden comparar una a una con el PDF de ECI: hay que comparar por departamento sumando todos los centros. En España pasa lo mismo, porque ECI lleva a 0090 las devoluciones de las tiendas.'),
      bullet('El PDF dice «facturar independientemente por centro», pero solo trae 0143. Conviene confirmar con ECI que la factura de Portugal va por departamento consolidado, como se ha hecho hasta ahora (facturas 260007291 a 260007293).'),

      // ================================================================== 6. reglas
      h1('5. Cómo construye ECI cada línea EDI', true),
      par('Para reconstruir desde Mirakl las líneas que ECI manda por EDI hay que aplicar estas reglas. Están comprobadas al céntimo en Portugal y explican por qué una línea de Mirakl no siempre se corresponde con una línea EDI.'),
      grid(['Tipo de línea EDI', 'Regla', '¿Se liquida?'], [
        ['Venta finalizada', 'Recepción del mes, por el importe de la línea; normalmente es la fecha del talón de cumplimentación. Las líneas rechazadas no cuentan.', 'Sí'],
        ['Devolución', 'Talón de abono del mes sobre una línea entregada y realmente devuelta, por las unidades devueltas. En tienda es la fecha de la R01. Cuenta aunque Mirakl aún no haya reembolsado (Incidencia abierta).', 'Sí, en negativo'],
        ['En proceso', 'Pedidos del mes, por fecha de cobro. ECI cierra el día hacia las 23:30 hora peninsular.', 'No'],
        ['Rescisión', 'Líneas rechazadas o canceladas del mes, y abonos o reembolsos del mes de líneas nunca entregadas.', 'No'],
      ], [1900, 6338, 1400], 17),
      h2('Casos de agosto que lo muestran'),
      bullet([B('Línea rechazada con talón de cumplimentación: '), run('00401430762747320260220131747_1-A-1, 53,96 €. El talón es del pedido y se copia a todas sus líneas, pero ECI no liquida la rechazada.')]),
      bullet([B('Línea hermana no devuelta: '), run('00401430750680520260627151042_1-A-1 (71,96 €) y 00401430761148620260802134750_1-A-1 (69,95 €) comparten el talón de abono con su hermana devuelta, pero no se devolvieron y no están en el EDI.')]),
      bullet([B('Devolución sin reembolso en Mirakl: '), run('las líneas en Incidencia abierta se liquidan enteras. Ejemplo: 00401430764963720260730123658_1-A-1 (niños, 35,96 €), talón 03594705 del 17/08, reembolso 0 en Mirakl.')]),
      bullet([B('Línea de 2 unidades con 1 devuelta: '), run('00401430763049820260801022856_1-A-1 y -A-2 (150 € cada una) entran como devolución de 1 unidad a 75 €.')]),
      bullet([B('Corte de fin de mes: '), run('dos pedidos del 31/08 por la noche (72,00 € cobrado a las 23:42 y 27,96 € cobrado el 02/09) no están en el «en proceso» de agosto. Sin ellos sale exacto: 7.202,99 €.')]),
      bullet([B('Reembolso sin talón: '), run('00401430766530620260706175838_1-A-1 (49,50 €), enviada y nunca entregada, reembolsada el 25/08 según el conector. Cuenta como rescisión de 602 aunque en Mirakl no tenga talón de abono.')]),
      h2('Corte de fin de mes en las ventas: la venta de 65 € de hombre'),
      par('En 0143 / 602, BC tiene 21 ventas finalizadas por 1.163,97 €; desde Mirakl salían 20 por 1.098,97 €. El detalle de BC confirma que la que falta es 00401430757641420260826172900_1-A-1 (zuecos de hombre, 65,00 €). Se entregó el 31/08 a las 18:47 y la recepción se confirmó a las 23:52. Mirakl fecha el talón de cumplimentación el 01/09, porque ya había pasado el cierre del día, pero ECI la liquida en agosto con fecha 31/08. Para ECI cuenta el día de la recepción, no la fecha del talón. La fila está en Cuadrado y BC la tiene procesada (documento 145645): no hay que hacer nada. Habrá que tenerlo en cuenta al cuadrar septiembre, donde Mirakl la pondrá aunque ECI ya la haya liquidado.'),

      // ================================================================== 7. pendiente
      h1('Peticiones y siguiente paso', true),
      h2('Para IT (Business Central)'),
      numbered('n6')([B('Comisión: '), run('calcular sobre la venta sin IVA del país y el neto de Portugal sin IVA; revisar el 29 % de 696 en España.')]),
      numbered('n6')([B('Conector: '), run('por qué dejó de actualizar los pedidos creados hasta el 28/06; relectura o abonos a mano. Afecta también a julio y probablemente a la venta 124836 (pedido del 15/06): confirmar si no se vincula porque el conector no tiene su talón de cumplimentación del 25/08, y vincularla.')]),
      numbered('n6')([B('Devoluciones antes del reembolso: '), run('BC crea la devolución con la incidencia abierta, antes de saber el importe que reembolsará Mirakl. Revisar cómo se corrige si el reembolso final es distinto.')]),
      numbered('n6')([B('Producto sin relacionar: '), run('qué línea o EAN es en 0143 / 601 y si impide vincular. Puede estar en una línea no liquidable: en España aparece en una fila con una sola rescisión.')]),
      numbered('n6')([B('Pedidos de SAP: '), run('cómo registrar en BC las entregas que ECI liquida de pedidos anteriores al 01/06.')]),
      h2('Para ECI'),
      bullet('Confirmar que Portugal se factura por departamento consolidado en 0143, con las devoluciones de Lisboa y Gaia dentro.'),
      bullet('Gaia: devolución del 10/08 del pedido 00401430751578320260801170207 (219,85 €), que no está registrada en Mirakl.'),
      bullet('Online: abono del 05/08 de la línea 00401430764858020260717201700_1-A-1 (79,95 €), sin reembolso en Mirakl.'),
      bullet('Plazos de las devoluciones en tienda: en las de agosto en Gaia, la mercancía tardó de 5 a 8 semanas en llegar al almacén (R02) y tres aún no han llegado. Mientras tanto Mirakl no refleja el reembolso.'),
      h2('Para el análisis de España (siguiente paso)'),
      bullet('Las mismas causas aparecen en España: líneas sin vincular de pedidos anteriores al conector o congelados, y tramos de devolución sin procesar (6).'),
      bullet('Hay además dos causas propias. En 0011 / 601 el EDI agrupa dos líneas iguales de un pedido en una sola de 2 unidades, que no se puede vincular una a una. Y algunas filas tienen cantidades devueltas imposibles (0037 / 601: −223 unidades en 28 líneas), probablemente un error al importar el campo cantidad.'),
      bullet('El PDF de España solo cuadra con BC por departamento (601: 59.276,57 €; 602: 14.080,85 € más la liquidación negativa de Vigo; 696: 313,48 €), no centro a centro.'),
    ],
  }],
});
Packer.toBuffer(doc).then((buf) => { fs.writeFileSync(OUT, buf); console.log('Escrito', OUT, buf.length, 'bytes'); });
