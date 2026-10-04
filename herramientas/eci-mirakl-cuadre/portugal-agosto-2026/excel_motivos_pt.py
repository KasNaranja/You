# -*- coding: utf-8 -*-
"""Excel de detalle del informe de motivos de Portugal (agosto 2026)."""
import json
import sys

import openpyxl
import pandas as pd
from openpyxl.formatting.rule import FormulaRule
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

sys.stdout.reconfigure(encoding='utf-8')
SC, OUT = sys.argv[1], sys.argv[2]
rec = pd.read_parquet(SC + '/pt/reconstruccion_pt.parquet')
bc = pd.DataFrame(json.load(open(SC + '/pt/bc_informe_pt.json', encoding='utf-8')))

F = 'Arial'
CAB = PatternFill('solid', fgColor='1F4E78')
CABF = Font(name=F, size=10, bold=True, color='FFFFFF')
N = Font(name=F, size=10)
B = Font(name=F, size=10, bold=True)
T = Font(name=F, size=14, bold=True, color='1F4E78')
NOTA = Font(name=F, size=9, italic=True, color='595959')
th = Side(style='thin', color='BFBFBF')
BOR = Border(left=th, right=th, top=th, bottom=th)
EUR = '#,##0.00 "€";-#,##0.00 "€";"-"'
DIF = '#,##0.00 "€";[Red]-#,##0.00 "€";"-"'
DIA = 'dd/mm/yyyy'
FH = 'dd/mm/yyyy hh:mm'


def cab(ws, r, heads, widths=None):
    for j, h in enumerate(heads, 1):
        c = ws.cell(row=r, column=j, value=h)
        c.fill, c.font, c.border = CAB, CABF, BOR
        c.alignment = Alignment(wrap_text=True, vertical='center')
        if widths:
            ws.column_dimensions[get_column_letter(j)].width = widths[j - 1]
    ws.row_dimensions[r].height = 30


def cel(ws, r, c, v, fmt=None, font=N, wrap=False):
    if isinstance(v, float) and pd.isna(v):
        v = None
    if isinstance(v, pd.Timestamp):
        v = None if pd.isna(v) else v.to_pydatetime()
    x = ws.cell(row=r, column=c, value=v)
    x.font, x.border = font, BOR
    if fmt:
        x.number_format = fmt
    if wrap:
        x.alignment = Alignment(wrap_text=True, vertical='top')
    return x


wb = openpyxl.Workbook()
ws = wb.active
ws.title = 'Resumen por fila BC'
ws2 = wb.create_sheet('Líneas EDI reconstruidas')
ws3 = wb.create_sheet('Pendiente de identificar')
ws4 = wb.create_sheet('Comisión e IVA')
ws5 = wb.create_sheet('Preguntas para IT y ECI')

# ---------------------------------------------------------------- hoja 2: líneas reconstruidas
cols = ['asiento', 'pedido', 'centro', 'uneco', 'concepto', 'vinculo', 'importe_edi', 'cantidad', 'importe', 'reembolso', 'estado',
        'ean', 'descripcion', 'creado', 'debito', 'cumplimentacion', 'talon_cumpl', 'abono', 'talon_abono', 'recogida', 'conector', 'pedido_bc', 'motivo']
heads = ['N.º asiento Mirakl', 'Nº pedido Mirakl', 'Centro EDI', 'UNECO', 'Concepto EDI', 'Vínculo con Mirakl', 'Importe EDI', 'Uds EDI',
         'Importe línea Mirakl', 'Reembolso Mirakl', 'Estado Mirakl (21/09)', 'EAN', 'Descripción', 'Creado', 'Cobrado', 'Cumplimentación',
         'Talón cumplim.', 'Abono', 'Talón abono', 'Recogida', 'Conector (01/09)', 'Pedido BC', 'Motivo']
orden = {'Venta finalizada': 1, 'Excluida del finalizado': 2, 'Devolución': 3, 'No es devolución': 4, 'Rescisión': 5, 'En proceso': 6, 'Fuera del EDI de agosto': 7}
rec = rec.assign(_o=rec['concepto'].map(orden)).sort_values(['_o', 'centro', 'uneco', 'vinculo', 'asiento']).drop(columns='_o')
ws2['A1'] = 'Líneas EDI de agosto de 2026 de Portugal reconstruidas desde el export de Mirakl (21/09) con las reglas verificadas'
ws2['A1'].font = T
ws2['A2'] = ('Una fila por línea EDI. «Importe EDI» lleva el signo de la liquidación (devoluciones y rescisiones en negativo). '
             'En proceso y rescisión no entran en la liquidación. Las 4 devoluciones sin procesar y la venta de 65 € de hombre no salen del export: ver «Pendiente de identificar».')
