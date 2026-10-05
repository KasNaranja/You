// RESUMEN LIQUIDACION BC — presentación del cuadre de la liquidación ECI Portugal (agosto 2026)
const pptxgen = require('pptxgenjs');
const { applyTheme } = require(process.argv[3]);
const OUT = process.argv[2];

const THEME = {
  name: 'Liquidacion ECI',
  headFontFace: 'Calibri',
  bodyFontFace: 'Calibri',
  colors: {
    dk1: '1F2933', lt1: 'FFFFFF', dk2: '1F4E78', lt2: 'EEF3F8',
    accent1: '1F4E78', accent2: '2E7D4F', accent3: 'B3261E', accent4: 'C98A00', accent5: '6B7785', accent6: '4F81BD',
    hlink: '1F4E78', folHlink: '6B4C9A',
  },
};
// tintes (hex) para fondos suaves de tabla y tarjetas
const VERDE_T = 'E3F2E8', ROJO_T = 'FBE5E3', GRIS_T = 'EDEFF2', AZUL_T = 'EEF3F8';

const pres = new pptxgen();
pres.layout = 'LAYOUT_WIDE'; // 13.33 x 7.5
pres.theme = { headFontFace: THEME.headFontFace, bodyFontFace: THEME.bodyFontFace };
pres.title = 'RESUMEN LIQUIDACION BC';
pres.subject = 'Liquidación ECI Portugal, agosto 2026: PDF de ECI frente a Business Central';
pres.author = 'Oriol Terradas';
const C = pres.SchemeColor;

pres.defineSlideMaster({
  title: 'TITULO',
  background: { color: 'FFFFFF' },
  margin: [0.5, 0.6, 0.6, 0.6],
  objects: [
    { placeholder: { options: { name: 'title', type: 'title', x: 0.6, y: 0.35, w: 12.1, h: 0.75, fontSize: 30, bold: true, color: C.accent1, valign: 'middle', align: 'left', margin: 0 }, text: '' } },
    { placeholder: { options: { name: 'body', type: 'body', x: 0.6, y: 1.1, w: 12.1, h: 0.45, fontSize: 15, color: C.accent5, valign: 'top', margin: 0 }, text: '' } },
    { text: { text: 'Liquidación ECI Portugal · agosto 2026', options: { x: 0.6, y: 7.0, w: 8, h: 0.3, fontSize: 10, color: C.accent5, margin: 0 } } },
  ],
  slideNumber: { x: 12.3, y: 7.0, w: 0.5, h: 0.3, fontSize: 10, color: '6B7785', align: 'right' },
});

const card = (slide, x, y, w, h, fill, name) => slide.addShape(pres.shapes.ROUNDED_RECTANGLE,
  { x, y, w, h, fill: { color: fill }, line: { color: fill }, rectRadius: 0.08, objectName: name });
const txt = (slide, text, o) => slide.addText(text, { isTextBox: true, margin: 0, fontFace: THEME.bodyFontFace, color: C.text1, ...o });

