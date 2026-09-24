const fs = require('fs');
const path = require('path');
const { Document, Packer, Paragraph, TextRun, HeadingLevel, Table, TableRow, TableCell, WidthType, AlignmentType,
        BorderStyle, ShadingType, LevelFormat, PageNumber, Footer, VerticalAlign, TableLayoutType } = require('docx');

const OUT = process.argv[2];
const TOP = JSON.parse(fs.readFileSync(path.join(__dirname, 'ean_top10.json'), 'utf8'));
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
const h1P = (t) => h1(t, true);
const h2 = (t) => new Paragraph({ heading: HeadingLevel.HEADING_2, children: [run(t, { size: 22, bold: true, color: AZUL })] });
const sep = () => par('', { spacing: { after: 80 } });
const B = (t) => run(t, { bold: true });
const numCfg = (ref) => ({ reference: ref, levels: [{ level: 0, format: LevelFormat.DECIMAL, text: '%1.', alignment: AlignmentType.START,
  style: { paragraph: { indent: { left: 500, hanging: 300 } } } }] });

const doc = new Document({
  creator: 'Oriol Terradas', title: 'Errores conector El Corte Inglés',
  styles: {
    default: { document: { run: { font, size: 20 } } },
    paragraphStyles: [
      { id: 'Title', name: 'Title', basedOn: 'Normal', next: 'Normal', run: { font, size: 44, bold: true, color: AZUL }, paragraph: { spacing: { after: 40 } } },
      { id: 'Heading1', name: 'Heading 1', basedOn: 'Normal', next: 'Normal', quickFormat: true, run: { font, size: 28, bold: true, color: AZUL }, paragraph: { spacing: { before: 240, after: 120 }, outlineLevel: 0 } },
      { id: 'Heading2', name: 'Heading 2', basedOn: 'Normal', next: 'Normal', quickFormat: true, run: { font, size: 22, bold: true, color: AZUL }, paragraph: { spacing: { before: 200, after: 80 }, outlineLevel: 1 } },
    ],
  },
  numbering: { config: [
    numCfg('p1'), numCfg('p2'), numCfg('p3'), numCfg('p4'), numCfg('p5'),
    { reference: 'vinetas', levels: [{ level: 0, format: LevelFormat.BULLET, text: '•', alignment: AlignmentType.START,
      style: { paragraph: { indent: { left: 500, hanging: 300 } } } }] },
  ] },
  sections: [{
    properties: { page: { margin: { top: 1134, bottom: 1134, left: 1134, right: 1134 } } },
    footers: { default: new Footer({ children: [new Paragraph({ alignment: AlignmentType.RIGHT, children: [
      run('Errores conector El Corte Inglés · página ', { size: 16, color: '808080' }),
      new TextRun({ children: [PageNumber.CURRENT], font, size: 16, color: '808080' }) ] })] }) },
    children: [
      // ======================================================================= página 1
      new Paragraph({ heading: HeadingLevel.TITLE, children: [run('Errores conector El Corte Inglés', { size: 44, bold: true, color: AZUL })] }),
      par([run('Integración Mirakl (marketplace de ECI) → Business Central · log del conector del 01/06 al 01/09/2026 y export de pedidos de Mirakl del 21/09/2026 · cuadre de agosto de 2026 · 24/09/2026', { size: 18, color: '595959' })], { spacing: { after: 200 } }),

      h1('1. El conector no procesa nada desde el 28 de julio: agosto entero en Pending'),
      par('El conector Mirakl → BC registra cada línea de pedido que recibe de ECI con un estado de proceso (Processed, Error o Pending). Solo ha creado pedidos de venta en tres momentos: ' +
          'junio, el 1 de julio y del 26 al 28 de julio (última línea procesada: 28/07/2026 a las 15:23). Todo lo que ha entrado después está en Pending: ' +
          'las 2.538 líneas de agosto (2.203 pedidos, 145.528,56 €) no tienen pedido de venta en BC, y ECI ya las ha liquidado.'),
      gridTable(['Mes de creación', 'Líneas recibidas', 'Processed (pedido BC creado)', 'Error', 'Pending', 'Comentario'], [
        ['Junio 2026', '4.718', '186', '4.532', '0', 'Se procesó todo; casi todo falló (páginas 2 a 4).'],
        ['Julio 2026', '3.685', '244', '153', '3.288', 'Solo se procesó el 1 de julio y del 26 al 28.'],
        ['Agosto 2026', '2.538', '0', '0', '2.538', 'Nada procesado.'],
        ['Sept. 2026 (hasta el 1/09)', '12', '0', '0', '12', 'Fecha de extracción del log.'],
      ], [1900, 1400, 2000, 1000, 1100, 2238], 17),

      h2('Ejemplo: línea 00100900695760820260801011213_1-A-1 (ECI España, venta a distancia)'),
      kvTable('Datos del pedido en Mirakl (export de pedidos)', [
        ['Producto', 'DONATA-RP · EAN 8434530936584 · Alpargatas de tacón de mujer de rafia con hebilla · 1 unidad · 85,00 €'],
        ['Fechas', 'pedido 01/08/2026 01:12 · aceptado 01:17 · cobrado al cliente 01:40 · enviado 03/08 (Correos Express) · entregado 06/08'],
        ['Talones de ECI', 'venta 06957608 del 01/08 · cumplimentación 92457447 del 06/08 · sin abono ni recogida'],
        ['Estado en Mirakl (21/09)', [B('Recibido'), run(', sin devolución. Entra en la liquidación de agosto de ECI (venta a distancia, mujer).')]],
      ]),
      sep(),
      kvTable('Qué ha hecho el conector (log de BC del 01/09)', [
        ['Estado del proceso', [B('Pending'), run(' desde el 01/08 a las 01:12, hora en que entró en el log')]],
        ['Artículo localizado (Item Found)', '0: el conector ni siquiera ha buscado el EAN en BC'],
        ['Nº de pedido BC', 'Ninguno'],
        ['Mensaje de error', 'Ninguno: no es un fallo, es que no se ha ejecutado'],
      ]),
      h2('Consecuencia y preguntas para IT'),
      par('La venta existe para ECI (liquidada en agosto, con su talón) y no existe en BC. Es la situación de las 2.538 líneas de agosto y de 3.288 de julio. ' +
          'Hasta que el conector no vuelva a ejecutarse, el cuadre de ECI con BC no puede empezar.'),
      bullet('¿Cómo se lanza el proceso: tarea programada, cola de trabajos o a mano? ¿Qué pasó el 28 de julio? Las tres ejecuciones con resultado parecen pruebas manuales.'),
      bullet('Cuando se reactive, ¿procesará las 5.838 líneas pendientes (julio, agosto y septiembre) o solo las nuevas?'),
      bullet('Pedimos una fecha y hora de proceso en el log: hoy solo se ve el estado, no cuándo se intentó.'),

      // ======================================================================= página 2
      h1P('2. Cliente C0001883 sin grupo de registro: 3.262 líneas rechazadas por BC'),
      par('En junio y el 1 de julio, BC rechazó todas las líneas de ECI España con el mensaje «Grupo registro cliente debe tener un valor en Cliente: Nº=C0001883. No puede ser cero ni estar vacío». ' +
          'C0001883 es la ficha de cliente de El Corte Inglés España en BC (la misma a la que se facturan las liquidaciones) y no tenía informado el grupo de registro de cliente. ' +
          'Son 3.262 líneas de 2.927 pedidos, 197.947,37 €. El artículo sí se encontró en todas (Item Found = 1): el fallo es solo de configuración del cliente.'),

      h2('Ejemplo: línea 00100900692610120260617183430_1-A-1'),
      kvTable('Datos del pedido en Mirakl', [
        ['Producto', 'ROMINA · EAN 8434530004641 · Alpargatas de cuña de mujer de tejido con hebilla · 1 unidad · 65,00 €'],
        ['Fechas', 'pedido 17/06/2026 18:34 · enviado 17/06 23:57 · entregado 19/06 · talón de cumplimentación 95923959 del 19/06'],
        ['Devolución', 'abono y recogida el 30/06/2026, 65,00 € (talón de abono 01233058)'],
        ['Estado en Mirakl (21/09)', [B('Reembolsado')]],
      ]),
      sep(),
      kvTable('Qué hizo el conector', [
        ['Estado del proceso', [B('Error'), run(' · artículo localizado (Item Found = 1) · nº de pedido BC: ninguno')]],
        ['Mensaje de BC', [run('«Grupo registro cliente debe tener un valor en Cliente: Nº=C0001883. No puede ser cero ni estar vacío.»', { italics: true })]],
        ['Proceso de la devolución', 'Pending: nunca se intentó, porque no hay pedido que abonar'],
      ]),
      h2('Cronología'),
      numbered('p2')('17/06 — el pedido entra en Mirakl y en el log de BC; el conector intenta crear el pedido de venta y BC lo rechaza por el cliente.'),
      numbered('p2')('19/06 — Toni Pons lo entrega; ECI lo cuenta como venta en la liquidación de junio.'),
      numbered('p2')('30/06 — el cliente lo devuelve; ECI lo abona y lo resta en la liquidación de junio.'),
      numbered('p2')('26/07 — el error ya no aparece en las ejecuciones posteriores: la ficha del cliente se corrigió, pero ninguna de las 3.262 líneas se volvió a procesar.'),
      h2('Consecuencia y preguntas para IT'),
      par('Faltan en BC 197.947,37 € de ventas de junio (todas las de España), y 642 de esas líneas ya están devueltas en Mirakl, así que necesitarán pedido y abono. ' +
          'La corrección de la ficha no sirve de nada si no se reprocesan las líneas en error.'),
      bullet('¿Se pueden reprocesar en bloque las líneas en Error una vez corregida la causa? Hoy el log no tiene esa acción.'),
      bullet('Comprobar que la ficha de ECI Portugal (C0010835) tiene también grupo de registro: en junio no falló porque sus líneas cayeron en otros errores.'),

      // ======================================================================= página 3
      h1P('3. Serie de numeración V-DEV sin números: ninguna devolución llega a BC'),
      par('Cuando el conector detecta una devolución en Mirakl intenta crear la devolución de venta en BC. En junio, 832 líneas fallaron con «No puede asignar números nuevos de la serie V-DEV»: ' +
          'la serie de numeración de las devoluciones de venta no tiene números libres o no tiene línea válida para la fecha. Desde julio el conector ni siquiera lo intenta (proceso de devolución Pending en 9.998 líneas). ' +
          'Resultado: en todo el log hay 2.810 líneas con devolución detectada, 2.144 reembolsadas por 134.130,94 €, y cero devoluciones creadas en BC (la columna «BC Return Order No.» está vacía en las 10.953 líneas).'),

      h2('Ejemplo: línea 00100900628939320260610015030_1-A-1'),
      kvTable('Datos del pedido en Mirakl', [
        ['Producto', 'BRIANA · EAN 8434530692091 · Alpargatas de cuña de mujer de tejido con elásticos · 1 unidad · 47,96 €'],
        ['Fechas', 'pedido 10/06/2026 01:50 · recogida en centro comercial · entregado 12/06 · talón de cumplimentación 07699558 del 13/06'],
        ['Devolución', 'abono y recogida el 16/06/2026, 47,96 € (talón de abono 01174607) · motivo en el log: REFUND_04'],
        ['Estado en Mirakl (21/09)', [B('Reembolsado')]],
      ]),
      sep(),
      kvTable('Qué hizo el conector', [
        ['Estado del proceso del pedido', [B('Error'), run(' · nº de pedido BC: ninguno')]],
        ['Estado del proceso de la devolución', [B('Error'), run(' · importe del reembolso detectado: 47,96 € · nº de devolución BC: ninguno')]],
        ['Mensaje de BC', [run('«No puede asignar números nuevos de la serie V-DEV.»', { italics: true })]],
        ['Observación', 'El log tiene una sola columna de mensaje para el pedido y la devolución: el error de la devolución ha tapado el del pedido.'],
      ]),
      h2('Consecuencia y preguntas para IT'),
      par('Ninguna devolución de ECI existe en BC. De los 382 pedidos que sí se crearon en BC (junio y julio), 68 líneas por 4.711,73 € están ya devueltas en Mirakl y no tienen abono en BC. ' +
          'ECI, en cambio, resta cada devolución en la liquidación del mes en que la abona.'),
      bullet('Revisar la serie V-DEV: líneas de numeración, último número usado y fecha de inicio. Después, reintentar las 832 líneas.'),
      bullet('Confirmar el flujo previsto: ¿devolución de venta más abono, o abono directo? ¿Qué pasa con las devoluciones de pedidos que nunca se crearon en BC (páginas 2 y 4)?'),
      bullet('Separar en el log el mensaje de error del pedido y el de la devolución.'),

      // ======================================================================= página 4
      h1P('4. 380 EAN que el conector no encuentra en BC: 607 líneas'),
      par('«This Mirakl order contains lines with missing SKU/barcode mapping»: el conector busca el EAN de la línea (SKU en Mirakl) en los códigos de barras de BC y no lo encuentra. ' +
          'Afecta a 484 líneas de pedido (403 pedidos, 29.977,65 €) y a 123 líneas de devolución (108 pedidos, 7.636,31 €), sobre 380 EAN distintos, todos de 13 dígitos. ' +
          'Solo 6 de esos 380 EAN aparecen en alguna línea procesada, o sea, casi ninguno existe en BC. Basta una línea sin mapear para que falle el pedido entero: 74 líneas con el artículo localizado cayeron por otra línea del mismo pedido. ' +
          'Sigue pasando en las últimas ejecuciones (15 líneas del 26 al 28 de julio).'),

      h2('Ejemplo: línea 00100900678455420260615231601_1-A-1'),
      kvTable('Datos del pedido en Mirakl y respuesta del conector', [
        ['Producto', 'FLORINA · EAN 8434530860612 · Alpargatas de cuña de mujer de tejido · 1 unidad · 69,95 €'],
        ['Fechas', 'pedido 15/06/2026 23:16 · enviado 16/06 · entregado 17/06 · talón de cumplimentación 95761742 del 17/06 · estado Recibido'],
        ['Conector', [B('Error'), run(' · Item Found = 0 · «This Mirakl order contains lines with missing SKU/barcode mapping.» · nº de pedido BC: ninguno')]],
        ['Misma causa en devoluciones', 'línea 00100900678178120260611185220_1-A-1, ETNA EAN 8434530002364, 69,95 € reembolsados el 17/06: «This Mirakl return contains lines with missing SKU/barcode mapping.»'],
      ]),
      h2('Los diez EAN con más líneas afectadas (lista completa en el Excel «EAN sin mapear ECI»)'),
      gridTable(['EAN', 'Descripción en Mirakl', 'Líneas'], TOP.map((t) => [t.ean, t.titulo, String(t.lineas)]), [2000, 6638, 1000], 17),
      h2('Consecuencia y preguntas para IT'),
      par('Es el mismo síntoma que en Channel Engine («Order has product mapping errors»): faltan artículos o variantes con su código de barras en BC. Mientras no estén, esos pedidos no se pueden crear ni reprocesar.'),
      bullet('¿El mapeo va por código de barras de la variante o por referencia? ¿Qué falta exactamente para estos 380 EAN: el artículo, la variante o el código?'),
      bullet('Cargar los EAN que faltan y reprocesar las 607 líneas; el mensaje debería indicar qué EAN falla.'),

      // ======================================================================= página 5
      h1P('5. Pedidos cancelados o rechazados que sí tienen pedido de venta en BC'),
      par('Un pedido de Mirakl pasa por «pendiente de cobro» antes de quedar aceptado; si ECI no consigue cobrar al cliente, la línea se cancela (motivos «No debitado» y «Expiración del plazo de débito»). ' +
          'También puede cancelarla el cliente, o rechazarla la tienda (Toni Pons) si no puede servirla. En las ejecuciones de julio el conector creó 6 pedidos de venta en BC ' +
          'para 7 líneas que hoy están canceladas o rechazadas en Mirakl, 412,72 €: son pedidos en BC que nunca se van a servir ni a cobrar.'),
      gridTable(['Nº pedido Mirakl', 'Canal', 'Producto', 'Importe', 'Estado y motivo en Mirakl', 'Nº pedido BC'], [
        ['00401430769767320260627130322_2-A', 'PT', 'SILVIA-S, sandalias de cuña', '65,00 €', 'Cancelado · cancelado (27/06)', '124964'],
        ['00100900675354620260726122835_1-A', 'ES', 'BASILEA, sandalias planas (2 líneas)', '139,90 €', 'Cancelado · expiración del plazo de débito', '125875'],
        ['00100900698019020260726132211_1-A', 'ES', 'FLORA, alpargatas planas', '69,95 €', 'Rechazado · rechazado por la tienda (26/07)', '125940'],
        ['00100900688614320260727074807_1-A', 'ES', 'SOMNI, zapatillas de casa', '39,96 €', 'Cancelado · no debitado', '125908'],
        ['00100900616344420260727120703_2-A', 'ES', 'MELY-AR, zapatillas de casa', '27,96 €', 'Cancelado · cancelado (27/07)', '125778'],
        ['00100900622692920260727135600_1-A', 'ES', 'DIXON, alpargatas de hombre', '69,95 €', 'Cancelado · no debitado', '125796'],
      ], [3400, 600, 2100, 900, 1938, 700], 16),
      h2('Cronología del pedido 00100900675354620260726122835_1-A (dos pares de BASILEA)'),
      numbered('p5')('26/07 12:28 — el pedido entra en Mirakl y en el log de BC; 12:33 queda aceptado, pendiente del cobro al cliente.'),
      numbered('p5')('26/07 a 28/07 — el conector lo procesa y crea el pedido de venta 125875 en BC.'),
      numbered('p5')('Días después — ECI no consigue cobrar («expiración del plazo de débito») y Mirakl cancela las dos líneas. Nunca se envía nada.'),
      numbered('p5')('01/09 — en el log el estado de Mirakl ya es CANCELED, pero el pedido 125875 sigue en BC como si fuera a servirse.'),
      h2('Consecuencia y preguntas para IT'),
      par('Son pocos casos porque el conector ha procesado poco, pero la regla afecta a todos los meses: en agosto Mirakl tiene 89 líneas canceladas o rechazadas (5.122,82 €) que el conector no debe crear cuando se reactive. ' +
          'El rechazo por la tienda (125940) es el caso más llamativo: Toni Pons rechazó la línea y BC creó el pedido igualmente.'),
      bullet('Crear el pedido en BC solo cuando la línea esté cobrada y aceptada (estado RECEIVED en Mirakl), no antes.'),
      bullet('Procesar los cambios de estado posteriores: una línea CANCELED o REFUSED con pedido en BC debe cancelar ese pedido (o la línea) automáticamente.'),
      bullet('Revisar y cerrar a mano los 6 pedidos de la tabla.'),
    ],
  }],
});
Packer.toBuffer(doc).then((buf) => { fs.writeFileSync(OUT, buf); console.log('Escrito', OUT, buf.length, 'bytes'); });
