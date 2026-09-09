# -*- coding: utf-8 -*-
"""
Distribució mensual (%) de la venda 2025 per col·lecció dels models HI26, per predir la demanda.

Fonts:
  T:\\Online\\Oriol\\Marketplaces\\ZALANDO\\VENDES\\VENDES SETMANALS\\2025\\<mes>\\VENDES DEL dd.mm al dd.mm.xlsx
      pestanyes DADES (data de comanda) + DADES2 (INITIAL+SHIPPED): una línia per línia de comanda.
      Cada unitat s'assigna al mes de la seva data de comanda; les línies repetides entre fitxers
      (setmanes que se solapen) només compten un cop.
  Informació models zalando\\TP Info Complerta Models Toni Pons.xlsx
      models amb Temporada = HI26 -> col·lecció (GrupArticle) i gènere (Código grupo talla).

Sortides (carpeta Previsió demanda):
  Càlcul venda per col·leccio 2025.xlsx  un full per temporada (HI26, ES26): blocs DONA / HOME / NEN, una fila per col·lecció,
                                         % de cada mes sobre el total 2025 de la col·lecció (suma 100%).
  Venda 2025 en € i %.xlsx               segon bloc: unitats totals per mes del 2025 i % del total.

Ús:  python previsio_colleccions.py [--any 2025] [--temporada HI26|ES26] [--nomes-taula]
     (executar-lo un cop per temporada: HI26 escriu el full HI26, ES26 el full ES26)
"""
import argparse
import datetime as dt
import glob
import json
import os
import re
import sys

import openpyxl
import pandas as pd
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.dirname(HERE)                       # carpeta "Zalando reposició"
T_BASE = r"T:\Online\Oriol\Marketplaces\ZALANDO\VENDES\VENDES SETMANALS"
TP_INFO = os.path.join(DATA, "Informació models zalando", "TP Info Complerta Models Toni Pons.xlsx")
CACHE = os.path.join(os.environ.get("LOCALAPPDATA", HERE), "Temp", "zalando_repo_cache", "previsio")
EXCLOU = ("acumulat", "anàlisi", "analisi", "no tenir en compte", "parcial", "brutes")
WEEK_RE = re.compile(r"DEL (\d\d)\.(\d\d) al (\d\d)\.(\d\d)", re.I)
GENERE = {"MUJER": "DONA", "UNISEX": "DONA", "CABALLERO": "HOME", "NIÑO": "NEN", "NINO": "NEN", "MINI": "NEN", "JUNIOR": "NEN"}
MESOS_CA = ["gen", "feb", "mar", "abr", "mai", "jun", "jul", "ago", "set", "oct", "nov", "des"]


def readable(path: str) -> str:
    """Si el fitxer està obert a Excel, en fa una còpia amb l'API de Windows."""
    try:
        with open(path, "rb"):
            return path
    except PermissionError:
        import ctypes
        os.makedirs(CACHE, exist_ok=True)
        dst = os.path.join(CACHE, "copia_" + os.path.basename(path))
        k32 = ctypes.windll.kernel32
        k32.CopyFileW.argtypes = [ctypes.c_wchar_p, ctypes.c_wchar_p, ctypes.c_bool]
        if not k32.CopyFileW(path, dst, False):
            raise SystemExit(f"No puc llegir {os.path.basename(path)} (obert a Excel?)")
        print(f"AVÍS: {os.path.basename(path)} està obert; es llegeix una còpia")
        return dst


# ----------------------------------------------------------------------------- vendes setmanals
def fitxers_setmanals(any_: int) -> list[str]:
    out = []
    for f in sorted(glob.glob(os.path.join(T_BASE, str(any_), "*", "*.xlsx"))):
        base = os.path.basename(f)
        if base.startswith("~$") or not WEEK_RE.search(base) or any(x in base.lower() for x in EXCLOU):
            continue
        out.append(f)
    return out


def inici_setmana(path: str, any_: int) -> dt.date:
    d1, m1, d2, m2 = map(int, WEEK_RE.search(os.path.basename(path)).groups())
    return dt.date(any_ - 1 if m1 > m2 else any_, m1, d1)