// ===================================================================== 1. cuadro PDF vs BC
pres.addSection({ title: 'Resumen' });
{
  const s = pres.addSlide({ masterName: 'TITULO', sectionTitle: 'Resumen' });
  s.addText('Columnas del PDF de ECI frente a Business Central', { placeholder: 'title' });
  s.addText('ECI Portugal, agosto 2026 · total de los tres departamentos (601 mujer, 602 hombre, 696 niños)', { placeholder: 'body' });
  const H = (t, align = 'left') => ({ text: t, options: { bold: true, color: 'FFFFFF', fill: { color: '1F4E78' }, align, valign: 'middle' } });
  const filas = [
    ['Venta total con IVA', 'VENDA TOTAL', 'Importe liquidable', '6.006,15', '6.006,15', '0,00', 'ok'],
    ['Venta neta sin IVA', 'NETA', 'Base imponible comisión', '4.883,05', '5.972,19', '+1.089,14', 'dif'],
    ['IVA de la venta (23 %)', 'IVA (23.00)', 'No existe en BC', '1.123,10', '—', '—', 'na'],
    ['% participación ECI', '%', 'Comisión esperada / base', '29 %', '29,00 %', '0', 'ok'],
    ['Participación ECI', 'PARTICIP.ECI EUROS', 'Comisión esperada', '1.416,09', '1.731,97', '+315,88', 'dif'],
    ['Importe a facturar', 'A FACTURAR IMPORTE', 'Importe neto esperado', '3.466,96', '4.274,18', '+807,22', 'dif'],
    ['IVA a facturar (0 %)', 'IVA (0.00)', 'IVA comisión esperado', '0,00', '0,00', '0,00', 'ok'],
    ['Total factura', 'TOTAL FRA', 'Importe neto esperado', '3.466,96', '4.274,18', '+807,22', 'dif'],
  ];
  const fondo = { ok: VERDE_T, dif: ROJO_T, na: GRIS_T };
  const rows = [[H('Columna PDF'), H('Nombre en el PDF'), H('Campo en BC'), H('Total PDF', 'right'), H('Total BC', 'right'), H('Total dif.', 'right')]];
  filas.forEach((f, i) => {
    const bold = i === filas.length - 1;
    const base = { fill: { color: fondo[f[6]] }, valign: 'middle', bold };
    rows.push([
      { text: f[0], options: { ...base, bold: true } },
      { text: f[1], options: { ...base, color: '6B7785' } },
      { text: f[2], options: base },
      { text: f[3], options: { ...base, align: 'right' } },
      { text: f[4], options: { ...base, align: 'right' } },
      { text: f[5], options: { ...base, align: 'right', bold: true, color: f[6] === 'dif' ? 'B3261E' : (f[6] === 'ok' ? '2E7D4F' : '6B7785') } },
    ]);
  });
  s.addTable(rows, {
    x: 0.6, y: 1.75, w: 12.1, colW: [2.7, 2.3, 2.7, 1.45, 1.45, 1.5], rowH: 0.47, fontSize: 15, fontFace: 'Calibri', color: '1F2933',
    border: { type: 'solid', pt: 0.75, color: 'FFFFFF' }, objectName: 'cuadro PDF vs BC',
  });
  txt(s, [
    { text: 'BC', options: { bold: true } },
    { text: ' = suma de los centros 0140 + 0142 + 0143 del informe «liquidación mensual ECI mes 8 datos». ' },
    { text: 'Diferencia', options: { bold: true } },
    { text: ' = BC − PDF. Verde: coincide. Rojo: diferencia. Gris: BC no tiene el dato.' },
  ], { x: 0.6, y: 6.15, w: 12.1, h: 0.55, fontSize: 12, color: C.accent5, valign: 'top' });
  s.addNotes('Solo coincide la venta con IVA. BC no quita el IVA portugués del 23 %, así que calcula la comisión y el neto sobre una base más alta: 315,88 € más de comisión y 807,22 € más de neto que lo que se factura a ECI (facturas 260007291, 260007292 y 260007293, 3.466,96 €). El campo IVA comisión esperado de BC es el IVA de la comisión, no el de la factura. Base de BC 5.972,19 = 6.006,15 − 33,96 de líneas sin vincular, que BC deja fuera.');
}

// ===================================================================== 2. mensaje principal
{
  const s = pres.addSlide({ masterName: 'TITULO', sectionTitle: 'Resumen' });
  s.addText('La venta cuadra al céntimo; la comisión y el neto no', { placeholder: 'title' });
  s.addText('Los importes EDI que tiene BC son los que liquida ECI. Las diferencias están en el cálculo de BC y en el vínculo con Mirakl', { placeholder: 'body' });
  const stats = [
    ['0,00 €', 'diferencia en la venta con IVA', '6.006,15 € en el PDF y en BC (centros 0140 + 0142 + 0143)', '2E7D4F', VERDE_T],
    ['+807,22 €', 'neto esperado de BC por encima de lo facturado', 'BC calcula comisión y neto sobre el importe con IVA', 'B3261E', ROJO_T],
    ['7 líneas', 'EDI sin vincular con Mirakl', 'Pedidos anteriores al conector o congelados en él (neto 33,96 €)', 'C98A00', 'FFF4D6'],
    ['299,80 €', '4 devoluciones sin procesar en BC', 'ECI las abona, pero en Mirakl no hay devolución', 'C98A00', 'FFF4D6'],
  ];
  stats.forEach(([big, lab, det, col, bg], i) => {
    const x = 0.6 + i * 3.1;
    card(s, x, 1.9, 2.85, 3.75, bg, `tarjeta ${i + 1}`);
    txt(s, big, { x: x + 0.25, y: 2.25, w: 2.35, h: 1.1, fontSize: 40, bold: true, color: col, fontFace: THEME.headFontFace, valign: 'middle', fit: 'shrink' });
    txt(s, lab, { x: x + 0.25, y: 3.45, w: 2.35, h: 0.95, fontSize: 17, bold: true, valign: 'top' });
    txt(s, det, { x: x + 0.25, y: 4.45, w: 2.35, h: 1.5, fontSize: 14, color: C.accent5, valign: 'top' });
  });
}