ws2['A2'].font = NOTA
cab(ws2, 4, heads, [36, 34, 8, 7, 18, 12, 11, 6, 11, 10, 15, 15, 34, 15, 15, 12, 11, 12, 11, 12, 18, 9, 80])
fmt = {'importe_edi': DIF, 'importe': EUR, 'reembolso': EUR, 'creado': FH, 'debito': FH, 'cumplimentacion': DIA, 'abono': DIA, 'recogida': DIA}
for i, rr in enumerate(rec[cols].itertuples(index=False), 5):
    for j, (k, v) in enumerate(zip(cols, rr), 1):
        cel(ws2, i, j, v, fmt.get(k))
n2 = 4 + len(rec)
ws2.freeze_panes = 'B5'
ws2.auto_filter.ref = f'A4:{get_column_letter(len(cols))}{n2}'
for txt, color in [('Sin vincular', 'FFC7CE'), ('Vinculada', 'C6EFCE')]:
    ws2.conditional_formatting.add(f'A5:{get_column_letter(len(cols))}{n2}',
                                   FormulaRule(formula=[f'$F5="{txt}"'], fill=PatternFill('solid', fgColor=color, bgColor=color)))
for txt in ['Excluida del finalizado', 'No es devolución', 'Fuera del EDI de agosto']:
    ws2.conditional_formatting.add(f'A5:{get_column_letter(len(cols))}{n2}',
                                   FormulaRule(formula=[f'$E5="{txt}"'], fill=PatternFill('solid', fgColor='E7E6E6', bgColor='E7E6E6')))
R = lambda col: f"'Líneas EDI reconstruidas'!${get_column_letter(cols.index(col) + 1)}$5:${get_column_letter(cols.index(col) + 1)}${n2}"

# ---------------------------------------------------------------- hoja 1: resumen por fila BC
ws['A1'] = 'Liquidación ECI Portugal, agosto de 2026: informe de BC frente a la reconstrucción desde Mirakl'
ws['A1'].font = T
ws['A2'] = ('Fuentes: «liquidación mensual ECI mes 8 datos.xlsx» (BC, 02/10/2026), «pedidos 2026.xlsx» (Mirakl, 21/09/2026), log del conector (01/09/2026) '
            'y PDF de ECI de Portugal (8 - AGOST). Columnas de reconstrucción con fórmulas sobre la hoja de líneas.')
ws['A2'].font = NOTA
h = ['Centro', 'UNECO', 'Estado BC', 'Liquidable BC', 'Finalizado BC', 'Finalizado reconstruido', 'Dif. finalizado', 'Devoluciones BC',
     'Devoluciones reconstruidas', 'Dif. devoluciones', 'Líneas sin vincular BC', 'Tramos sin procesar BC', 'Motivo']
cab(ws, 4, h, [8, 7, 11, 13, 13, 14, 12, 13, 14, 12, 10, 10, 95])
motivos = {
    ('0140', '601'): 'Cuadrado. 9 devoluciones hechas en la tienda de Lisboa (cajas 0247, 0558-0561), todas con tramo procesado. ECI las liquida dentro de 0143.',
    ('0140', '696'): 'Cuadrado. 1 devolución de niños en Lisboa (talón 03594705) en Incidencia abierta: ECI la liquida por el importe completo aunque Mirakl no haya reembolsado.',
    ('0142', '601'): ('Aviso. 9 devoluciones de Gaia con tramo procesado (518,12). 1 sin vincular de 34,95: pedido de junio que el conector dejó de actualizar. '
                      '3 líneas EDI por 219,85 con tramo vinculado sin procesar que no tienen abono de agosto en Mirakl (pendiente de identificar).'),
    ('0143', '601'): ('Aviso. 6 líneas sin vincular (neto +68,91): 4 ventas de pedidos anteriores a julio (220,82) y 2 devoluciones de pedidos de junio congelados en el conector (151,91). '
                      '1 devolución EDI de 79,95 con tramo sin procesar y sin abono de agosto en Mirakl. 1 producto sin relacionar sin identificar.'),
    ('0143', '602'): 'Cuadrado. La reconstrucción desde Mirakl da 65,00 menos de finalizado: una venta recepcionada el 31/08 por la noche cuyo talón ECI fecha el 01/09 (probable).',
    ('0143', '696'): 'Cuadrado. Sin incidencias.',
}
r = 5
for _, b in bc.iterrows():
    c, u = str(b['Código centro']), str(b['Código UNECO candidato'])
    cel(ws, r, 1, c)
    cel(ws, r, 2, u)
    cel(ws, r, 3, b['Estado comparación operativa'])
    cel(ws, r, 4, float(b['Importe liquidable']), EUR)
    cel(ws, r, 5, float(b['Importe finalizado']), EUR)
    cel(ws, r, 6, f'=SUMIFS({R("importe_edi")},{R("centro")},$A{r},{R("uneco")},$B{r},{R("concepto")},"Venta finalizada")', EUR)
    cel(ws, r, 7, f'=ROUND(E{r}-F{r},2)', DIF)
    cel(ws, r, 8, float(b['Importe devoluciones']), EUR)
    cel(ws, r, 9, f'=SUMIFS({R("importe_edi")},{R("centro")},$A{r},{R("uneco")},$B{r},{R("concepto")},"Devolución")', EUR)
    cel(ws, r, 10, f'=ROUND(H{r}-I{r},2)', DIF)
    cel(ws, r, 11, int(b['Líneas EDI liquidables sin vincular']))
    cel(ws, r, 12, int(b['Tramos de origen sin procesar en BC']))
    cel(ws, r, 13, motivos.get((c, u), ''), wrap=True)
    ws.row_dimensions[r].height = 45
    r += 1