def llegeix_setmana(path: str) -> pd.DataFrame:
    wb = openpyxl.load_workbook(readable(path), read_only=True, data_only=True)
    if "DADES" not in wb.sheetnames or "DADES2" not in wb.sheetnames:
        raise ValueError("sense pestanyes DADES/DADES2")
    d1 = wb["DADES"].iter_rows(values_only=True)
    d2 = wb["DADES2"].iter_rows(values_only=True)
    h1 = [str(v).strip() if v is not None else "" for v in next(d1)]
    h2 = [str(v).strip() if v is not None else "" for v in next(d2)]
    i_date = h1.index("order_date") if "order_date" in h1 else h1.index("created_at")
    i_num = h1.index("order_number") if "order_number" in h1 else h1.index("order_id")
    i_ext1, i_ext2 = h1.index("external_id"), h2.index("external_id")
    i_q, i_model, i_mc = h2.index("INITIAL+SHIPPED"), h2.index("MODEL"), h2.index("MODEL_COLOR")
    rows1 = [r for r in d1 if any(v is not None for v in r)]
    rows2 = [r for r in d2 if any(v is not None for v in r)]
    if len(rows1) != len(rows2):
        raise ValueError(f"DADES ({len(rows1)}) i DADES2 ({len(rows2)}) no quadren")
    recs = []
    for a, b in zip(rows1, rows2):
        if (a[i_ext1] or "") != (b[i_ext2] or ""):
            raise ValueError("DADES i DADES2 desalineades")
        d = a[i_date]
        if isinstance(d, str):
            d = dt.datetime.fromisoformat(d[:19].replace("Z", ""))
        if not isinstance(d, (dt.datetime, dt.date)):
            continue
        q = b[i_q] if isinstance(b[i_q], (int, float)) else 0
        recs.append((pd.Timestamp(d).normalize(), int(q), str(b[i_model] or "").strip(), str(b[i_mc] or "").strip(),
                     f"{a[i_num]}|{a[i_ext1]}"))
    return pd.DataFrame(recs, columns=["data", "unitats", "model", "model_color", "clau"])


def linies_any(any_: int) -> tuple[pd.DataFrame, list[str]]:
    os.makedirs(CACHE, exist_ok=True)
    frames, avisos = [], []
    files = sorted(fitxers_setmanals(any_), key=lambda f: inici_setmana(f, any_))
    for f in files:
        cache = os.path.join(CACHE, f"{any_}_{os.path.basename(f)}.{int(os.path.getmtime(f))}.parquet")
        if os.path.exists(cache):
            df = pd.read_parquet(cache)
        else:
            try:
                df = llegeix_setmana(f)
            except Exception as e:  # noqa: BLE001
                avisos.append(f"{os.path.basename(f)}: {e}; s'ignora")
                continue
            df.to_parquet(cache)
        df["fitxer"] = os.path.basename(f)
        frames.append(df)
        print(f"  {os.path.basename(f):48s} {int(df['unitats'].sum()):6d}", flush=True)
    lines = pd.concat(frames, ignore_index=True)
    dup = lines.duplicated("clau", keep="first")
    avisos.append(f"{int(lines.loc[dup, 'unitats'].sum())} unitats repetides entre setmanes descartades")
    lines = lines[~dup]
    fora = lines["data"].dt.year != any_
    avisos.append(f"{int(lines.loc[fora, 'unitats'].sum())} unitats d'altres anys descartades")
    return lines[~fora].copy(), avisos