// ===================================================================== 3. comisión
pres.addSection({ title: 'Motivos' });
{
  const s = pres.addSlide({ masterName: 'TITULO', sectionTitle: 'Motivos' });
  s.addText('BC calcula la comisión sobre el importe con IVA', { placeholder: 'title' });
  s.addText('ECI quita antes el IVA portugués del 23 % y Toni Pons factura sin IVA', { placeholder: 'body' });
  card(s, 0.6, 1.85, 5.6, 2.05, AZUL_T, 'cálculo ECI');
  txt(s, 'Cómo calcula ECI (PDF)', { x: 0.85, y: 2.0, w: 5.1, h: 0.4, fontSize: 18, bold: true, color: C.accent1 });
  txt(s, [
    { text: 'Neta = venta con IVA / 1,23', options: { bullet: true, breakLine: true } },
    { text: 'Participación = 29 % de la neta', options: { bullet: true, breakLine: true } },
    { text: 'A facturar = neta − participación, sin IVA', options: { bullet: true } },
  ], { x: 0.85, y: 2.45, w: 5.1, h: 1.35, fontSize: 15, paraSpaceAfter: 4, valign: 'top' });
  card(s, 0.6, 4.1, 5.6, 2.05, ROJO_T, 'cálculo BC');
  txt(s, 'Cómo calcula BC', { x: 0.85, y: 4.25, w: 5.1, h: 0.4, fontSize: 18, bold: true, color: C.accent3 });
  txt(s, [
    { text: 'Comisión esperada = 29 % del importe con IVA vinculado', options: { bullet: true, breakLine: true } },
    { text: 'Neto esperado = importe con IVA − comisión', options: { bullet: true, breakLine: true } },
    { text: 'En España también: 29 % en niños (ECI aplica 30 %)', options: { bullet: true } },
  ], { x: 0.85, y: 4.7, w: 5.1, h: 1.35, fontSize: 15, paraSpaceAfter: 4, valign: 'top' });
  s.addChart(pres.charts.BAR, [
    { name: 'A facturar (ECI)', labels: ['601 mujer', '602 hombre', '696 niños'], values: [2841.57, 566.59, 58.80] },
    { name: 'Neto esperado (BC)', labels: ['601 mujer', '602 hombre', '696 niños'], values: [3504.98, 696.88, 72.32] },
  ], {
    x: 6.6, y: 1.85, w: 6.1, h: 4.3, barDir: 'col', barGrouping: 'clustered', barGapWidthPct: 80, barOverlapPct: -20, chartColors: ['1F4E78', 'B3261E'],
    showTitle: true, title: 'Importe a facturar por departamento (€)', titleFontSize: 14, titleColor: '1F2933', titleFontFace: '+mn-lt',
    showValue: true, dataLabelPosition: 'outEnd', dataLabelFontSize: 11, dataLabelFontFace: '+mn-lt', dataLabelColor: '1F2933', dataLabelFormatCode: '#,##0.00',
    catAxisLabelColor: '6B7785', valAxisLabelColor: '6B7785', catAxisLabelFontFace: '+mn-lt', valAxisLabelFontFace: '+mn-lt', catAxisLabelFontSize: 12, valAxisLabelFontSize: 11,
    valGridLine: { color: 'E1E5EA', size: 0.5 }, catGridLine: { style: 'none' }, showLegend: true, legendPos: 'b', legendFontSize: 12, legendFontFace: '+mn-lt',
    objectName: 'gráfico a facturar vs neto',
  });
  s.addNotes('Total Portugal: a facturar según ECI 3.466,96 €; neto esperado BC 4.274,18 €; diferencia 807,22 € = IVA no descontado 1.123,10 € − exceso de comisión 315,88 €. Petición a IT: calcular la comisión sobre la venta neta del IVA del país y el neto de Portugal sin IVA; revisar el 29 % de 696 en España.');
}

