# -*- coding: utf-8 -*-
"""Reconstrucción línea a línea de las líneas EDI de agosto 2026 de Portugal a partir del export de Mirakl,
con las reglas verificadas, y comprobación contra las filas del informe de BC."""
import sys
import pandas as pd

sys.stdout.reconfigure(encoding='utf-8')
SC = sys.argv[1]
pt = pd.read_parquet(SC + '/pt/pt_mirakl_export.parquet')
log = pd.read_parquet(SC + '/pt/pt_log_conector_bc_0109.parquet')
for c in ['Importe', 'Cantidad', 'Importe total reembolsado (impuestos incluidos)', 'Precio por unidad']:
    pt[c] = pd.to_numeric(pt[c].replace('', None), errors='coerce').fillna(0.0)
for c in ['Fecha Emisión', 'Fecha de cumplimentación', 'Fecha de abono 1', 'Fecha de recogida 1']:
    pt[c + '_d'] = pd.to_datetime(pt[c].replace('', None), format='%Y%m%d', errors='coerce')
for c in ['Fecha de creación', 'Fecha de débito al cliente', 'Fecha de recepción', 'Entrega']:
    pt[c + '_d'] = pd.to_datetime(pt[c].replace('', None), format='%d/%m/%Y %H:%M:%S', errors='coerce')
lg = log.set_index('Mirakl Line Id')
pt['en_log'] = pt['N.º de asiento de pedido'].isin(lg.index)
pt['log_status'] = pt['N.º de asiento de pedido'].map(lg['Processing Status']).fillna('')
pt['log_bc_order'] = pt['N.º de asiento de pedido'].map(lg['BC Sales Order No.']).fillna('')
pt['log_refund_date'] = pd.to_datetime(pt['N.º de asiento de pedido'].map(lg['Refund Created Date']).replace('', None),
                                       errors='coerce', utc=True).dt.tz_convert('Europe/Madrid').dt.tz_localize(None)
INI, FIN = pd.Timestamp('2026-08-01'), pd.Timestamp('2026-08-31 23:59:59')


def ago(x):
    return pd.notna(x) and INI <= x <= FIN


CORTE_CONECTOR = pd.Timestamp('2026-06-29')  # pedidos creados antes: estado congelado en el conector (verificado)
S0140 = ('0247', '0257', '0358', '0359', '0558', '0559', '0560', '0561')
S0142 = ('0250', '0253', '0260', '0265', '0266', '0269', '0616', '0617')


def centro_abono(t):
    t = str(t)
    if t.startswith('9'):
        return '0143'
    if t[:4] in S0140:
        return '0140'
    if t[:4] in S0142:
        return '0142'
    return '?'