cel(ws, r, 1, 'Total', font=B)
for col in 'DEFGHIJ':
    cel(ws, r, ord(col) - 64, f'=SUM({col}5:{col}{r - 1})', EUR if col not in 'GJ' else DIF, B)
for col in 'KL':
    cel(ws, r, ord(col) - 64, f'=SUM({col}5:{col}{r - 1})', '0', B)
tot = r
ws.conditional_formatting.add(f'A5:M{r - 1}', FormulaRule(formula=['$C5="Aviso"'], fill=PatternFill('solid', fgColor='FFEB9C', bgColor='FFEB9C')))
ws.conditional_formatting.add(f'A5:M{r - 1}', FormulaRule(formula=['$C5="Cuadrado"'], fill=PatternFill('solid', fgColor='C6EFCE', bgColor='C6EFCE')))
r += 2
ws.cell(row=r, column=1, value='Cuadre con los PDF de ECI (ECI solo liquida el centro 0143 y mete dentro las devoluciones de las tiendas 0140 y 0142)').font = B
r += 1
cab(ws, r, ['UNECO', '', '', 'Liquidable BC (0140+0142+0143)', 'Total venta PDF ECI', 'Diferencia'])
r += 1
pdf = {'601': 4922.72, '602': 981.56, '696': 101.87}
r0 = r
for u, v in pdf.items():
    cel(ws, r, 1, u)
    cel(ws, r, 4, f'=SUMIFS($D$5:$D${tot - 1},$B$5:$B${tot - 1},$A{r})', EUR)
    cel(ws, r, 5, v, EUR)
    cel(ws, r, 6, f'=ROUND(D{r}-E{r},2)', DIF)
    r += 1
cel(ws, r, 1, 'Total', font=B)
cel(ws, r, 4, f'=SUM(D{r0}:D{r - 1})', EUR, B)
cel(ws, r, 5, f'=SUM(E{r0}:E{r - 1})', EUR, B)
cel(ws, r, 6, f'=ROUND(D{r}-E{r},2)', DIF, B)
ws.freeze_panes = 'C5'
ws.sheet_view.showGridLines = False