// ===================================================================== 4. sin vincular
{
  const s = pres.addSlide({ masterName: 'TITULO', sectionTitle: 'Motivos' });
  s.addText('7 líneas EDI sin vincular: pedidos de antes de julio', { placeholder: 'title' });
  s.addText('BC no las vincula con Mirakl y las deja fuera de la base de comisión', { placeholder: 'body' });
  const bloques = [
    ['A', 'Ventas de pedidos de enero a junio', '220,82 €', '4 ventas en 0143 mujer',
      ['3 entregas de pedidos de enero, febrero y mayo, registrados en SAP (160,87 €)', '1 pedido del 15/06 que BC ya tiene como venta 124836, pero no vincula (59,95 €)']],
    ['B', 'Pedidos congelados en el conector', '−186,86 €', '3 devoluciones (0143 y Gaia)',
      ['Pedidos creados hasta el 28/06: el conector dejó de actualizarlos el 29-30/06', 'No ve sus devoluciones y no crea el tramo (79,95 + 71,96 + 34,95 €)']],
  ];
  bloques.forEach(([letra, tit, imp, sub, puntos], i) => {
    const x = 0.6 + i * 6.2;
    card(s, x, 1.85, 5.9, 4.0, AZUL_T, `causa ${letra}`);
    s.addShape(pres.shapes.OVAL, { x: x + 0.3, y: 2.1, w: 0.65, h: 0.65, fill: { color: '1F4E78' }, line: { color: '1F4E78' }, objectName: `icono ${letra}` });
    txt(s, letra, { x: x + 0.3, y: 2.1, w: 0.65, h: 0.65, fontSize: 22, bold: true, color: 'FFFFFF', align: 'center', valign: 'middle' });
    txt(s, tit, { x: x + 1.15, y: 2.1, w: 4.5, h: 0.65, fontSize: 19, bold: true, color: C.accent1, valign: 'middle' });
    txt(s, imp, { x: x + 0.3, y: 2.95, w: 5.3, h: 0.75, fontSize: 34, bold: true, color: C.accent4, fontFace: THEME.headFontFace });
    txt(s, sub, { x: x + 0.3, y: 3.7, w: 5.3, h: 0.4, fontSize: 15, color: C.accent5 });
    txt(s, puntos.map((p, k) => ({ text: p, options: { bullet: true, breakLine: k < puntos.length - 1 } })),
      { x: x + 0.3, y: 4.2, w: 5.3, h: 1.5, fontSize: 15, paraSpaceAfter: 6, valign: 'top' });
  });
  txt(s, [{ text: 'Seguirá pasando: ', options: { bold: true } }, { text: 'en julio hay al menos 12 devoluciones más de pedidos congelados, que saldrán sin vincular en la liquidación de julio.' }],
    { x: 0.6, y: 6.05, w: 12.1, h: 0.4, fontSize: 15, color: C.accent3 });
  s.addNotes('Ventas sin vincular (0143/601): 00401430766493020260112191028_1-A-1 (26,96), 00401430762747320260220131747_1-A-2 (63,96), 00401430760456120260512181250_1-A-1 (69,95) y 00401430752499520260615175342_1-A-1 (59,95, venta BC 124836). Devoluciones sin vincular: 00401430758314520260624160644_1-A-1 (79,95, online), 00401430753352420260626123836_1-A-1 (71,96, online) y 00401430750680520260627151042_1-A-2 (34,95, Gaia). Neto sin vincular: 0143/601 = 220,82 − 151,91 = +68,91 €; 0142/601 = −34,95 €. Petición a IT: por qué el conector dejó de refrescar los pedidos creados hasta el 28/06; por qué la venta 124836 no se vincula; cómo registrar en BC las entregas de pedidos de SAP.');
}