rows = []
for _, r in pt.iterrows():
    base = dict(asiento=r['N.º de asiento de pedido'], pedido=r['Número de pedido'], uneco=r['UNECO_inferido_por_descripcion'],
                ean=r['SKU del producto'], descripcion=str(r['Detalles']).split(' (SKU')[0][:70], estado=r['Estado'],
                cantidad=r['Cantidad'], importe=r['Importe'], reembolso=r['Importe total reembolsado (impuestos incluidos)'],
                creado=r['Fecha de creación_d'], debito=r['Fecha de débito al cliente_d'], cumplimentacion=r['Fecha de cumplimentación_d'],
                talon_cumpl=r['Talón de cumplimentación'], abono=r['Fecha de abono 1_d'], talon_abono=r['Talón de abono 1'],
                recogida=r['Fecha de recogida 1_d'],
                conector=('no está (pedido anterior al 01/06)' if not r['en_log'] else r['log_status']), pedido_bc=r['log_bc_order'])
    fd = r['Fecha de débito al cliente_d'] if pd.notna(r['Fecha de débito al cliente_d']) else r['Fecha de creación_d']
    if ago(r['Fecha Emisión_d']):
        if pd.notna(fd) and ago(fd + pd.Timedelta(minutes=30)):
            rows.append({**base, 'concepto': 'En proceso', 'centro': '0143', 'importe_edi': r['Importe'], 'vinculo': '',
                         'motivo': 'Pedido del mes (no entra en la liquidación)'})
        else:
            rows.append({**base, 'concepto': 'Fuera del EDI de agosto', 'centro': '0143', 'importe_edi': 0.0, 'vinculo': '',
                         'motivo': 'Pedido de la última hora del 31/08 o cobrado en septiembre: ECI cierra el día hacia las 23:30 y lo pasa a septiembre'})
    if ago(r['Fecha de cumplimentación_d']):
        if r['Estado'] == 'Rechazado':
            rows.append({**base, 'concepto': 'Excluida del finalizado', 'centro': '0143', 'importe_edi': 0.0, 'vinculo': '',
                         'motivo': 'Línea rechazada: el talón de cumplimentación es del pedido y se copia a todas sus líneas, pero ECI no la liquida'})
        else:
            if not r['en_log']:
                v, m = 'Sin vincular', 'Venta de un pedido anterior al arranque del conector (01/06): BC no tiene tramo Mirakl'
            else:
                v, m = 'Vinculada', 'Venta finalizada con tramo Mirakl procesado'
            rows.append({**base, 'concepto': 'Venta finalizada', 'centro': '0143', 'importe_edi': r['Importe'], 'vinculo': v, 'motivo': m})
    ab = ago(r['Fecha de abono 1_d'])
    if ab:
        c = centro_abono(r['Talón de abono 1'])
        if pd.isna(r['Fecha de cumplimentación_d']):
            rows.append({**base, 'concepto': 'Rescisión', 'centro': '0143', 'importe_edi': -r['Importe'], 'vinculo': '',
                         'motivo': 'Abono de una línea nunca entregada: anula el pedido en el centro del pedido, sea cual sea la caja del abono (no entra en la liquidación)'})
        elif r['Estado'] == 'Recibido' and r['Importe total reembolsado (impuestos incluidos)'] == 0:
            rows.append({**base, 'concepto': 'No es devolución', 'centro': c, 'importe_edi': 0.0, 'vinculo': '',
                         'motivo': 'Línea hermana no devuelta: comparte el talón de abono del pedido, pero no se devolvió'})
        else:
            imp, q = r['Importe'], r['Cantidad']
            if q > 1 and 0 < r['Importe total reembolsado (impuestos incluidos)'] < r['Importe']:
                imp, q = r['Importe total reembolsado (impuestos incluidos)'], 1
            if pd.notna(r['Fecha de creación_d']) and r['Fecha de creación_d'] < CORTE_CONECTOR:
                v, m = 'Sin vincular', 'Devolución de un pedido creado antes del 29/06: el conector dejó de actualizar esos pedidos y no tiene tramo de devolución'
            else:
                extra = (' (Incidencia abierta: Mirakl aún no ha reembolsado, pero ECI la liquida por el importe completo)'
                         if r['Estado'] == 'Incidencia abierta' else '')
                v, m = 'Vinculada', 'Devolución con tramo Mirakl procesado' + extra
            if c != '0143':
                m += f'. Devolución hecha en tienda ({"Lisboa" if c == "0140" else "Gaia"}): EDI la pone en el centro {c}; ECI la liquida dentro de 0143'
            rows.append({**base, 'cantidad': q, 'concepto': 'Devolución', 'centro': c, 'importe_edi': -imp, 'vinculo': v, 'motivo': m})
    if r['Estado'] in ('Rechazado', 'Cancelado') and ago(r['Fecha Emisión_d']):
        rows.append({**base, 'concepto': 'Rescisión', 'centro': '0143', 'importe_edi': -r['Importe'], 'vinculo': '',
                     'motivo': f'Línea {r["Estado"].lower()} del mes (no entra en la liquidación)'})
    if (not ab) and pd.isna(r['Fecha de cumplimentación_d']) and r['Talón de abono 1'] == '' and r['Estado'] == 'Reembolsado' and ago(r['log_refund_date']):
        rows.append({**base, 'concepto': 'Rescisión', 'centro': '0143', 'importe_edi': -r['Importe'], 'vinculo': '',
                     'motivo': 'Reembolso sin talón de abono (fecha del reembolso en el conector) de una línea nunca entregada'})

df = pd.DataFrame(rows)
df.to_parquet(SC + '/pt/reconstruccion_pt.parquet')
print('líneas reconstruidas:', len(df))
g = df[df['importe_edi'] != 0].groupby(['centro', 'uneco', 'concepto']).agg(
    lineas=('asiento', 'size'), uds=('cantidad', 'sum'), importe=('importe_edi', 'sum')).round(2)
print(g.to_string())
print('\nvinculación:')
print(df[df['vinculo'] != ''].groupby(['centro', 'uneco', 'concepto', 'vinculo'])['importe_edi'].agg(['size', 'sum']).round(2).to_string())
print('\nexcluidas / fuera:')
print(df[df['concepto'].isin(['Fuera del EDI de agosto', 'Excluida del finalizado', 'No es devolución'])][['asiento', 'concepto', 'centro', 'uneco', 'importe', 'creado', 'debito']].to_string(index=False))