# ---------------------------------------------------------------- hoja 3: pendiente de identificar
ws3['A1'] = 'Lo que no se puede identificar con el export de Mirakl y el log: hace falta el detalle de BC'
ws3['A1'].font = T
cab(ws3, 3, ['Fila BC', 'Qué falta', 'Importe', 'Qué sabemos', 'Candidatas', 'Qué pedir a IT'], [12, 40, 11, 70, 70, 60])
pend = [
    ('0142/601', '3 líneas EDI de devolución con tramo vinculado y sin procesar', -219.85,
     'El EDI de Gaia tiene 13 líneas: 10 son devoluciones de agosto de Mirakl (9 procesadas por 518,12 y 1 sin vincular de 34,95). Las otras 3 (219,85) no tienen abono de agosto en Mirakl a 21/09 y tienen tramo, así que son de pedidos posteriores al 29/06.',
     'Ambigüedad: el trío 02654478 + 02655550 + 02695702 (Incidencia abierta) suma también 219,85; puede ser ese trío el que está sin procesar y las 3 líneas extra procesadas. Pista de baja confianza: devoluciones de julio en Gaia (02650450, 06166877 A-1, 02652811) liquidadas tarde.',
     'Para los 12 tramos vinculados de 0142/601: Mirakl Line Id, importe EDI, talón y estado de proceso (y el error si no se procesó).'),
    ('0143/601', '1 línea EDI de devolución con tramo vinculado y sin procesar', -79.95,
     'Las 8 devoluciones EDI de 0143 son las 7 online de agosto (394,72) más una de 79,95 que no aparece entre los abonos de agosto del export.',
     'Por importe podría intercambiarse con 92013281 (79,95, pedido de junio). Las dos de 79,95 con talón de Gaia (02654478, 02655550) están en 0142. La recogida del 31/08 abonada el 14/09 (00401430756819220260821155459_1-A-1) no encaja con la regla del talón de abono.',
     'Mirakl Line Id y talón del tramo sin procesar de 0143/601.'),
    ('0143/601', '4.ª venta finalizada sin vincular', 59.95,
     'Las 4 ventas sin vincular suman 220,82. Tres están identificadas (pedidos de enero, febrero y mayo, 160,87); la cuarta vale 59,95.',
     'Seis líneas de 59,95 cumplimentadas en agosto; la más probable por mecanismo es 00401430752499520260615175342_1-A-1 (pedido del 15/06, venta BC 124836), sin demostrar.',
     'Qué línea EDI de 59,95 de 0143/601 está sin vincular y por qué no se vincula si su pedido está en BC.'),
    ('0143/602', '1 venta finalizada de 65,00 que la reconstrucción no encuentra', 65.00,
     'BC tiene 21 tramos de venta procesados por 1.163,97 y la reconstrucción por fecha de cumplimentación da 20 por 1.098,97. La línea existe en el conector.',
     'Única candidata con entrega en agosto: 00401430757641420260826172900_1-A-1 (zuecos de hombre, recepción 31/08 23:52, talón de cumplimentación 95416672 del 01/09).',
     'Mirakl Line Id del 21.º tramo de venta de 0143/602 y la fecha de su línea EDI.'),
    ('0143/601', 'Producto sin relacionar (1)', None,
     'No coincide con ninguna línea concreta: puede estar en una línea no liquidable (en España aparece en una fila con una sola línea de rescisión).',
     'Ninguno de los EAN de las líneas sin vincular está en la lista de EAN sin mapear de junio-julio.',
     'Qué línea o EAN cuenta como «producto sin relacionar» y si impide la vinculación.'),
]
for i, p in enumerate(pend, 4):
    for j, v in enumerate(p, 1):
        cel(ws3, i, j, v, EUR if j == 3 else None, wrap=True)
    ws3.row_dimensions[i].height = 90

# ---------------------------------------------------------------- hoja 4: comisión e IVA
ws4['A1'] = 'Comisión de ECI y neto a facturar: cálculo de ECI (PDF) frente a cálculo de BC'
ws4['A1'].font = T
ws4['A2'] = ('ECI: neta = total / 1,23 (IVA portugués); participación = 29 % de la neta; Toni Pons factura la neta menos la participación SIN IVA. '
             'BC: comisión = 29 % de la base con IVA; neto esperado = liquidable − comisión.')
ws4['A2'].font = NOTA
cab(ws4, 4, ['UNECO', 'Total venta ECI', 'Neta ECI', 'IVA 23 %', 'Participación ECI 29 %', 'A facturar ECI (sin IVA)', 'Liquidable BC', 'Base comisión BC',
             'Comisión esperada BC', 'Neto esperado BC', 'Dif. neto BC − a facturar', 'Dif. comisión BC − ECI'], [8, 13, 12, 11, 13, 14, 13, 13, 13, 13, 14, 13])
ecis = {'601': (4922.72, 4002.21, 920.51, 1160.64, 2841.57), '602': (981.56, 798.02, 183.54, 231.43, 566.59), '696': (101.87, 82.82, 19.05, 24.02, 58.80)}
bcu = bc.assign(u=bc['Código UNECO candidato'].astype(str)).groupby('u')[['Importe liquidable', 'Base imponible comisión', 'Comisión esperada', 'Importe neto esperado']].sum()
r = 5
for u, (t_, n_, iv, pa, af) in ecis.items():
    vals = [u, t_, n_, iv, pa, af] + [round(float(bcu.loc[u, c]), 2) for c in ['Importe liquidable', 'Base imponible comisión', 'Comisión esperada', 'Importe neto esperado']]
    for j, v in enumerate(vals, 1):
        cel(ws4, r, j, v, None if j == 1 else EUR)
    cel(ws4, r, 11, f'=ROUND(J{r}-F{r},2)', DIF)
    cel(ws4, r, 12, f'=ROUND(I{r}-E{r},2)', DIF)
    r += 1