// ===================================================================== 5. sin procesar
{
  const s = pres.addSlide({ masterName: 'TITULO', sectionTitle: 'Motivos' });
  s.addText('4 devoluciones sin procesar: ECI las abona y Mirakl no las tiene', { placeholder: 'title' });
  s.addText('BC solo crea la devolución si existe en Mirakl. Las 4 están en el EDI de ECI, pero no en Mirakl', { placeholder: 'body' });
  const casos = [
    ['0142 Gaia · 3 líneas', '219,85 €', 'Pedido ', '00401430751578320260801170207',
      ['Según el EDI, la clienta devolvió los 3 pares en la tienda de Gaia el 10/08', 'En Mirakl el pedido sigue «Recibido»: sin devolución, sin incidencia y sin mensajes']],
    ['0143 online · 1 línea', '79,95 €', 'Línea ', '00401430764858020260717201700_1-A-1',
      ['El EDI del 05/08 abona las 2 líneas del pedido: esta y la de 75 €', 'Mirakl solo reembolsó la de 75 €; esta sigue «Recibido»']],
  ];
  casos.forEach(([tit, imp, etq, ped, puntos], i) => {
    const x = 0.6 + i * 6.2;
    card(s, x, 1.85, 5.9, 2.65, 'FFF4D6', `caso sin procesar ${i + 1}`);
    txt(s, tit, { x: x + 0.3, y: 2.0, w: 3.2, h: 0.45, fontSize: 17, bold: true, color: C.accent1, valign: 'middle' });
    txt(s, imp, { x: x + 3.4, y: 1.95, w: 2.2, h: 0.55, fontSize: 28, bold: true, color: C.accent4, align: 'right', valign: 'middle', fontFace: THEME.headFontFace });
    txt(s, [{ text: etq, options: { color: C.accent5 } }, { text: ped, options: { bold: true } }], { x: x + 0.3, y: 2.6, w: 5.3, h: 0.4, fontSize: 14 });
    txt(s, puntos.map((p, k) => ({ text: p, options: { bullet: true, breakLine: k < puntos.length - 1 } })),
      { x: x + 0.3, y: 3.1, w: 5.3, h: 1.3, fontSize: 15, paraSpaceAfter: 6, valign: 'top' });
  });
  card(s, 0.6, 4.8, 12.1, 1.15, AZUL_T, 'petición ECI sin procesar');
  txt(s, [
    { text: 'Qué pedir a ECI: ', options: { bold: true, color: C.accent1 } },
    { text: 'si las devoluciones se hicieron, el talón de abono y registrarlas en Mirakl para poder recoger la mercancía. Si no se hicieron, regularizar los 299,80 € en la liquidación.' },
  ], { x: 0.9, y: 4.9, w: 11.5, h: 0.95, fontSize: 15, valign: 'middle' });
  s.addNotes('Identificadas con el detalle de la comparación operativa de BC (filas 0142/601 y 0143/601). Gaia: informe EDI 20260811035705067032352, líneas 1, 2 y 4; EAN 8434530939677, 8434530688612 y 8434530872639; talón de venta 07515783; BC las vincula por el talón de venta porque no hay talón de abono. Online: informe EDI 20260806042406067032352; EAN 8434530946972; la hermana 2-A-1 (75 €, talón de abono 92363569) sí está procesada (documento 6245). Las 7 incidencias abiertas de Gaia sí están procesadas en BC.');
}