# ----------------------------------------------------------------------------- TP Info
def models_temporada(temp: str) -> pd.DataFrame:
    """model -> col·lecció (GrupArticle) i gènere (DONA/HOME/NEN) dels models amb la Temporada indicada (HI26, ES26...)."""
    cache = os.path.join(CACHE, f"tpinfo_{temp}.{int(os.path.getmtime(TP_INFO))}.json")
    if os.path.exists(cache):
        recs = json.load(open(cache, encoding="utf-8"))
    else:
        print("  llegint TP Info (triga un parell de minuts)...", flush=True)
        wb = openpyxl.load_workbook(readable(TP_INFO), read_only=True, data_only=True)
        ws = wb[wb.sheetnames[0]]
        it = ws.iter_rows(values_only=True)
        hdr = [str(h).strip() if h is not None else "" for h in next(it)]
        ix = {h: i for i, h in enumerate(hdr)}
        recs = []
        for r in it:
            if r[ix["Temporada"]] == temp:
                recs.append([r[ix["Model"]], r[ix["GrupArticle"]], r[ix["Código grupo talla"]]])
        os.makedirs(CACHE, exist_ok=True)
        json.dump(recs, open(cache, "w", encoding="utf-8"), ensure_ascii=False)
    df = pd.DataFrame(recs, columns=["model", "colleccio", "grup_talla"])
    df["model"] = df["model"].astype(str).str.strip()
    df["genere"] = df["grup_talla"].map(lambda g: GENERE.get(str(g).strip().upper(), None))
    # per model, la col·lecció i el gènere més freqüents entre les seves talles/colors
    def moda(s):
        s = s.dropna()
        return s.value_counts().index[0] if len(s) else None
    out = df.groupby("model").agg(colleccio=("colleccio", moda), genere=("genere", moda), files=("model", "size")).reset_index()
    return out


# ----------------------------------------------------------------------------- Excel
HDR_FILL = PatternFill("solid", fgColor="1F3864")
HDR_FONT = Font(bold=True, color="FFFFFF")
NOTE_FONT = Font(italic=True, color="7F7F7F")


def escriu_colleccions(path: str, taula: pd.DataFrame, any_: int, temp: str = "HI26"):
    wb = openpyxl.load_workbook(readable(path))
    ws = wb[temp] if temp in wb.sheetnames else wb.create_sheet(temp)
    # neteja el contingut anterior (conserva la pestanya)
    for row in ws.iter_rows(min_row=1, max_row=ws.max_row, max_col=max(ws.max_column, 20)):
        for c in row:
            c.value = None
            c.fill = PatternFill()
            c.font = Font()
    ws.cell(row=1, column=2, value=f"% de la venda {any_} de cada mes sobre el total de l'any, per col·lecció dels models {temp} (mes = data de comanda)").font = NOTE_FONT
    r = 2
    for genere in ["DONA", "HOME", "NEN"]:
        cap = [genere] + list(range(1, 13)) + ["TOTAL", f"UNITATS {any_}", f"MODELS AMB VENDA {any_}", f"MODELS {temp}", "NOTA"]
        for j, v in enumerate(cap):
            c = ws.cell(row=r, column=2 + j, value=v)
            c.fill, c.font = HDR_FILL, HDR_FONT
            c.alignment = Alignment(horizontal="center" if j else "left")
        r += 1
        blk = taula[taula["genere"] == genere].copy()
        blk["_tot"] = blk["colleccio"].str.startswith("TOTS ELS MODELS")
        blk = blk.sort_values(["_tot", "unitats"], ascending=[True, False])
        gen = blk[blk["_tot"]].iloc[0] if blk["_tot"].any() else None
        gen_pct = ([float(gen[f"m{m + 1}"]) / float(gen["unitats"]) for m in range(12)]
                   if gen is not None and gen["unitats"] > 0 else None)
        for _, t in blk.iterrows():
            c = ws.cell(row=r, column=2, value=t["colleccio"])
            if t["_tot"]:
                c.font = Font(bold=True)
            nota = t.get("nota") or ""
            # poques dades, llançament a mig any o sense venda: corba genèrica del gènere, i es deixa dit
            if nota and not t["_tot"] and gen_pct is not None:
                src = gen_pct
                nota = f"% = corba genèrica {genere} (tots els models HI26) perquè: {nota}"
            elif t["unitats"] > 0:
                src = [float(t[f"m{m + 1}"]) / float(t["unitats"]) for m in range(12)]
            else:
                src = None
            if nota:
                ws.cell(row=r, column=19, value=nota).font = NOTE_FONT
            if src is not None:
                pct = [round(x, 6) for x in src]
                pct[pct.index(max(pct))] += round(1.0 - sum(pct), 6)   # que sumi exactament 100%
                for m in range(12):
                    c = ws.cell(row=r, column=3 + m, value=round(pct[m], 6))
                    c.number_format = "0.0%"
                c = ws.cell(row=r, column=15, value=f"=SUM(C{r}:N{r})")
                c.number_format = "0.0%"
                c.font = Font(bold=True)
            else:
                c = ws.cell(row=r, column=3, value=f"sense venda {any_}: no es pot calcular")
                c.font = NOTE_FONT
            if t["_tot"]:
                for j in range(3, 16):
                    ws.cell(row=r, column=j).font = Font(bold=True)
            ws.cell(row=r, column=16, value=int(t["unitats"])).number_format = "#,##0"
            ws.cell(row=r, column=17, value=int(t["models_venda"]))
            ws.cell(row=r, column=18, value=int(t["models_hi26"]))
            r += 1
        r += 2
    ws.column_dimensions["A"].width = 2
    ws.column_dimensions["B"].width = 22
    for j in range(3, 16):
        ws.column_dimensions[get_column_letter(j)].width = 8
    for j, w in zip(range(16, 20), (14, 22, 13, 70)):
        ws.column_dimensions[get_column_letter(j)].width = w
    ws.freeze_panes = "C3"
    wb.save(path)