cel(ws4, r, 1, 'Total', font=B)
for col in 'BCDEFGHIJKL':
    cel(ws4, r, ord(col) - 64, f'=SUM({col}5:{col}{r - 1})', EUR if col not in 'KL' else DIF, B)
r += 2
for t in ['Lectura: el neto esperado de BC supera en el total lo que realmente se factura a ECI. La diferencia = IVA portugués que BC no descuenta − exceso de comisión que BC calcula sobre el importe con IVA.',
          'Además, BC deja fuera de la base de comisión las líneas sin vincular pero las suma enteras en el neto esperado (601: 33,96 de neto sin comisión).',
          '«Comisión real Mirakl» vale 0 en todas las filas: ECI no carga su participación en Mirakl (las 27.730 líneas del export tienen comisión 0), la cobra en la liquidación mensual.']:
    ws4.cell(row=r, column=1, value=t).font = NOTA
    r += 1

# ---------------------------------------------------------------- hoja 5: preguntas
ws5['A1'] = 'Preguntas y peticiones'
ws5['A1'].font = T
cab(ws5, 3, ['Para', 'Tema', 'Pregunta o petición'], [8, 30, 120])
qs = [
    ('IT', 'Comisión e IVA de Portugal', 'Calcular la comisión esperada sobre la venta neta sin IVA del país (23 % en Portugal) y el neto esperado sin IVA en Portugal (Toni Pons factura a ECI Portugal sin IVA). Hoy el neto esperado de Portugal sale 807,22 € por encima de lo facturable.'),
    ('IT', 'Comisión de niños en España', 'BC aplica el 29 % a las filas 696 de España y ECI aplica el 30 % en 0090/696. Revisar la tabla de porcentajes por país y UNECO.'),
    ('IT', 'Pedidos congelados en el conector', 'Los pedidos creados hasta el 28/06 dejaron de actualizarse en el conector: sus devoluciones posteriores no generan tramo y salen como líneas EDI sin vincular. Forzar una relectura de esos pedidos o crear el abono a mano. En julio hay al menos 12 devoluciones más en esta situación.'),
    ('IT', 'Ventas de pedidos anteriores al conector', 'ECI sigue liquidando entregas de pedidos de enero a mayo (registrados en SAP). Definir cómo se registran en BC: vínculo manual o documento manual.'),
    ('IT', 'Detalle de tramos', 'Sacar de BC, para 0142/601 y 0143/601, la lista de líneas EDI con su Mirakl Line Id, talón, importe, tramo vinculado y estado de proceso (con el error de los no procesados). Con eso se identifican las 4 devoluciones por 299,80 € y la venta de 65 € de 0143/602.'),
    ('IT', 'Valoración del tramo sin procesar', 'Confirmar que un tramo sin procesar cuenta 0 € en el lado Mirakl y por qué no se procesan: los 10 del informe (España y Portugal) son devoluciones.'),
    ('IT', 'Producto sin relacionar', 'Indicar qué línea o EAN cuenta como «producto sin relacionar» en 0143/601 y si bloquea la vinculación.'),
    ('IT', 'Cantidades devueltas en España', 'Algunas filas de España tienen cantidades devueltas imposibles (0037/601: -223 uds en 28 líneas; 0003/601: -214 en 16). Revisar el campo cantidad en la importación EDI.'),
    ('ECI', 'Liquidación por centro', 'Los PDF dicen «facturar independientemente por centro» pero solo traen 0143, con las devoluciones de las tiendas de Lisboa y Gaia dentro. Confirmar que se factura por departamento consolidado.'),
    ('ECI', 'Devoluciones liquidadas sin abono de agosto en Mirakl', 'Hay 4 devoluciones (299,80 €) liquidadas en agosto cuyo talón de abono no aparece en agosto en Mirakl. Pedir el detalle EDI de esas líneas si IT no puede sacarlo de BC.'),
]
for i, q in enumerate(qs, 4):
    for j, v in enumerate(q, 1):
        cel(ws5, i, j, v, wrap=True)
    ws5.row_dimensions[i].height = 45

sys.path.insert(0, SC + "/pt")
from hoja_pdf_vs_bc import anadir
anadir(wb, bc, 1)

for w in (ws, ws3, ws4, ws5):
    w.sheet_view.showGridLines = False
wb.calculation.fullCalcOnLoad = True
wb.save(OUT)
print('guardado', OUT, '| líneas', len(rec))