// ===================================================================== 6. tiendas
{
  const s = pres.addSlide({ masterName: 'TITULO', sectionTitle: 'Motivos' });
  s.addText('Devoluciones en tienda: BC las separa, ECI las junta en 0143', { placeholder: 'title' });
  s.addText('El PDF de Portugal solo trae el centro 0143, que es la suma de los tres centros de BC', { placeholder: 'body' });
  s.addChart(pres.charts.BAR, [
    { name: 'Devoluciones (€)', labels: ['0143 online', '0140 Lisboa', '0142 Gaia'], values: [657.08, 658.76, 772.92] },
  ], {
    x: 0.6, y: 1.85, w: 6.4, h: 4.3, barDir: 'bar', chartColors: ['1F4E78'],
    showTitle: true, title: 'Devoluciones de agosto por centro en BC (€)', titleFontSize: 14, titleColor: '1F2933', titleFontFace: '+mn-lt',
    showValue: true, dataLabelPosition: 'outEnd', dataLabelFontSize: 12, dataLabelFontFace: '+mn-lt', dataLabelColor: '1F2933', dataLabelFormatCode: '#,##0.00',
    catAxisLabelColor: '6B7785', valAxisLabelColor: '6B7785', catAxisLabelFontFace: '+mn-lt', valAxisLabelFontFace: '+mn-lt', catAxisLabelFontSize: 13, valAxisLabelFontSize: 11,
    valGridLine: { color: 'E1E5EA', size: 0.5 }, catGridLine: { style: 'none' }, showLegend: false, valAxisMaxVal: 1000,
    objectName: 'gráfico devoluciones por centro',
  });
  const pts = [
    ['Dónde va cada devolución', 'BC y EDI la ponen en la tienda donde se hizo el abono; ECI la liquida en 0143.'],
    ['Cómo se reconoce la tienda', 'Por la caja: 4 primeros dígitos del talón de abono. Lisboa 0247, 0359, 0558, 0559, 0561; Gaia 0265, 0266, 0269, 0617; online empieza por 9.'],
    ['Qué implica', 'Las filas de BC por centro no se comparan una a una con el PDF: hay que sumar por departamento.'],
  ];
  pts.forEach(([t, d], i) => {
    const y = 1.85 + i * 1.47;
    card(s, 7.3, y, 5.4, 1.32, i === 2 ? 'FFF4D6' : AZUL_T, `punto tiendas ${i + 1}`);
    txt(s, t, { x: 7.55, y: y + 0.12, w: 4.95, h: 0.38, fontSize: 16, bold: true, color: C.accent1 });
    txt(s, d, { x: 7.55, y: y + 0.5, w: 4.95, h: 0.75, fontSize: 13.5, valign: 'top' });
  });
  s.addNotes('0140 Lisboa: 9 líneas mujer (622,80 €) + 1 niños (35,96 €). 0142 Gaia: 13 líneas (772,92 €), todas identificadas con el detalle de BC. 0143 online: 8 líneas mujer (474,67 €) + 3 hombre (182,41 €). Las ventas finalizadas y las rescisiones van siempre al centro del pedido (0143). Pregunta a ECI: confirmar que Portugal se factura por departamento consolidado.');
}

// ===================================================================== 7. R01 / R02 / R03
{
  const s = pres.addSlide({ masterName: 'TITULO', sectionTitle: 'Motivos' });
  s.addText('Devolución en tienda: cada sistema la registra en un paso distinto', { placeholder: 'title' });
  s.addText('ECI la liquida con la R01, BC la crea con la incidencia y Mirakl reembolsa con la R03, semanas después', { placeholder: 'body' });
  const pasos = [
    ['R01', 'Devolución en tienda', 'El cliente devuelve en una tienda de ECI y le abonan por el TPV. Mirakl abre una incidencia.',
      [['ECI', 'la liquida ese mes'], ['BC', 'puede crear la devolución']]],
    ['R02', 'Llega al almacén', 'La mercancía llega al almacén de MRW. En las devoluciones de agosto en Gaia tardó de 5 a 8 semanas, y tres aún no han llegado.', []],
    ['R03', 'Toni Pons la recoge', 'Se cierra la devolución.', [['Mirakl', 'hace el reembolso']]],
  ];
  s.addShape(pres.shapes.LINE, { x: 1.4, y: 2.35, w: 9.9, h: 0, line: { color: '6B7785', width: 2, endArrowType: 'triangle' }, objectName: 'línea de tiempo' });
  pasos.forEach(([cod, tit, det, quien], i) => {
    const x = 0.6 + i * 4.15;
    s.addShape(pres.shapes.OVAL, { x: x + 0.3, y: 1.9, w: 0.9, h: 0.9, fill: { color: '1F4E78' }, line: { color: 'FFFFFF', width: 3 }, objectName: `paso ${cod}` });
    txt(s, cod, { x: x + 0.3, y: 1.9, w: 0.9, h: 0.9, fontSize: 18, bold: true, color: 'FFFFFF', align: 'center', valign: 'middle' });
    card(s, x, 3.0, 3.85, 2.75, AZUL_T, `detalle ${cod}`);
    txt(s, tit, { x: x + 0.25, y: 3.12, w: 3.35, h: 0.45, fontSize: 18, bold: true, color: C.accent1 });
    txt(s, det, { x: x + 0.25, y: 3.6, w: 3.35, h: 1.15, fontSize: 14, valign: 'top' });
    quien.forEach(([sis, que], k) => {
      txt(s, [{ text: sis + ' ', options: { bold: true, color: C.accent2 } }, { text: que }],
        { x: x + 0.25, y: 4.8 + k * 0.42, w: 3.35, h: 0.38, fontSize: 15 });
    });
  });
  txt(s, [
    { text: 'Ejemplo, pedido 00401430750813420260714121528: ', options: { bold: true } },
    { text: 'R01 el 27/07, R02 el 24/08 y R03 el 31/08. Mirakl hace el reembolso el 31/08, pero ECI no lo liquida en agosto porque la R01 es de julio.' },
  ], { x: 0.6, y: 5.95, w: 12.1, h: 0.75, fontSize: 14, color: C.accent5, valign: 'top' });
  s.addNotes('Entre la R01 y la R03, Mirakl muestra la línea como «Incidencia abierta» con reembolso 0. Comprobado: el reembolso de Mirakl (motivo REFUND_04, solo devoluciones de tienda) se crea a la misma hora que la R03, por lotes en los días de recogida (26/06, 24/07, 31/07, 31/08). Tres devoluciones de Lisboa con R01 en julio y R03 en agosto no están en el EDI de agosto. BC procesó las 7 incidencias abiertas de Gaia sin esperar al reembolso. A 01/09 BC no tenía ninguna devolución de Portugal procesada: se procesaron entre el 01/09 y el 02/10. Riesgo: BC crea la devolución antes de saber el importe que reembolsará Mirakl.');
}

