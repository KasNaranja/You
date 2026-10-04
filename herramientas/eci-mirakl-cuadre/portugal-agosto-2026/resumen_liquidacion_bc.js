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
  s.addNotes('Solo coincide la venta con IVA. BC no quita el IVA portugués del 23 %, así que calcula la comisión y el neto sobre una base más alta: 315,88 € más de comisión y 807,22 € más de neto que lo que se factura a ECI (facturas 260007291, 260007292 y 260007293, 3.466,96 €). El campo IVA comisión esperado de BC es el IVA de la comisión, no el de la factura.');
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
    ['299,80 €', '4 devoluciones sin procesar en BC', 'ECI las liquida en agosto sin abono de agosto en Mirakl', 'C98A00', 'FFF4D6'],
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
    { text: 'Comisión esperada = 29 % del importe con IVA', options: { bullet: true, breakLine: true } },
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
  s.addText('Sin tramo de Mirakl, BC no puede vincular la línea EDI y la deja fuera de la base de comisión', { placeholder: 'body' });
  const bloques = [
    ['A', 'Pedidos anteriores al conector', '220,82 €', '4 ventas en 0143 mujer',
      ['3 entregas de pedidos de enero, febrero y mayo, registrados en SAP (160,87 €)', 'Una cuarta de 59,95 € aún sin identificar']],
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
  txt(s, [{ text: 'Seguirá pasando: ', options: { bold: true } }, { text: 'en julio hay al menos 12 devoluciones más de pedidos congelados.' }],
    { x: 0.6, y: 6.05, w: 12.1, h: 0.4, fontSize: 15, color: C.accent3 });
  s.addNotes('Neto sin vincular: 0143/601 = 220,82 − 151,91 = +68,91 € (liquidable 6.318,44 − base de comisión 6.249,53); 0142/601 = −34,95 € (772,92 − 737,97). Petición a IT: por qué el conector dejó de refrescar los pedidos creados hasta el 28/06; relectura o abonos a mano; cómo registrar en BC las entregas de pedidos de SAP.');
}