def escriu_unitats_totals(path: str, per_mes: list[int]):
    wb = openpyxl.load_workbook(readable(path))
    ws = wb[wb.sheetnames[0]]
    caps = [c.row for c in ws["A"] if isinstance(c.value, str) and c.value.strip().lower() == "zalando"]
    if len(caps) < 2:
        raise SystemExit("No trobo el segon bloc de 'Venda 2025 en € i %.xlsx'")
    r_val, r_pct = caps[1] + 1, caps[1] + 2
    ws.cell(row=r_val, column=1, value="Vendes")
    for m in range(12):
        ws.cell(row=r_val, column=2 + m, value=per_mes[m]).number_format = "#,##0"
    ws.cell(row=r_val, column=14, value=f"=SUM(B{r_val}:M{r_val})").number_format = "#,##0"
    for m in range(13):
        col = get_column_letter(2 + m)
        ws.cell(row=r_pct, column=2 + m, value=f"={col}{r_val}/$N${r_val}").number_format = "0.0%"
    wb.save(path)
    return r_val


# ----------------------------------------------------------------------------- principal
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--any", type=int, default=2025)
    ap.add_argument("--temporada", default="HI26", help="temporada dels models al TP Info: HI26 (hivern) o ES26 (estiu)")
    ap.add_argument("--nomes-taula", action="store_true", help="no escriu cap Excel, només mostra la taula")
    a = ap.parse_args()
    temp = a.temporada.upper()
    hivern = temp.startswith("HI")
    # mesos de temporada (per al resum en pantalla) i mes a partir del qual una primera venda es considera llançament
    idx_temp = (0, 1, 8, 9, 10, 11) if hivern else (2, 3, 4, 5, 6, 7)
    etiq_temp = "set-feb" if hivern else "mar-ago"
    mes_llanc = 6 if hivern else 3

    print("Vendes setmanals", a.any, "(T:)")
    lines, avisos = linies_any(a.any)
    print(f"Models {temp} (TP Info)")
    hi26 = models_temporada(temp)
    sense_genere = hi26[hi26["genere"].isna()]
    hi26 = hi26[hi26["genere"].notna()]

    per_model = lines.groupby(["model", lines["data"].dt.month])["unitats"].sum().unstack(fill_value=0)
    per_model = per_model.reindex(columns=range(1, 13), fill_value=0)
    per_model.columns = [f"m{m}" for m in per_model.columns]
    per_model["unitats"] = per_model.sum(axis=1)

    t = hi26.merge(per_model, left_on="model", right_index=True, how="left").fillna({f"m{m}": 0 for m in range(1, 13)} | {"unitats": 0})
    grp = t.groupby(["genere", "colleccio"])
    taula = grp[[f"m{m}" for m in range(1, 13)] + ["unitats"]].sum()
    taula["models_hi26"] = grp.size()
    taula["models_venda"] = grp["unitats"].apply(lambda s: int((s > 0).sum()))
    taula = taula.reset_index()
    # fila de total per gènere (tots els models HI26 del gènere): serveix de corba de reserva
    gg = t.groupby("genere")
    tot = gg[[f"m{m}" for m in range(1, 13)] + ["unitats"]].sum()
    tot["models_hi26"] = gg.size()
    tot["models_venda"] = gg["unitats"].apply(lambda s: int((s > 0).sum()))
    tot = tot.reset_index()
    tot["colleccio"] = f"TOTS ELS MODELS {temp}"
    taula = pd.concat([taula, tot[taula.columns]], ignore_index=True)

    def nota(r):
        if r["unitats"] <= 0:
            return f"sense venda {a.any}"
        mesos = [m for m in range(1, 13) if r[f"m{m}"] > 0]
        notes = []
        if r["unitats"] < 500 or r["models_venda"] < 3:
            notes.append("poques dades")
        if mesos and mesos[0] > mes_llanc:
            notes.append(f"venda només des del mes {mesos[0]} (llançament {a.any}): no té històric de gen-{MESOS_CA[mesos[0] - 2]}")
        return "; ".join(notes)
    taula["nota"] = taula.apply(nota, axis=1)

    # taula per pantalla
    print()
    print(f"{'GÈNERE':6s} {'COL·LECCIÓ':18s} {'UNIT.':>7s} {'MOD':>4s} " + " ".join(f"{m:>5s}" for m in MESOS_CA) + f"   {etiq_temp}")
    for _, r in taula.sort_values(["genere", "unitats"], ascending=[True, False]).iterrows():
        if r["unitats"] > 0:
            pct = [r[f"m{m}"] / r["unitats"] for m in range(1, 13)]
            hiv = sum(pct[i] for i in idx_temp)
            print(f"{r['genere']:6s} {str(r['colleccio'])[:18]:18s} {int(r['unitats']):7d} {int(r['models_venda']):4d} "
                  + " ".join(f"{p * 100:5.1f}" for p in pct) + f"   {hiv * 100:5.1f}%")
        else:
            print(f"{r['genere']:6s} {str(r['colleccio'])[:18]:18s} {'0':>7s} {0:4d}   sense venda {a.any}")
    tot_mes = [int(lines.loc[lines['data'].dt.month == m, 'unitats'].sum()) for m in range(1, 13)]
    print("\nTOTAL Zalando", a.any, "per mes:", dict(zip(MESOS_CA, tot_mes)), "| total", sum(tot_mes))
    for av in avisos:
        print("AVÍS:", av)
    if len(sense_genere):
        print(f"AVÍS: models {temp} sense gènere de calçat (complements, bosses, cinturons...):", len(sense_genere), "->", ", ".join(sense_genere["model"].head(12)))
    no_hi26 = lines[~lines["model"].isin(set(hi26["model"]))]
    print(f"Info: {int(no_hi26['unitats'].sum())} unitats {a.any} són de models que no són {temp} (no entren a la taula)")

    if a.nomes_taula:
        return
    p1 = os.path.join(HERE, f"Càlcul venda per col·leccio {a.any}.xlsx")
    escriu_colleccions(p1, taula, a.any, temp)
    print(f"Escrit: {p1} (full {temp})")
    p2 = os.path.join(HERE, f"Venda {a.any} en € i %.xlsx")
    if os.path.exists(p2):
        r = escriu_unitats_totals(p2, tot_mes)
        print(f"Escrit: {p2} (fila {r} unitats, fila {r + 1} %)")


if __name__ == "__main__":
    main()