// ===================================================================== 7. peticiones
pres.addSection({ title: 'Siguientes pasos' });
{
  const s = pres.addSlide({ masterName: 'TITULO', sectionTitle: 'Siguientes pasos' });
  s.addText('Qué pedimos para cerrar la liquidación', { placeholder: 'title' });
  s.addText('Con estas respuestas se cierra Portugal; después, España con el mismo método', { placeholder: 'body' });
  const cols = [
    ['IT (Business Central)', AZUL_T, [
      'Comisión sobre la venta sin IVA del país y neto de Portugal sin IVA',
      'Revisar el 29 % de niños en España (ECI aplica 30 %)',
      'Por qué el conector dejó de actualizar los pedidos creados hasta el 28/06',
      'Por qué la venta 124836 (pedido del 15/06) no se vincula con su línea EDI',
      'Qué línea es el «producto sin relacionar» de 0143 / 601',
      'Cómo registrar en BC las entregas de pedidos de SAP (antes del 01/06)',
    ]],
    ['ECI', 'FFF4D6', [
      'Confirmar que Portugal se factura por departamento, con las tiendas dentro de 0143',
      'Gaia: devolución del 10/08 del pedido 00401430751578320260801170207 (219,85 €), que no está en Mirakl',
      'Online: abono del 05/08 de la línea 00401430764858020260717201700_1-A-1 (79,95 €), sin reembolso en Mirakl',
      'Devoluciones en tienda: en agosto tardaron de 5 a 8 semanas en llegar al almacén (R02)',
    ]],
  ];
  cols.forEach(([t, bg, items], i) => {
    const x = 0.6 + i * 6.2, w = 5.9;
    card(s, x, 1.85, w, 4.25, bg, `peticiones ${t}`);
    txt(s, t, { x: x + 0.3, y: 2.05, w: w - 0.6, h: 0.45, fontSize: 19, bold: true, color: C.accent1 });
    txt(s, items.map((p, k) => ({ text: p, options: { bullet: { type: 'number' }, breakLine: k < items.length - 1 } })),
      { x: x + 0.3, y: 2.6, w: w - 0.6, h: 3.4, fontSize: 15, paraSpaceAfter: 8, valign: 'top' });
  });
  txt(s, [
    { text: 'Resuelto, sin acción: ', options: { bold: true } },
    { text: 'la venta de 65 € de hombre del pedido 00401430757641420260826172900 se entregó el 31/08 y la recepción se confirmó a las 23:52. ECI la liquida en agosto y Mirakl la fecha el 01/09 (corte de fin de mes). BC ya la tiene procesada.' },
  ], { x: 0.6, y: 6.25, w: 12.1, h: 0.6, fontSize: 12, color: C.accent5, valign: 'top' });
  s.addNotes('Detalle completo en el informe Word «Informe motivos liquidación ECI Portugal agosto 2026 (v3)» y en el Excel «Motivos liquidación ECI Portugal agosto 2026 (v2)».');
}

(async () => {
  await pres.writeFile({ fileName: OUT });
  await applyTheme(OUT, THEME);
  console.log('Escrito', OUT);
})();