// ===================================================================== 5. sin procesar
{
  const s = pres.addSlide({ masterName: 'TITULO', sectionTitle: 'Motivos' });
  s.addText('4 devoluciones sin procesar por 299,80 €', { placeholder: 'title' });
  s.addText('ECI las liquida en agosto, pero en Mirakl no tienen abono de agosto: BC no crea el documento y las cuenta a 0', { placeholder: 'body' });
  card(s, 0.6, 1.85, 4.2, 4.3, 'FFF4D6', 'cifra sin procesar');
  txt(s, '299,80 €', { x: 0.9, y: 2.2, w: 3.6, h: 1.1, fontSize: 48, bold: true, color: C.accent4, fontFace: THEME.headFontFace });
  txt(s, 'en 4 tramos de devolución vinculados y sin documento en BC', { x: 0.9, y: 3.35, w: 3.6, h: 0.9, fontSize: 16, bold: true, valign: 'top' });
  txt(s, 'Los 10 tramos sin procesar del informe (6 de España y 4 de Portugal) son todos devoluciones.', { x: 0.9, y: 4.4, w: 3.6, h: 1.4, fontSize: 14, color: C.accent5, valign: 'top' });
  const H = (t, al = 'left') => ({ text: t, options: { bold: true, color: 'FFFFFF', fill: { color: '1F4E78' }, align: al } });
  s.addTable([
    [H('Fila BC'), H('Tramos'), H('Importe EDI', 'right'), H('Qué sabemos')],
    ['0142 Gaia / 601', '3', { text: '219,85 €', options: { align: 'right' } }, 'Ambigüedad: otras 3 devoluciones de Gaia en incidencia suman también 219,85 €'],
    ['0143 online / 601', '1', { text: '79,95 €', options: { align: 'right' } }, 'Puede intercambiarse con una devolución de junio del mismo importe'],
  ], { x: 5.2, y: 1.85, w: 7.5, colW: [1.9, 0.9, 1.3, 3.4], fontSize: 14, fontFace: 'Calibri', color: '1F2933', rowH: [0.45, 0.8, 0.8],
    fill: { color: GRIS_T }, border: { type: 'solid', pt: 0.75, color: 'FFFFFF' }, valign: 'middle', objectName: 'tabla sin procesar' });
  card(s, 5.2, 4.35, 7.5, 1.8, AZUL_T, 'petición IT sin procesar');
  txt(s, 'Qué pedir a IT', { x: 5.45, y: 4.5, w: 7.0, h: 0.4, fontSize: 17, bold: true, color: C.accent1 });
  txt(s, 'Para 0142 / 601 y 0143 / 601, la lista de líneas EDI con su Mirakl Line Id, talón, importe, tramo vinculado y estado de proceso, con el error de los no procesados.',
    { x: 5.45, y: 4.95, w: 7.0, h: 1.1, fontSize: 15, valign: 'top' });
  s.addNotes('Las devoluciones EDI de Portugal son 34 líneas por 2.088,76 €. Las devoluciones de agosto de Mirakl explican 30 por 1.788,96 €; las 4 restantes (299,80 €) coinciden en número, importe y centro con los tramos sin procesar. Con la lista de IT se cierra también la venta de 65 € de 0143/602.');
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
    ['Cómo se reconoce la tienda', 'Por la caja: 4 primeros dígitos del talón de abono. Lisboa 0247, 0359, 0558-0561; Gaia 0265, 0266, 0269, 0617; online empieza por 9.'],
    ['Qué implica', 'Las filas de BC por centro no se comparan una a una con el PDF: hay que sumar por departamento.'],
  ];
  pts.forEach(([t, d], i) => {
    const y = 1.85 + i * 1.47;
    card(s, 7.3, y, 5.4, 1.32, i === 2 ? 'FFF4D6' : AZUL_T, `punto tiendas ${i + 1}`);
    txt(s, t, { x: 7.55, y: y + 0.12, w: 4.95, h: 0.38, fontSize: 16, bold: true, color: C.accent1 });
    txt(s, d, { x: 7.55, y: y + 0.5, w: 4.95, h: 0.75, fontSize: 13.5, valign: 'top' });
  });
  s.addNotes('0140 Lisboa: 9 líneas mujer (622,80 €) + 1 niños (35,96 €). 0142 Gaia: 13 líneas (772,92 €), 10 identificadas en Mirakl. 0143 online: 8 líneas mujer (474,67 €) + 3 hombre (182,41 €). Las ventas finalizadas y las rescisiones van siempre al centro del pedido (0143). Pregunta a ECI: confirmar que Portugal se factura por departamento consolidado.');
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
      'Lista de tramos de 0142 y 0143 con Mirakl Line Id y estado de proceso',
      'Qué línea es el «producto sin relacionar» de 0143 / 601',
    ]],
    ['ECI', 'FFF4D6', [
      'Confirmar que Portugal se factura por departamento, con las tiendas dentro de 0143',
      'Si IT no puede sacarlo de BC: detalle EDI de las 4 devoluciones liquidadas sin abono de agosto en Mirakl',
    ]],
  ];
  cols.forEach(([t, bg, items], i) => {
    const x = 0.6 + i * 6.2, w = 5.9;
    card(s, x, 1.85, w, 3.9, bg, `peticiones ${t}`);
    txt(s, t, { x: x + 0.3, y: 2.05, w: w - 0.6, h: 0.45, fontSize: 19, bold: true, color: C.accent1 });
    txt(s, items.map((p, k) => ({ text: p, options: { bullet: { type: 'number' }, breakLine: k < items.length - 1 } })),
      { x: x + 0.3, y: 2.6, w: w - 0.6, h: 3.5, fontSize: 15, paraSpaceAfter: 8, valign: 'top' });
  });
  s.addNotes('Detalle completo en el informe Word «Informe motivos liquidación ECI Portugal agosto 2026» y en el Excel «Motivos liquidación ECI Portugal agosto 2026» (hoja PDF vs BC para el cuadro de la primera diapositiva).');
}

(async () => {
  await pres.writeFile({ fileName: OUT });
  await applyTheme(OUT, THEME);
  console.log('Escrito', OUT);
})();
