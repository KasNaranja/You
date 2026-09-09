# -*- coding: utf-8 -*-
"""
Càlcul de reposició Zalando per SKU i per model_color.

Fonts (carpeta de dades, per defecte la carpeta on hi ha aquest script):
  Models a reposar.xlsx              llista base de SKUs a reposar (EAN, SKU, season, gènere, model_color, talla...)
  NIVEL.xlsx                         nivells i desglossament per talla (MUJER / CABALLERO / NIÑO)
  Vendes/2025/Venda 2025.xlsx        acumulat 2025 per model_color
  Vendes/2026/<mes>/VENDES DEL dd.mm al dd.mm.xlsx   vendes setmanals (pestanya DADES2, una línia per comanda)
  Stock Toni Pons/*.txt              export SAP (UTF-16, tabuladors): Stock 01 02, Disponible 30 / 59 dies
  Stock Zalando/*.csv|*.xlsx         stock snapshot Zalando (EAN, Offerable, Non-offerable, Total)
  Enviaments pendents/*.csv          enviaments ja fets però encara no al snapshot (ean;quantity)
  VENTA POR MES.xlsx                 multiplicador de la venda setmanal per mes (fila de mesos + fila de valors)
  Creats Zalando HI26.xlsx           model_color HI26 ja creats a Zalando (columna MODEL_COLOR) -> columna CREAT HI26
  Informació models zalando/*.csv    export d'articles de zDirect (EAN x país, PVP i preu rebaixat) -> columna DTE (% dte a DE)
  Ajustos repo.xlsx (opcional)       multiplicador / nivell forçat per model_color

Regla:
  objectiu = venda setmanal del model_color x MULT (el del mes de càlcul a VENTA POR MES.xlsx; --mult el força)
  nivell   = el primer nivell de la taula del gènere amb què la suma de les talles QUE TÉ EL MODEL (= HAURIA)
             cobreix l'objectiu, o sigui HAURIA >= objectiu (p.ex. GEMINA-QT 35-42, objectiu 249 -> nivell 60, 274 parells)
  HAURIA   = desglossament per talla d'aquest nivell
  DIF      = HAURIA - stock Zalando (total) - enviaments pendents
  REPO     = DIF si és positiu
  PREPARABLE = min(REPO, stock disponible 30 dies a Toni Pons)

Sortides:
  Vendes/2026/Venda 2026 dd.mm.xlsx  consolidat de totes les setmanes (un fitxer per data de càlcul; el bo és sempre l'últim)
  REPO/REPO ZALANDO dd.mm.xlsx       pestanyes CÀLCUL SKU, MODEL_COLOR, FORA LLISTA, PARÀMETRES, NIVELLS
  REPO/REPO ZALANDO dd.mm.html       mateixes dues vistes, filtrables i ordenables
  (REPO/ penja de la carpeta de sortida, per defecte la de dades)

Ús:
  python repo_zalando.py                       (data = avui, MULT = 3, nivell mínim 6 dona i home, 2 nens)
  python repo_zalando.py --mult 3 --min-level 0 --min-level-kids 0      (sense nivell mínim)
  python repo_zalando.py --data "C:\\...\\Zalando reposició" --out "C:\\...\\sortida"
"""
from __future__ import annotations

import argparse
import datetime as dt
import glob
import html
import json
import os
import re
import sys
import unicodedata

import numpy as np
import openpyxl
import pandas as pd
from openpyxl.comments import Comment
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

# --------------------------------------------------------------------------------------
# Paràmetres
# --------------------------------------------------------------------------------------
GENDER_GROUP = {  # GÈNERE de "Models a reposar" -> bloc de NIVEL.xlsx
    "DONA": "MUJER",
    "HOME": "CABALLERO",
    "NENS": "NIÑO",
    "UNISEX": "MUJER",       # taula de dona; talles 46-47 = valor de la talla 45
    "MINI": "NIÑO",          # taula de nen; talles < 25 = valor de la talla 25
    "COMPLEMENTS": None,     # sense taula: HAURIA = objectiu (talla única)
}
KIDS_GROUPS = {"NIÑO"}
WEEK_RE = re.compile(r"DEL (\d\d)\.(\d\d) al (\d\d)\.(\d\d)", re.I)
SNAP_DATE_RE = re.compile(r"(\d\d)[_\-.](\d\d)[_\-.](\d{4})")
EXCLUDE_SALES = ("acumulat", "càlcul", "calcul", "ranking", "anàlisi", "analisi")
HTML_HIDE = {"VENDA 4 SETM"}  # columnes de l'Excel que no es mostren a l'HTML
COBERTURA_FACTOR = 2  # la cobertura es multiplica x2: la meitat del que es ven torna (devolucions) i torna a estar disponible

# Explicació de cada columna (comentari a la capçalera de l'Excel i tooltip a l'HTML)
COL_HELP = {
    "EAN": "Codi de barres de la talla (EAN-13). És la clau per creuar amb el snapshot de Zalando, els enviaments pendents i el stock de Toni Pons.",
    "SKU": "Codi SAP de l'article (model + color + talla + partida).",
    "SEASON": "Temporada Toni Pons segons 'Models a reposar' (ES26, HI26, HI25).",
    "TEMPORADA": "NOU = article nou de la temporada; CONTIN = continua de la temporada anterior.",
    "COL·LECCIÓ": "Col·lecció del model segons 'Models a reposar'.",
    "GÈNERE": "Gènere del model. Determina la taula de nivells: DONA i UNISEX → MUJER, HOME → CABALLERO, NENS i MINI → NIÑO, COMPLEMENTS sense taula.",
    "model": "Model (nom comercial) del calçat.",
    "color": "Color del model.",
    "model_color": "Model + color. És la unitat sobre la qual es mira la venda setmanal i es tria el nivell.",
    "talla": "Talla de l'article.",
    "SEASON ZLD": "Season amb què l'article està donat d'alta a Zalando (columna amb data de 'Models a reposar'). Buit = no constava a Zalando en aquella data.",
    "ES POT ENVIAR?": "Marca de 'Models a reposar' per als HI26 nous que ja es poden enviar (creats a Zalando). Buit = sense marca.",
    "CREAT A ZLD?": "SÍ, o NO CONSTA per als HI26 NOU sense marca a 'es pot enviar?'. Els NO CONSTA queden amb REPO = 0.",
    "CREAT HI26": "SÍ si el model_color és a la llista 'Creats Zalando HI26.xlsx' (articles HI26 creats a Zalando i que ja es poden enviar). Només informativa.",
    "VENDA SET": "Unitats venudes del model_color (totes les talles) la setmana de referència (INITIAL+SHIPPED de la pestanya DADES2). És la base del càlcul.",
    "ACUM'25": "Unitats venudes del model_color durant tot el 2025 (Venda 2025.xlsx).",
    "ACUM'26": "Unitats venudes del model_color el 2026 fins a la setmana de referència (suma de tots els fitxers setmanals).",
    "ACUM HI": "Unitats venudes del model_color des de l'1 de setembre (inici de la temporada d'hivern) fins a l'última setmana carregada, per data de comanda. Cada setmana s'hi va sumant.",
    "PREVISIÓ": "Parells que es preveu vendre des de l'última setmana carregada fins al 31/12: ACUM HI ÷ (part de la corba de la col·lecció ja transcorreguda des de l'1 de setembre) × (% de setembre a desembre) − ACUM HI. La corba és la del gènere i col·lecció de la pestanya Previsió demanda (la genèrica del gènere si la col·lecció no hi és). Només models HI26/HI25; buit si no hi ha corba o no hi ha venda des de l'1 de setembre.",
    "A COMPRAR": "PREVISIÓ − STOCK ZLD − ENV PENDENTS − DISPONIBLE ALMACÉN, si és positiu: parells que faltarien per cobrir la previsió fins al 31/12 amb el stock que ja tenim.",
    "VENDA 4 SETM": "Suma de les últimes 4 setmanes de venda del model_color. Només informativa.",
    "MULT": "Multiplicador de la venda setmanal. Surt de 'VENTA POR MES.xlsx' segons el mes de la data de càlcul (p.ex. setembre 3, abril 5). Es pot canviar per model_color a 'Ajustos repo.xlsx'.",
    "OBJECTIU": "VENDA SET × MULT: parells que hauria d'haver-hi a Zalando del model_color.",
    "NIVELL": "Nivell de NIVEL.xlsx escollit: el primer amb què la suma de les talles del model cobreix l'OBJECTIU (HAURIA ≥ OBJECTIU). Mínim 6 per dona i home i 2 per nens, encara que no hi hagi venda.",
    "HAURIA": "Parells que hauria d'haver-hi a Zalando segons el desglossament per talla del NIVELL a NIVEL.xlsx. A la vista model_color és la suma de totes les talles del model.",
    "STOCK ZLD": "Stock total a Zalando segons el snapshot (offerable + non-offerable, tots els magatzems).",
    "OFFERABLE": "Part del STOCK ZLD que Zalando té disponible per vendre.",
    "NON OFFERABLE": "Part del STOCK ZLD no disponible per vendre (en moviment intern, devolucions en procés, etc.).",
    "ENV PENDENTS": "Suma dels enviaments pendents: parells que ja han sortit de Toni Pons però encara no compten al stock de Zalando.",
    "COBERTURA SET": "Setmanes de venda que cobreix el stock: 2 × (STOCK ZLD + ENV PENDENTS) / VENDA SET. El ×2 compensa les devolucions, que tornen a estar disponibles. Buit si no hi ha venda. En vermell si és menys de 4 setmanes. Només informativa.",
    "DIF": "HAURIA − STOCK ZLD − ENV PENDENTS, talla per talla. Negatiu vol dir que sobra stock d'aquesta talla. A la vista model_color és el net de totes les talles.",
    "REPO": "Parells a reposar: el DIF de cada talla quan és positiu (si no, 0). A la vista model_color és la suma de les talles que van curtes. 0 si CREAT A ZLD? = NO CONSTA.",
    "STOCK TP 01 02": "Stock físic al magatzem de Toni Pons (columna 'Stock 01 02' de l'export SAP), sumat per EAN.",
    "DISPO 30 DIES": "Stock disponible a Toni Pons a 30 dies (columna 'Stock Disponible 30 Dies' de l'export SAP): el que queda lliure després de reservar les comandes dels propers 30 dies. A la vista model_color, en vermell si el model té menys de 100 parells.",
    "PREPARABLE": "Part del REPO que es pot preparar avui: el mínim entre REPO i DISPO 30 DIES, talla per talla.",
    "DISPONIBLE ALMACÉN": "Stock disponible a Toni Pons segons 'Previsió demanda/almacen_taula.xlsx' (pestanya ESTOC, columna SumCantidad_disponible), sumat per SKU i per model_color. Només es mostra a la pestanya Previsió demanda.",
    "DTE": "% de descompte actual a Zalando Alemanya (país DE): (PVP − preu rebaixat) / PVP, del CSV més recent de la carpeta 'Informació models zalando'. 0 = sense descompte. A la vista model_color, el màxim de les seves talles.",
    "VENDA SKU 1 SETM": "Unitats venudes d'aquesta talla la setmana de referència.",
    "VENDA SKU ACUM'26": "Unitats venudes d'aquesta talla el 2026.",
    "AVÍS": "Notes del càlcul: nivell mínim aplicat, talla fora de la taula de nivells, sense EAN, objectiu per sobre del nivell màxim, etc.",
}


def col_help(name: str) -> str:
    if name in COL_HELP:
        return COL_HELP[name]
    if str(name).startswith("ENV "):
        return f"Parells enviats el {name[4:]} que encara no apareixen al snapshot de Zalando (fitxer d'Enviaments pendents)."
    return ""


def norm(s: str) -> str:
    """minúscules sense accents, per comparar capçaleres."""
    s = unicodedata.normalize("NFKD", str(s))
    return "".join(c for c in s if not unicodedata.combining(c)).lower().strip()


def clean_ean(x) -> str | None:
    if x is None or (isinstance(x, float) and np.isnan(x)):
        return None
    s = str(x).strip()
    if s.endswith(".0"):
        s = s[:-2]
    if not re.fullmatch(r"\d{8,14}", s) or int(s) == 0:
        return None
    return s


def to_num(series: pd.Series) -> pd.Series:
    """'1.234,00' -> 1234.0 ; '12,00' -> 12.0 ; números tal qual."""
    if series.dtype.kind in "if":
        return series.fillna(0)
    s = series.astype(str).str.strip()
    s = s.where(~s.isin(["", "nan", "None"]), "0")
    has_comma = s.str.contains(",", regex=False)
    s = s.where(~has_comma, s.str.replace(".", "", regex=False).str.replace(",", ".", regex=False))
    return pd.to_numeric(s, errors="coerce").fillna(0)


CACHE_DIR = os.path.join(os.environ.get("LOCALAPPDATA", os.path.dirname(os.path.abspath(__file__))), "Temp", "zalando_repo_cache")


def readable_copy(path: str) -> str:
    """Camí llegible: si Excel/OneDrive tenen el fitxer obert i Python no pot obrir-lo,
    en fa una còpia amb l'API de Windows (CopyFileW) i retorna la còpia."""
    try:
        with open(path, "rb"):
            return path
    except PermissionError:
        pass
    os.makedirs(CACHE_DIR, exist_ok=True)
    dst = os.path.join(CACHE_DIR, "copia_" + os.path.basename(path))
    ok = False
    if os.name == "nt":
        import ctypes
        k32 = ctypes.windll.kernel32
        k32.CopyFileW.argtypes = [ctypes.c_wchar_p, ctypes.c_wchar_p, ctypes.c_bool]
        k32.CopyFileW.restype = ctypes.c_bool
        ok = bool(k32.CopyFileW(path, dst, False))
    if not ok:
        raise SystemExit(f"No puc llegir {os.path.basename(path)} (obert a Excel?). Tanca'l i torna-ho a provar.")
    print(f"AVÍS: {os.path.basename(path)} està obert a Excel; es llegeix una còpia.")
    return dst


def safe_out(path: str) -> str:
    """Si el fitxer de sortida està obert a Excel, escriu al costat amb el sufix ' (nou)'."""
    if os.path.exists(path):
        try:
            with open(path, "ab"):
                pass
        except PermissionError:
            root, ext = os.path.splitext(path)
            alt = f"{root} (nou){ext}"
            print(f"AVÍS: {os.path.basename(path)} està obert a Excel; s'escriu {os.path.basename(alt)}")
            return safe_out(alt)
    return path


# --------------------------------------------------------------------------------------
# Càrrega de fonts
# --------------------------------------------------------------------------------------
def load_models(path: str) -> pd.DataFrame:
    df = pd.read_excel(path, dtype={"codigo_barra": str, "SKU": str})
    cols = {norm(c): c for c in df.columns}
    ren = {}
    for want, keys in {
        "EAN": ["codigo_barra", "ean"],
        "SKU": ["sku"],
        "SEASON": ["season"],
        "TEMPORADA": ["temporada"],
        "COL·LECCIÓ": ["col·leccio", "colleccio", "coleccion", "col·lecció"],
        "GÈNERE": ["genere", "gènere", "sexe", "genero"],
        "model": ["model"],
        "color": ["color"],
        "model_color": ["model_color"],
        "talla": ["talla"],
        "ES POT ENVIAR?": ["es pot enviar?", "es pot enviar"],
    }.items():
        for k in keys:
            if norm(k) in cols:
                ren[cols[norm(k)]] = want
                break
    # la columna amb la season de Zalando porta una data com a capçalera (p.ex. "12/08")
    for c in df.columns:
        if c not in ren and re.fullmatch(r"\d{1,2}/\d{1,2}", str(c).strip()):
            ren[c] = "SEASON ZLD"
    df = df.rename(columns=ren)
    for c in ["SEASON ZLD", "ES POT ENVIAR?"]:
        if c not in df.columns:
            df[c] = np.nan
    df = df[df["model_color"].notna()].copy()
    df["EAN"] = df["EAN"].map(clean_ean)
    df["talla"] = df["talla"].map(lambda t: re.sub(r"\.0$", "", str(t).strip()))
    df["GÈNERE"] = df["GÈNERE"].astype(str).str.strip().str.upper()
    ep = df["ES POT ENVIAR?"].fillna("").astype(str).str.strip()
    df["ES POT ENVIAR?"] = ep.where(~ep.isin(["#N/A", "nan", "None", "<NA>"]), "")
    return df


def load_levels(path: str) -> dict:
    """Retorna {grup: {'levels': [int...], 'table': {level: {talla_str: qty}}}}"""
    wb = openpyxl.load_workbook(path, data_only=True)
    ws = wb[wb.sheetnames[0]]
    rows = [list(r) for r in ws.iter_rows(values_only=True)]
    groups: dict = {}
    current = None
    levels: list[int] = []
    for r in rows:
        first = r[0]
        if isinstance(first, str) and first.strip() and norm(first) != "nivel":
            current = first.strip().upper()
            groups[current] = {"levels": [], "table": {}}
            levels = []
            continue
        if isinstance(first, str) and norm(first) == "nivel":
            levels = [int(v) for v in r[1:] if isinstance(v, (int, float))]
            groups[current]["levels"] = levels
            for lv in levels:
                groups[current]["table"][lv] = {}
            continue
        if current and levels and isinstance(first, (int, float)):
            talla = str(int(first))
            for lv, v in zip(levels, r[1 : 1 + len(levels)]):
                groups[current]["table"][lv][talla] = int(v) if isinstance(v, (int, float)) else 0
    # normalitza noms de grup (NIÑO pot venir com NINO)
    out = {}
    for g, d in groups.items():
        key = {"MUJER": "MUJER", "CABALLERO": "CABALLERO", "NINO": "NIÑO", "NIÑO": "NIÑO"}.get(norm(g).upper(), g)
        d["totals"] = {lv: int(sum(t.values())) for lv, t in d["table"].items()}  # parells de tot el nivell
        out[key] = d
    return out


def sales_files(data_dir: str) -> list[str]:
    patterns = [os.path.join(data_dir, "Vendes", "20*", "**", "*.xlsx"),   # Vendes/2026/<mes>/VENDES DEL dd.mm al dd.mm.xlsx
                os.path.join(data_dir, "Vendes 20*", "*", "*.xlsx")]        # disposició antiga (Vendes 2026/<mes>/)
    files = sorted({f for p in patterns for f in glob.glob(p, recursive=True)})
    out = []
    for f in files:
        base = os.path.basename(f)
        if base.startswith("~$"):
            continue
        if any(x in norm(base) for x in EXCLUDE_SALES):
            continue
        if not WEEK_RE.search(base):
            continue
        out.append(f)
    return out


def week_range(path: str) -> tuple[pd.Timestamp, pd.Timestamp]:
    m = WEEK_RE.search(os.path.basename(path))
    d1, m1, d2, m2 = map(int, m.groups())
    ym = re.search(r"Vendes[\\/ ](20\d\d)", path)
    base_year = int(ym.group(1)) if ym else dt.date.today().year
    y1 = base_year - 1 if m1 > m2 else base_year
    return pd.Timestamp(y1, m1, d1), pd.Timestamp(base_year, m2, d2)


def read_dades2(path: str) -> pd.DataFrame:
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    sheet = "DADES2" if "DADES2" in wb.sheetnames else None
    if sheet is None:
        raise ValueError(f"{os.path.basename(path)}: no té pestanya DADES2")
    ws = wb[sheet]
    it = ws.iter_rows(values_only=True)
    hdr = [norm(h) if h is not None else "" for h in next(it)]
    idx = {h: i for i, h in enumerate(hdr) if h}
    need = ["model_color", "talla", "initial+shipped"]
    for n in need:
        if n not in idx:
            raise ValueError(f"{os.path.basename(path)}: DADES2 sense columna {n}")
    cm, ct, cq = idx["model_color"], idx["talla"], idx["initial+shipped"]
    cmod, ccol = idx.get("model"), idx.get("color")
    ceur = next((idx[h] for h in idx if h.startswith("venda")), None)
    cret = idx.get("quantity_returned")
    cext = idx.get("external_id")
    recs, exts = [], []
    for r in it:
        if r[cm] is None:
            continue
        q = r[cq] if isinstance(r[cq], (int, float)) else 0
        eur = r[ceur] if (ceur is not None and isinstance(r[ceur], (int, float))) else 0.0
        ret = r[cret] if (cret is not None and isinstance(r[cret], (int, float))) else 0
        recs.append((r[cmod] if cmod is not None else None, r[ccol] if ccol is not None else None,
                     str(r[cm]).strip(), str(r[ct]).strip() if r[ct] is not None else "", q, eur, ret))
        exts.append(str(r[cext] or "") if cext is not None else "")
    df = pd.DataFrame(recs, columns=["MODEL", "COLOR", "MODEL_COLOR", "TALLA", "units", "eur", "returned"])
    df["TALLA"] = df["TALLA"].str.replace(r"\.0$", "", regex=True)
    df["has_eur"] = ceur is not None
    # data de comanda: pestanya DADES (una fila per línia de comanda, mateix ordre que DADES2)
    dates = None
    if "DADES" in wb.sheetnames:
        it1 = wb["DADES"].iter_rows(values_only=True)
        h1 = [norm(h) if h is not None else "" for h in next(it1, [])]
        i_d = h1.index("order_date") if "order_date" in h1 else (h1.index("created_at") if "created_at" in h1 else None)
        i_e = h1.index("external_id") if "external_id" in h1 else None
        if i_d is not None:
            rows1 = [r for r in it1 if any(v is not None for v in r)]
            if len(rows1) == len(df) and (i_e is None or all(str(r[i_e] or "") == e for r, e in zip(rows1, exts))):
                def _d(v):
                    if isinstance(v, str):
                        try:
                            return pd.Timestamp(v[:19])
                        except ValueError:
                            return pd.NaT
                    return pd.Timestamp(v) if isinstance(v, (dt.datetime, dt.date)) else pd.NaT
                dates = [_d(r[i_d]).normalize() if not pd.isna(_d(r[i_d])) else pd.NaT for r in rows1]
    df["data"] = pd.to_datetime(dates) if dates is not None else pd.NaT
    return df


def load_sales(data_dir: str, cache_dir: str) -> tuple[pd.DataFrame, list[dict]]:
    os.makedirs(cache_dir, exist_ok=True)
    frames, sources = [], []
    for f in sales_files(data_dir):
        start, end = week_range(f)
        mtime = int(os.path.getmtime(f))
        cache = os.path.join(cache_dir, f"{os.path.basename(f)}.{mtime}.v2.parquet")
        if os.path.exists(cache):
            df = pd.read_parquet(cache)
        else:
            df = read_dades2(readable_copy(f))
            try:
                df.to_parquet(cache)
            except Exception:
                pass
        if "data" not in df.columns:
            df["data"] = pd.NaT
        df["data"] = pd.to_datetime(df["data"]).fillna(pd.Timestamp(start))   # sense data de comanda: inici de la setmana
        df = df.assign(start=start, end=end, file=os.path.basename(f))
        frames.append(df)
        sources.append({"fitxer": os.path.basename(f), "inici": start.date().isoformat(), "fi": end.date().isoformat(),
                        "unitats": int(df["units"].sum()), "eur": round(float(df["eur"].sum()), 2),
                        "amb_eur": bool(df["has_eur"].iloc[0]) if len(df) else False})
    if not frames:
        raise SystemExit("No s'ha trobat cap fitxer de vendes setmanals a 'Vendes 20xx/'")
    lines = pd.concat(frames, ignore_index=True)
    # setmanes duplicades (mateix rang en dos fitxers) -> avisa i queda't amb el primer
    dup = lines.drop_duplicates(["file", "start", "end"]).duplicated(["start", "end"], keep="first")
    if dup.any():
        bad = lines.drop_duplicates(["file", "start", "end"])[dup]["file"].tolist()
        print("AVÍS: setmanes duplicades, s'ignoren:", bad)
        lines = lines[~lines["file"].isin(bad)]
    return lines, sorted(sources, key=lambda s: s["inici"])


def load_sales_2025(path: str) -> pd.Series:
    raw = pd.read_excel(path, header=None)
    hdr_row = None
    for i in range(min(10, len(raw))):
        if any(norm(v) == "etiquetas de fila" for v in raw.iloc[i].tolist() if isinstance(v, str)):
            hdr_row = i
            break
    if hdr_row is None:
        hdr_row = 0
    df = raw.iloc[hdr_row + 1 :, :2].copy()
    df.columns = ["model_color", "units"]
    df = df[df["model_color"].notna() & (df["model_color"].astype(str) != "Total general")]
    df["units"] = pd.to_numeric(df["units"], errors="coerce").fillna(0)
    return df.groupby(df["model_color"].astype(str).str.strip())["units"].sum()


def load_stock_tp(folder: str) -> tuple[pd.DataFrame, str]:
    files = sorted(glob.glob(os.path.join(folder, "*.txt")), key=os.path.getmtime)
    if not files:
        raise SystemExit(f"No hi ha cap .txt a {folder}")
    path = files[-1]
    df = pd.read_csv(readable_copy(path), sep="\t", encoding="utf-16", dtype=str)
    cols = {norm(c): c for c in df.columns}
    ean_col = cols.get("codigo de barras") or cols.get("código de barras") or cols.get("ean")
    c0102 = cols.get("stock 01 02")
    c30 = cols.get("stock disponible 30 dies")
    c59 = cols.get("stock disponible 59 dies")
    if not all([ean_col, c0102, c30, c59]):
        raise SystemExit(f"Columnes no trobades a {os.path.basename(path)}: {list(df.columns)}")
    out = pd.DataFrame({
        "EAN": df[ean_col].map(clean_ean),
        "STOCK TP 01 02": to_num(df[c0102]),
        "DISPO 30 DIES": to_num(df[c30]),
        "DISPO 59 DIES": to_num(df[c59]),
    })
    out = out[out["EAN"].notna()].groupby("EAN", as_index=False).sum()
    return out, os.path.basename(path)


def _snapshot_frame(path: str) -> pd.DataFrame | None:
    """Llegeix un snapshot (csv o xlsx) i retorna EAN / Offerable / Non-offerable / Total, o None si no és vàlid."""
    ext = os.path.splitext(path)[1].lower()
    path = readable_copy(path)
    df = None
    if ext == ".csv":
        with open(path, "r", encoding="utf-8-sig", errors="replace") as fh:
            head = fh.readline()
        sep = ";" if head.count(";") >= head.count(",") else ","
        df = pd.read_csv(path, sep=sep, dtype=str, encoding="utf-8-sig", encoding_errors="replace")
    elif ext in (".xlsx", ".xlsm"):
        wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
        for sn in wb.sheetnames:
            ws = wb[sn]
            it = ws.iter_rows(values_only=True)
            first = next(it, None)
            if first and any(norm(v) == "ean" for v in first if v is not None):
                hdr = [str(v) if v is not None else f"c{i}" for i, v in enumerate(first)]
                df = pd.DataFrame(list(it), columns=hdr)
                break
    if df is None or df.empty:
        return None
    cols = {norm(c): c for c in df.columns}
    ean_col = cols.get("ean")
    if ean_col is None:
        return None
    off = cols.get("offerable stock")
    non = cols.get("non-offerable stock")
    tot = cols.get("total")
    if off is None or tot is None:
        return None
    out = pd.DataFrame({
        "EAN": df[ean_col].map(clean_ean),
        "OFFERABLE": to_num(df[off]),
        "NON OFFERABLE": to_num(df[non]) if non else 0,
        "STOCK ZLD": to_num(df[tot]),
    })
    valid = out["EAN"].notna().mean()
    if valid < 0.9:   # EANs en notació científica (8,43453E+12) o buits
        return None
    return out[out["EAN"].notna()].groupby("EAN", as_index=False).sum()


def load_snapshot(folder: str, extra_paths: list[str] | None = None) -> tuple[pd.DataFrame, dict]:
    cands = sorted(glob.glob(os.path.join(folder, "*.csv")) + glob.glob(os.path.join(folder, "*.xlsx")))
    cands = [c for c in cands if not os.path.basename(c).startswith("~$")]
    if extra_paths:
        cands += [p for p in extra_paths if os.path.exists(p)]
    dated = []
    for c in cands:
        m = SNAP_DATE_RE.search(os.path.basename(c))
        d = dt.date(int(m.group(3)), int(m.group(2)), int(m.group(1))) if m else dt.date.fromtimestamp(os.path.getmtime(c))
        dated.append((d, c))
    rejected, chosen, frame = [], None, None
    for d, c in sorted(dated, reverse=True):
        fr = _snapshot_frame(c)
        if fr is None:
            rejected.append(os.path.basename(c))
            continue
        chosen, frame = (d, c), fr
        break
    if frame is None:
        raise SystemExit("Cap snapshot de stock Zalando vàlid (EANs íntegres). Rebutjats: " + ", ".join(rejected))
    meta = {"fitxer": os.path.basename(chosen[1]), "data": chosen[0].isoformat(), "rebutjats": rejected,
            "eans": int(len(frame)), "total": int(frame["STOCK ZLD"].sum())}
    return frame, meta


def load_pending(folder: str) -> tuple[pd.DataFrame, list[str]]:
    files = sorted(glob.glob(os.path.join(folder, "*.csv")))
    frames, labels = [], []
    for f in files:
        base = os.path.basename(f)
        src = readable_copy(f)
        with open(src, "r", encoding="utf-8-sig", errors="replace") as fh:
            head = fh.readline()
        sep = ";" if head.count(";") >= head.count(",") else ","
        df = pd.read_csv(src, sep=sep, dtype=str, encoding="utf-8-sig", encoding_errors="replace")
        cols = {norm(c): c for c in df.columns}
        ec, qc = cols.get("ean"), cols.get("quantity") or cols.get("quantitat") or cols.get("qty")
        if ec is None or qc is None:
            print(f"AVÍS: {base} sense columnes ean/quantity, s'ignora")
            continue
        m = re.search(r"(\d\d)(\d\d)(\d{4})", base)
        if m:
            label = f"ENV {m.group(1)}.{m.group(2)}"
        else:  # sense data al nom: data de modificació del fitxer
            label = f"ENV {dt.date.fromtimestamp(os.path.getmtime(f)):%d.%m}"
        while label in labels:
            label += "'"
        labels.append(label)
        g = pd.DataFrame({"EAN": df[ec].map(clean_ean), label: to_num(df[qc])}).dropna(subset=["EAN"]).groupby("EAN", as_index=False).sum()
        frames.append(g)
    if not frames:
        return pd.DataFrame({"EAN": pd.Series(dtype=str), "ENV PENDENTS": pd.Series(dtype=float)}), []
    out = frames[0]
    for fr in frames[1:]:
        out = out.merge(fr, on="EAN", how="outer")
    out = out.fillna(0)
    out["ENV PENDENTS"] = out[labels].sum(axis=1)
    return out, labels


MONTHS = {  # nom de mes (sense accents, minúscules) -> número
    "enero": 1, "febrero": 2, "marzo": 3, "abril": 4, "mayo": 5, "junio": 6, "julio": 7, "agosto": 8,
    "septiembre": 9, "setiembre": 9, "octubre": 10, "noviembre": 11, "diciembre": 12,
    "gener": 1, "febrer": 2, "marc": 3, "maig": 5, "juny": 6, "juliol": 7, "agost": 8, "setembre": 9, "novembre": 11, "desembre": 12,
}
MONTH_NAMES_CA = ["", "gener", "febrer", "març", "abril", "maig", "juny", "juliol", "agost", "setembre", "octubre", "novembre", "desembre"]


def load_month_mult(path: str) -> dict[int, float]:
    """VENTA POR MES.xlsx: una fila amb els mesos i, a sota, el multiplicador de la venda setmanal de cada mes."""
    wb = openpyxl.load_workbook(path, data_only=True)
    ws = wb[wb.sheetnames[0]]
    rows = [list(r) for r in ws.iter_rows(values_only=True)]
    for i, r in enumerate(rows):
        cols = {j: MONTHS[norm(v)] for j, v in enumerate(r) if isinstance(v, str) and norm(v) in MONTHS}
        if len(cols) < 6:
            continue
        for r2 in rows[i + 1:]:
            vals = {m: float(r2[j]) for j, m in cols.items() if j < len(r2) and isinstance(r2[j], (int, float))}
            if len(vals) >= 6:
                return vals
    return {}


INFO_DATE_RE = re.compile(r"(\d{2})[._-](\d{2})(?:[._-](\d{4}))?")


def load_zalando_info(folder: str, country: str = "de") -> tuple[pd.DataFrame, dict]:
    """Informació models zalando dd.mm.csv (export d'articles de zDirect, una fila per EAN i país):
    % de descompte actual per EAN al país indicat = (regular_price - discounted_price) / regular_price."""
    empty = pd.DataFrame({"EAN": pd.Series(dtype=str), "DTE": pd.Series(dtype=int), "PVP DE": pd.Series(dtype=float)})
    if not os.path.isdir(folder):
        return empty, {}
    files = [f for f in glob.glob(os.path.join(folder, "*.csv")) if not os.path.basename(f).startswith("~$")]
    if not files:
        return empty, {}

    def fdate(f):
        m = INFO_DATE_RE.search(os.path.basename(f))
        if m:
            y = int(m.group(3)) if m.group(3) else dt.date.fromtimestamp(os.path.getmtime(f)).year
            try:
                return dt.date(y, int(m.group(2)), int(m.group(1)))
            except ValueError:
                pass
        return dt.date.fromtimestamp(os.path.getmtime(f))

    path = max(files, key=lambda f: (fdate(f), os.path.getmtime(f)))
    src = readable_copy(path)
    with open(src, "r", encoding="utf-8-sig", errors="replace") as fh:
        head = fh.readline()
    sep = ";" if head.count(";") >= head.count(",") else ","
    df = pd.read_csv(src, sep=sep, dtype=str, encoding="utf-8-sig", encoding_errors="replace",
                     usecols=lambda c: norm(c) in ("ean", "country", "regular_price", "discounted_price"))
    cols = {norm(c): c for c in df.columns}
    if not all(k in cols for k in ("ean", "country", "regular_price", "discounted_price")):
        raise SystemExit(f"{os.path.basename(path)}: falten columnes ean/country/regular_price/discounted_price")
    df = df[df[cols["country"]].astype(str).str.strip().str.lower() == country.lower()]
    reg = to_num(df[cols["regular_price"]]).to_numpy()
    disc = to_num(df[cols["discounted_price"]]).to_numpy()
    with np.errstate(divide="ignore", invalid="ignore"):
        dte = np.where((reg > 0) & (disc > 0) & (disc < reg), np.round((reg - disc) / np.where(reg > 0, reg, 1) * 100), 0).astype(int)
    out = pd.DataFrame({"EAN": df[cols["ean"]].map(clean_ean).to_numpy(), "DTE": dte, "PVP DE": reg})
    out = out[out["EAN"].notna()].groupby("EAN", as_index=False).agg(DTE=("DTE", "max"), **{"PVP DE": ("PVP DE", "max")})
    meta = {"fitxer": os.path.basename(path), "data": fdate(path).isoformat(), "eans": int(len(out)), "amb_dte": int((out["DTE"] > 0).sum()),
            "pais": country.upper()}
    return out, meta


def load_previsio(folder: str) -> dict | None:
    """Previsió demanda/Càlcul venda per col·leccio <any>.xlsx (generat per previsio_colleccions.py):
    blocs DONA/HOME/NEN amb una fila per col·lecció i el % de cada mes. Retorna l'estructura per a l'HTML."""
    files = [f for f in glob.glob(os.path.join(folder, "Càlcul venda per col·leccio *.xlsx")) if not os.path.basename(f).startswith("~$")]
    if not files:
        return None
    path = max(files, key=lambda f: (re.search(r"(20\d\d)", os.path.basename(f)).group(1) if re.search(r"(20\d\d)", os.path.basename(f)) else "", os.path.getmtime(f)))
    m = re.search(r"(20\d\d)", os.path.basename(path))
    wb = openpyxl.load_workbook(readable_copy(path), read_only=True, data_only=True)

    def num(v):
        return int(v) if isinstance(v, (int, float)) else 0

    seasons: dict = {}
    for ws in wb.worksheets:   # un full per temporada (HI26, ES26...)
        blocks, cur = [], None
        for r in ws.iter_rows(values_only=True):
            r = list(r) + [None] * (19 - len(r))
            b = r[1]
            if b in ("DONA", "HOME", "NEN"):
                cur = {"genere": b, "rows": []}
                blocks.append(cur)
                continue
            if cur is None or b is None:
                continue
            pct = r[2:14]
            ok = all(isinstance(v, (int, float)) for v in pct)
            cur["rows"].append({"colleccio": str(b), "pct": [float(v) for v in pct] if ok else None,
                                "unitats": num(r[15]), "models_venda": num(r[16]), "models_hi26": num(r[17]),
                                "nota": str(r[18]) if r[18] else "", "total": str(b).upper().startswith("TOTS ELS MODELS")})
        if blocks:
            seasons[ws.title.strip().upper()] = blocks
    hi = next((k for k in seasons if k.startswith("HI")), None)
    return {"any": int(m.group(1)) if m else None, "fitxer": os.path.basename(path), "blocks": seasons.get(hi, []), "seasons": seasons}


def load_almacen(folder: str) -> tuple[pd.DataFrame, dict]:
    """Previsió demanda/almacen_taula.xlsx, pestanya ESTOC: [SumCantidad_disponible] per codi d'article SAP (SKU)."""
    files = [f for f in glob.glob(os.path.join(folder, "almacen*.xlsx")) if not os.path.basename(f).startswith("~$")]
    empty = pd.DataFrame({"SKU": pd.Series(dtype=str), "DISPONIBLE ALMACÉN": pd.Series(dtype=float)})
    if not files:
        return empty, {}
    path = max(files, key=os.path.getmtime)
    wb = openpyxl.load_workbook(readable_copy(path), read_only=True, data_only=True)
    sheet = next((s for s in wb.sheetnames if norm(s) in ("estoc", "stock")), None)
    if sheet is None:
        raise SystemExit(f"{os.path.basename(path)}: no té la pestanya ESTOC")
    ws = wb[sheet]
    it = ws.iter_rows(values_only=True)
    i_sku = i_disp = None
    for r in it:  # la capçalera és la primera fila que conté el codi d'article i el disponible
        hs = [norm(v) if isinstance(v, str) else "" for v in r]
        for j, h in enumerate(hs):
            if "codigo de articulo" in h or "código de artículo" in h:
                i_sku = j
            if "sumcantidad_disponible" in h:
                i_disp = j
        if i_sku is not None and i_disp is not None:
            break
    if i_sku is None or i_disp is None:
        raise SystemExit(f"{os.path.basename(path)}: no trobo 'Código de artículo' i 'SumCantidad_disponible' a ESTOC")
    recs = [(str(r[i_sku]).strip(), r[i_disp]) for r in it if len(r) > max(i_sku, i_disp) and r[i_sku] and isinstance(r[i_disp], (int, float))]
    out = pd.DataFrame(recs, columns=["SKU", "DISPONIBLE ALMACÉN"]).groupby("SKU", as_index=False).sum()
    meta = {"fitxer": os.path.basename(path), "skus": int(len(out)), "total": int(out["DISPONIBLE ALMACÉN"].sum())}
    return out, meta


def previsio_fins_desembre(mc: pd.DataFrame, prev: dict | None, hi_start: dt.date, cover_end: dt.date) -> tuple[pd.Series, list[str], dict]:
    """PREVISIÓ per model_color: parells a vendre des de cover_end fins al 31/12, extrapolant ACUM HI amb la corba
    mensual (% del 2025) de la col·lecció del seu gènere. NaN si no hi ha corba, no és model d'hivern o no hi ha venda.
    També retorna el detall per model_color (total set-des previst, corba i origen) per al gràfic de l'HTML."""
    import calendar
    out = pd.Series(np.nan, index=mc.index, dtype=float)
    avisos: list[str] = []
    detail: dict = {}
    if not prev or not prev.get("blocks") or cover_end.month < 9 or cover_end < hi_start:
        return out, avisos, detail
    curves: dict = {}
    generic: dict = {}
    for b in prev["blocks"]:
        for r in b["rows"]:
            if not r["pct"]:
                continue
            if r.get("total"):
                generic[b["genere"]] = r["pct"]
            else:
                curves[(b["genere"], norm(r["colleccio"]))] = r["pct"]
    GEN = {"DONA": "DONA", "UNISEX": "DONA", "HOME": "HOME", "NENS": "NEN", "NEN": "NEN", "MINI": "NEN"}

    def corba(genere, colleccio):
        g = GEN.get(str(genere).upper())
        if g is None:
            return None, None
        c = norm(colleccio)
        for k in (c, c.replace(" dona", "").replace(" home", "").strip(), c.split("-")[0].strip(), c.split(" ")[0].strip()):
            if (g, k) in curves:
                return curves[(g, k)], k
        return generic.get(g), "genèrica"

    dim = calendar.monthrange(cover_end.year, cover_end.month)[1]
    usats = set()
    for i, r in mc.iterrows():
        if str(r.get("SEASON", "")).upper()[:2] != "HI" or r.get("ACUM HI", 0) <= 0:
            continue
        p, k = corba(r.get("GÈNERE"), r.get("COL·LECCIÓ"))
        if p is None:
            continue
        f = sum(p[m - 1] for m in range(9, cover_end.month)) + p[cover_end.month - 1] * cover_end.day / dim
        tot = sum(p[8:12])
        if f <= 0:
            continue
        total_sep_des = r["ACUM HI"] / f * tot
        out.at[i] = max(0.0, round(total_sep_des - r["ACUM HI"]))
        usats.add((r.get("GÈNERE"), r.get("COL·LECCIÓ"), k))
        detail[r["model_color"]] = {"total": round(float(total_sep_des), 1), "curve": [round(float(x), 5) for x in p],
                                    "src": ("genèrica " + str(GEN.get(str(r.get("GÈNERE")).upper()))) if k == "genèrica" else str(k).upper()}
    gen = sorted({f"{g}/{c}" for g, c, k in usats if k == "genèrica"})
    if gen:
        avisos.append("Col·leccions sense corba pròpia (s'usa la genèrica del gènere): " + ", ".join(gen))
    return out, avisos, detail


def load_created_hi26(path: str) -> set[str]:
    """Creats Zalando HI26.xlsx: llista de model_color HI26 ja creats a Zalando (columna MODEL_COLOR o MODEL + COLOR)."""
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    out: set[str] = set()
    for ws in wb.worksheets:
        it = ws.iter_rows(values_only=True)
        hdr = [norm(v) if v is not None else "" for v in next(it, [])]
        if "model_color" in hdr:
            j = hdr.index("model_color")
            out |= {str(r[j]).strip().upper() for r in it if j < len(r) and r[j]}
        elif "model" in hdr and "color" in hdr:
            a, b = hdr.index("model"), hdr.index("color")
            out |= {f"{str(r[a]).strip()}_{str(r[b]).strip()}".upper() for r in it if r[a] and r[b]}
    return out


def load_adjustments(path: str) -> pd.DataFrame:
    if not os.path.exists(path):
        return pd.DataFrame(columns=["model_color", "multiplicador", "nivell", "comentari"])
    df = pd.read_excel(readable_copy(path))
    cols = {norm(c): c for c in df.columns}
    out = pd.DataFrame({
        "model_color": df[cols["model_color"]].fillna("").astype(str).str.strip(),
        "multiplicador": pd.to_numeric(df[cols["multiplicador"]], errors="coerce") if "multiplicador" in cols else np.nan,
        "nivell": pd.to_numeric(df[cols["nivell"]], errors="coerce") if "nivell" in cols else np.nan,
        "comentari": df[cols["comentari"]] if "comentari" in cols else "",
    })
    return out[out["model_color"].ne("")]


# --------------------------------------------------------------------------------------
# Càlcul
# --------------------------------------------------------------------------------------
def pick_level(levels: list[int], totals: dict, target: float, min_level: int) -> tuple[int | None, str]:
    """Primer nivell (ordenats pel total de parells) el total del qual cobreix l'objectiu."""
    order = sorted(levels, key=lambda l: (totals.get(l, 0), l))
    if target <= 0:
        if min_level:
            lv = min_level if min_level in levels else next((l for l in order if l >= min_level), None)
            return lv, "nivell mínim"
        return None, ""
    for lv in order:
        if totals.get(lv, 0) >= target:
            if min_level and min_level in levels and totals.get(min_level, 0) > totals.get(lv, 0):
                return min_level, "nivell mínim"
            return lv, ""
    top = order[-1]
    return top, f"objectiu {int(target)} > màxim de la taula ({totals.get(top, 0)} parells, nivell {top})"


def size_qty(table: dict, group: str, gender: str, talla: str) -> tuple[int, str]:
    if talla in table:
        return table[talla], ""
    if gender == "UNISEX" and talla.isdigit() and int(talla) > 45 and "45" in table:
        return table["45"], "talles 46-47 = talla 45"
    if group == "NIÑO" and talla.isdigit() and int(talla) < 25 and "25" in table:
        return table["25"], "talles <25 = talla 25"
    return 0, f"talla {talla} fora de taula"


def compute(models: pd.DataFrame, levels: dict, lines: pd.DataFrame, acum25: pd.Series,
            stock_tp: pd.DataFrame, snap: pd.DataFrame, pending: pd.DataFrame, pend_labels: list[str],
            adjust: pd.DataFrame, mult: float, min_level: int, min_level_kids: int, max_level: int | None = None,
            created: set | None = None, zinfo: pd.DataFrame | None = None, hi_start: dt.date | None = None):
    last_end = lines["end"].max()
    last_start = lines.loc[lines["end"] == last_end, "start"].iloc[0]
    week_ends = sorted(lines["end"].unique())
    last4 = week_ends[-4:]
    lw = lines[lines["end"] == last_end]
    prev_end = week_ends[-2] if len(week_ends) > 1 else None
    pw = lines[lines["end"] == prev_end] if prev_end is not None else lines.iloc[0:0]

    mc_week = lw.groupby("MODEL_COLOR")["units"].sum()
    mc_prev = pw.groupby("MODEL_COLOR")["units"].sum()
    mc_4w = lines[lines["end"].isin(last4)].groupby("MODEL_COLOR")["units"].sum()
    mc_26 = lines.groupby("MODEL_COLOR")["units"].sum()
    hi_lines = lines[lines["data"] >= pd.Timestamp(hi_start)] if hi_start else lines.iloc[0:0]
    mc_hi = hi_lines.groupby("MODEL_COLOR")["units"].sum()
    sku_week = lw.groupby(["MODEL_COLOR", "TALLA"])["units"].sum()
    sku_26 = lines.groupby(["MODEL_COLOR", "TALLA"])["units"].sum()

    adj = adjust.set_index("model_color") if len(adjust) else adjust

    df = models.copy()
    df["VENDA SET"] = df["model_color"].map(mc_week).fillna(0).astype(int)
    df["VENDA SETM ANT"] = df["model_color"].map(mc_prev).fillna(0).astype(int)
    df["VENDA 4 SETM"] = df["model_color"].map(mc_4w).fillna(0).astype(int)
    df["ACUM'25"] = df["model_color"].map(acum25).fillna(0).astype(int)
    df["ACUM'26"] = df["model_color"].map(mc_26).fillna(0).astype(int)
    df["ACUM HI"] = df["model_color"].map(mc_hi).fillna(0).astype(int)
    key = list(zip(df["model_color"], df["talla"]))
    df["VENDA SKU 1 SETM"] = [int(sku_week.get(k, 0)) for k in key]
    df["VENDA SKU ACUM'26"] = [int(sku_26.get(k, 0)) for k in key]

    # multiplicador i nivell per model_color
    mults, forced = {}, {}
    for mc in df["model_color"].unique():
        m = mult
        f = None
        if len(adj) and mc in adj.index:
            row = adj.loc[mc]
            if isinstance(row, pd.DataFrame):
                row = row.iloc[0]
            if pd.notna(row.get("multiplicador", np.nan)):
                m = float(row["multiplicador"])
            if pd.notna(row.get("nivell", np.nan)):
                f = int(row["nivell"])
        mults[mc], forced[mc] = m, f
    df["MULT"] = df["model_color"].map(mults)
    df["OBJECTIU"] = (df["VENDA SET"] * df["MULT"]).round().astype(int)

    grp = [GENDER_GROUP.get(g, "?") for g in df["GÈNERE"]]
    df["GRUP NIVELL"] = [g or "" for g in grp]
    niv, hauria, avis = [], [], []
    mc_cache: dict = {}
    sizes_by_mc = df.groupby("model_color")["talla"].apply(list).to_dict()
    for i, r in enumerate(df.itertuples(index=False)):
        mc, gender, g, talla, target = r.model_color, r.GÈNERE, grp[i], r.talla, r.OBJECTIU
        notes = []
        if g == "?":
            niv.append(None); hauria.append(0); avis.append(f"gènere {gender} sense taula assignada")
            continue
        if g is None:
            # sense taula (complements): objectiu directe si talla única
            q = int(target) if talla.upper() in ("UNICA", "ÚNICA", "UNICO", "U") else 0
            niv.append(None); hauria.append(q); avis.append("sense taula de nivells")
            continue
        if g not in levels:
            niv.append(None); hauria.append(0); avis.append(f"grup {g} no és a NIVEL.xlsx")
            continue
        if mc not in mc_cache:
            lvls = [l for l in levels[g]["levels"] if max_level is None or l <= max_level] or levels[g]["levels"][:1]
            ml = min_level_kids if g in KIDS_GROUPS else min_level
            if forced.get(mc) is not None:
                lv = forced[mc] if forced[mc] in lvls else next((l for l in lvls if l >= forced[mc]), lvls[-1])
                mc_cache[mc] = (lv, f"nivell forçat {forced[mc]}")
            else:
                # total de cada nivell comptant només les talles que té aquest model_color (= el seu HAURIA)
                tbl = levels[g]["table"]
                tot_mc = {L: sum(size_qty(tbl[L], g, gender, t)[0] for t in sizes_by_mc[mc]) for L in lvls}
                mc_cache[mc] = pick_level(lvls, tot_mc, target, ml)
        lv, note = mc_cache[mc]
        if note:
            notes.append(note)
        if lv is None:
            niv.append(None); hauria.append(0); avis.append("; ".join(notes))
            continue
        q, n2 = size_qty(levels[g]["table"][lv], g, gender, talla)
        if n2:
            notes.append(n2)
        niv.append(lv); hauria.append(int(q)); avis.append("; ".join(notes))
    df["NIVELL"] = pd.array(niv, dtype="Int64")
    df["HAURIA"] = hauria
    df["AVÍS"] = avis

    # stocks
    df = df.merge(snap, on="EAN", how="left").merge(pending, on="EAN", how="left").merge(stock_tp, on="EAN", how="left")
    if zinfo is not None and len(zinfo):
        df = df.merge(zinfo[["EAN", "DTE"]], on="EAN", how="left")
    for c in ["STOCK ZLD", "OFFERABLE", "NON OFFERABLE", "ENV PENDENTS", "STOCK TP 01 02", "DISPO 30 DIES", "DISPO 59 DIES", "DTE"] + pend_labels:
        if c not in df.columns:
            df[c] = 0
        df[c] = df[c].fillna(0).astype(int)
    df.loc[df["EAN"].isna(), "AVÍS"] = (df.loc[df["EAN"].isna(), "AVÍS"] + "; sense EAN").str.strip("; ")

    # enviable? (HI26 NOU sense marca a 'es pot enviar?' = encara no creat a Zalando)
    not_created = (df["SEASON"].astype(str).str.upper() == "HI26") & (df["TEMPORADA"].astype(str).str.upper() == "NOU") & (df["ES POT ENVIAR?"] == "")
    df["CREAT A ZLD?"] = np.where(not_created, "NO CONSTA", "SÍ")
    df["CREAT HI26"] = np.where(df["model_color"].astype(str).str.strip().str.upper().isin(created or set()), "SÍ", "")

    df["DIF"] = df["HAURIA"] - df["STOCK ZLD"] - df["ENV PENDENTS"]
    df["REPO"] = np.where(df["CREAT A ZLD?"] == "SÍ", df["DIF"].clip(lower=0), 0).astype(int)
    df["PREPARABLE"] = np.minimum(df["REPO"], df["DISPO 30 DIES"]).astype(int)
    df["FALTA STOCK TP"] = (df["REPO"] - df["PREPARABLE"]).astype(int)

    def talla_key(t):
        return (0, int(t)) if str(t).isdigit() else (1, str(t))
    df["_tk"] = df["talla"].map(talla_key)
    df = df.sort_values(["VENDA SET", "model_color", "_tk"], ascending=[False, True, True]).drop(columns="_tk").reset_index(drop=True)

    sku_cols = ["EAN", "SKU", "SEASON", "TEMPORADA", "COL·LECCIÓ", "GÈNERE", "model", "color", "model_color", "talla",
                "SEASON ZLD", "ES POT ENVIAR?", "CREAT A ZLD?", "CREAT HI26", "VENDA SET", "ACUM'25", "ACUM'26", "ACUM HI", "VENDA 4 SETM",
                "MULT", "OBJECTIU", "NIVELL", "HAURIA", "STOCK ZLD", "OFFERABLE", "NON OFFERABLE"] + pend_labels + \
               ["ENV PENDENTS", "DIF", "REPO", "STOCK TP 01 02", "DISPO 30 DIES", "DTE", "PREPARABLE",
                "VENDA SKU 1 SETM", "VENDA SKU ACUM'26", "AVÍS"]
    sku = df[sku_cols].copy()

    # vista model_color
    first = {c: "first" for c in ["model", "color", "SEASON", "TEMPORADA", "COL·LECCIÓ", "GÈNERE", "SEASON ZLD", "ES POT ENVIAR?",
                                 "CREAT A ZLD?", "CREAT HI26", "VENDA SET", "VENDA SETM ANT", "VENDA 4 SETM", "MULT", "OBJECTIU", "GRUP NIVELL",
                                 "NIVELL", "ACUM'25", "ACUM'26", "ACUM HI"]}
    sums = {c: "sum" for c in ["HAURIA", "STOCK ZLD", "OFFERABLE", "ENV PENDENTS", "DIF", "REPO", "PREPARABLE", "FALTA STOCK TP",
                               "STOCK TP 01 02", "DISPO 30 DIES", "DISPO 59 DIES"]}
    sums["DTE"] = "max"
    mc = df.groupby("model_color").agg({**first, **sums, "talla": "count"}).rename(columns={"talla": "N TALLES"})
    mc["TALLES AMB REPO"] = df[df["REPO"] > 0].groupby("model_color").size().reindex(mc.index).fillna(0).astype(int)
    mc["TALLES SENSE STOCK ZLD"] = df[(df["STOCK ZLD"] + df["ENV PENDENTS"]) <= 0].groupby("model_color").size().reindex(mc.index).fillna(0).astype(int)
    cov = COBERTURA_FACTOR * (mc["STOCK ZLD"] + mc["ENV PENDENTS"]) / mc["VENDA SET"].replace(0, np.nan)
    mc["COBERTURA SET"] = cov.round(1)
    mc["AVÍS"] = df.groupby("model_color")["AVÍS"].agg(lambda s: "; ".join(sorted({x for x in s if x})))
    mc = mc.reset_index()
    mc_cols = ["model_color", "model", "color", "SEASON", "TEMPORADA", "COL·LECCIÓ", "GÈNERE", "SEASON ZLD", "CREAT A ZLD?", "CREAT HI26",
               "VENDA SET", "ACUM'25", "ACUM'26", "ACUM HI", "VENDA 4 SETM", "MULT", "OBJECTIU", "NIVELL", "HAURIA",
               "STOCK ZLD", "OFFERABLE", "ENV PENDENTS", "COBERTURA SET", "DIF", "REPO", "PREPARABLE",
               "STOCK TP 01 02", "DISPO 30 DIES", "DTE", "AVÍS"]
    mc = mc[mc_cols].sort_values(["VENDA SET", "REPO", "ACUM'26"], ascending=[False, False, False]).reset_index(drop=True)

    # vendes de la setmana de model_colors fora de la llista
    fora = lw[~lw["MODEL_COLOR"].isin(set(models["model_color"]))].groupby("MODEL_COLOR").agg(
        MODEL=("MODEL", "first"), COLOR=("COLOR", "first"), **{"VENDA SET": ("units", "sum")}).reset_index()
    fora["ACUM'26"] = fora["MODEL_COLOR"].map(mc_26).fillna(0).astype(int)
    fora["ACUM'25"] = fora["MODEL_COLOR"].map(acum25).fillna(0).astype(int)
    fora = fora.sort_values("VENDA SET", ascending=False).reset_index(drop=True)

    # venda mensual de l'any en curs per model_color (per data de comanda), per al gràfic de l'HTML
    yr = last_end.year
    ly = lines[lines["data"].dt.year == yr]
    mm = ly.groupby(["MODEL_COLOR", ly["data"].dt.month])["units"].sum()
    mc_months: dict = {}
    for (m_c, mth), v in mm.items():
        mc_months.setdefault(m_c, [0] * 12)[int(mth) - 1] = int(v)
    info = {"setmana_inici": last_start.date().isoformat(), "setmana_fi": last_end.date().isoformat(),
            "setmanes": len(week_ends), "setmana_ant": (prev_end.date().isoformat() if prev_end is not None else ""),
            "venda_setm_total": int(lw["units"].sum()), "venda_setm_llistat": int(mc["VENDA SET"].sum()),
            "any": yr, "mc_months": mc_months}
    return sku, mc, fora, info


# --------------------------------------------------------------------------------------
# Sortides
# --------------------------------------------------------------------------------------
HDR_FILL = PatternFill("solid", fgColor="1F3864")
HDR_FONT = Font(bold=True, color="FFFFFF")
REPO_FILL = PatternFill("solid", fgColor="E2F0D9")
NO_FILL = PatternFill("solid", fgColor="EDEDED")
KEY_FILL = PatternFill("solid", fgColor="FFF2CC")
GREY_HDR = "D9D9D9"
YELLOW_HDR = "FFE699"
GREEN_HDR = "C6E0B4"
ORANGE_HDR = "F8CBAD"
RED_FILL = PatternFill("solid", fgColor="FFC7CE")
RED_FONT = Font(color="9C0006")
RED_RULES_MC = {"COBERTURA SET": 4, "DISPO 30 DIES": 100}  # en vermell si el valor és < llindar (vista model_color)


def style_sheet(ws, df: pd.DataFrame, highlight_col: str | None = None, grey_col: str | None = None, key_cols=(), header_groups=(),
                red_rules: dict | None = None):
    ws.freeze_panes = "A2"
    ws.auto_filter.ref = ws.dimensions
    names = list(df.columns)
    hdr_fill = {}
    for start, end, color in header_groups:
        if start in names and end in names:
            for k in range(names.index(start), names.index(end) + 1):
                hdr_fill[k + 1] = PatternFill("solid", fgColor=color)
    for j, c in enumerate(df.columns, start=1):
        cell = ws.cell(row=1, column=j)
        cell.fill = hdr_fill.get(j, HDR_FILL)
        cell.font = Font(bold=True, color="000000") if j in hdr_fill else HDR_FONT
        txt = col_help(c)
        if txt:
            cell.comment = Comment(txt, "repo_zalando")
            cell.comment.width, cell.comment.height = 340, 120
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        if c in key_cols:
            for i in range(2, len(df) + 2):
                ws.cell(row=i, column=j).fill = KEY_FILL
        width = max(8, min(38, int(max([len(str(c))] + [len(str(v)) for v in df[c].head(300).tolist()]) * 1.1) + 1))
        if c in ("AVÍS",):
            width = 40
        ws.column_dimensions[get_column_letter(j)].width = width
    ws.row_dimensions[1].height = 32
    if highlight_col and highlight_col in df.columns:
        j = list(df.columns).index(highlight_col) + 1
        for i, v in enumerate(df[highlight_col].tolist(), start=2):
            if isinstance(v, (int, float)) and v > 0:
                ws.cell(row=i, column=j).fill = REPO_FILL
                ws.cell(row=i, column=j).font = Font(bold=True)
    if grey_col and grey_col in df.columns:
        j = list(df.columns).index(grey_col) + 1
        for i, v in enumerate(df[grey_col].tolist(), start=2):
            if v == "NO CONSTA":
                ws.cell(row=i, column=j).fill = NO_FILL
    if "DTE" in df.columns:  # percentatge sencer; els zeros no es mostren
        j = list(df.columns).index("DTE") + 1
        for i in range(2, len(df) + 2):
            ws.cell(row=i, column=j).number_format = '0"%";-0"%";'
    for col, threshold in (red_rules or {}).items():
        if col not in df.columns:
            continue
        j = list(df.columns).index(col) + 1
        for i, v in enumerate(df[col].tolist(), start=2):
            if isinstance(v, (int, float)) and not pd.isna(v) and v < threshold:
                ws.cell(row=i, column=j).fill = RED_FILL
                ws.cell(row=i, column=j).font = RED_FONT


def write_vendes(lines: pd.DataFrame, sources: list[dict], acum25: pd.Series, path: str, info: dict):
    last_end = lines["end"].max()
    lw = lines[lines["end"] == last_end]
    mc = lines.groupby("MODEL_COLOR").agg(MOD=("MODEL", "first"), COL=("COLOR", "first"), **{
        "2026 ACUMULAT": ("units", "sum"), "2026 EUR (des de 18.03)": ("eur", "sum"), "RETORNS 2026": ("returned", "sum")}).reset_index()
    mc = mc.rename(columns={"MODEL_COLOR": "model_color"})
    mc["2026 EUR (des de 18.03)"] = mc["2026 EUR (des de 18.03)"].round(2)
    wk_label = f"SETM {info['setmana_inici'][8:10]}.{info['setmana_inici'][5:7]}-{info['setmana_fi'][8:10]}.{info['setmana_fi'][5:7]}"
    mc[wk_label] = mc["model_color"].map(lw.groupby("MODEL_COLOR")["units"].sum()).fillna(0).astype(int)
    mc["2025 ACUMULAT"] = mc["model_color"].map(acum25).fillna(0).astype(int)
    mc = mc.sort_values("2026 ACUMULAT", ascending=False).reset_index(drop=True)
    sku = lines.groupby(["MODEL_COLOR", "TALLA"]).agg(**{"2026 ACUMULAT": ("units", "sum")}).reset_index()
    lw_sku = lw.groupby(["MODEL_COLOR", "TALLA"])["units"].sum()
    sku[wk_label] = [int(lw_sku.get(k, 0)) for k in zip(sku["MODEL_COLOR"], sku["TALLA"])]
    sku = sku.sort_values(["2026 ACUMULAT"], ascending=False).reset_index(drop=True)
    piv = lines.pivot_table(index="MODEL_COLOR", columns="end", values="units", aggfunc="sum", fill_value=0)
    piv.columns = [f"{c.day:02d}.{c.month:02d}" for c in piv.columns]
    piv["TOTAL"] = piv.sum(axis=1)
    piv = piv.sort_values("TOTAL", ascending=False).reset_index().rename(columns={"MODEL_COLOR": "model_color"})
    src = pd.DataFrame(sources).rename(columns={"fitxer": "FITXER", "inici": "INICI", "fi": "FI", "unitats": "UNITATS", "eur": "EUR", "amb_eur": "TÉ VENDA €"})
    with pd.ExcelWriter(path, engine="openpyxl") as xw:
        mc.to_excel(xw, sheet_name="MODEL_COLOR", index=False)
        sku.to_excel(xw, sheet_name="SKU", index=False)
        piv.to_excel(xw, sheet_name="SETMANES", index=False)
        src.to_excel(xw, sheet_name="FONTS", index=False)
        for name, d in [("MODEL_COLOR", mc), ("SKU", sku), ("SETMANES", piv), ("FONTS", src)]:
            style_sheet(xw.sheets[name], d)
    return mc


def write_excel(sku: pd.DataFrame, mc: pd.DataFrame, fora: pd.DataFrame, params: list[tuple], levels: dict, path: str):
    lvl_rows = []
    for g, d in levels.items():
        lvl_rows.append([g] + d["levels"])
        sizes = sorted({t for lv in d["table"].values() for t in lv}, key=lambda t: (len(t), t))
        for t in sizes:
            lvl_rows.append([t] + [d["table"][lv].get(t, 0) for lv in d["levels"]])
        lvl_rows.append(["TOTAL PARELLS"] + [d["totals"][lv] for lv in d["levels"]])
        lvl_rows.append([])
    width = max(len(r) for r in lvl_rows)
    lvl = pd.DataFrame([r + [None] * (width - len(r)) for r in lvl_rows], columns=["NIVELL"] + [f"c{i}" for i in range(1, width)])
    par = pd.DataFrame(params, columns=["PARÀMETRE", "VALOR"])
    with pd.ExcelWriter(path, engine="openpyxl") as xw:
        sku.to_excel(xw, sheet_name="CÀLCUL SKU", index=False)
        mc.to_excel(xw, sheet_name="MODEL_COLOR", index=False)
        fora.to_excel(xw, sheet_name="FORA LLISTA", index=False)
        par.to_excel(xw, sheet_name="PARÀMETRES", index=False)
        lvl.to_excel(xw, sheet_name="NIVELLS", index=False, header=False)
        groups_sku = (("EAN", "CREAT HI26", GREY_HDR), ("VENDA SET", "OBJECTIU", YELLOW_HDR), ("DIF", sku.columns[-1], GREEN_HDR), ("DTE", "DTE", ORANGE_HDR))
        groups_mc = (("model_color", "CREAT HI26", GREY_HDR), ("VENDA SET", "OBJECTIU", YELLOW_HDR), ("DIF", mc.columns[-1], GREEN_HDR), ("DTE", "DTE", ORANGE_HDR),
                     ("PREVISIÓ", "A COMPRAR", ORANGE_HDR))
        style_sheet(xw.sheets["CÀLCUL SKU"], sku, highlight_col="REPO", grey_col="CREAT A ZLD?", key_cols=("HAURIA", "DIF", "REPO", "PREPARABLE"), header_groups=groups_sku)
        style_sheet(xw.sheets["MODEL_COLOR"], mc, highlight_col="REPO", grey_col="CREAT A ZLD?", key_cols=("HAURIA", "REPO", "PREPARABLE"), header_groups=groups_mc,
                    red_rules=RED_RULES_MC)
        # columnes de previsió: ocultes als fulls de càlcul (es veuen a la pestanya Previsió demanda de l'HTML); Excel > Mostrar per veure-les
        for sheet_name, frame, cols_ in (("CÀLCUL SKU", sku, ("ACUM HI",)), ("MODEL_COLOR", mc, ("ACUM HI", "PREVISIÓ", "A COMPRAR"))):
            for c in cols_:
                if c in frame.columns:
                    xw.sheets[sheet_name].column_dimensions[get_column_letter(list(frame.columns).index(c) + 1)].hidden = True
        style_sheet(xw.sheets["FORA LLISTA"], fora)
        style_sheet(xw.sheets["PARÀMETRES"], par)
        xw.sheets["PARÀMETRES"].column_dimensions["A"].width = 34
        xw.sheets["PARÀMETRES"].column_dimensions["B"].width = 110


HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="ca"><head><meta charset="utf-8"><title>__TITLE__</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
:root{--bg:#f6f7f9;--card:#fff;--ink:#1c2430;--muted:#66717f;--line:#e3e7ec;--head:#1f3864;--accent:#2e7d32;--warn:#b26a00;--bad:#b3261e}
*{box-sizing:border-box}body{margin:0;font:14px/1.4 system-ui,Segoe UI,Roboto,Arial,sans-serif;color:var(--ink);background:var(--bg)}
header{background:var(--head);color:#fff;padding:14px 22px}header h1{margin:0;font-size:19px;font-weight:600}
header .sub{opacity:.85;font-size:12.5px;margin-top:4px}
.warn{background:#fff4e5;border-left:4px solid var(--warn);color:#5a3a00;padding:8px 14px;margin:12px 22px 0;border-radius:4px;font-size:13px}
.tabs{display:flex;gap:6px;padding:14px 22px 0}
.tab{border:1px solid var(--line);border-bottom:none;background:#e9edf2;padding:8px 16px;border-radius:8px 8px 0 0;cursor:pointer;font-weight:600;color:var(--muted)}
.tab.active{background:var(--card);color:var(--ink)}
.panel{display:none;background:var(--card);margin:0 22px 22px;border:1px solid var(--line);border-radius:0 8px 8px 8px;padding:12px}
.panel.active{display:block}
.bar{display:flex;flex-wrap:wrap;gap:10px;align-items:center;margin-bottom:10px}
.bar input[type=text]{padding:7px 10px;border:1px solid var(--line);border-radius:6px;min-width:260px}
.bar select{padding:6px 8px;border:1px solid var(--line);border-radius:6px;background:#fff}
.bar label{font-size:13px;color:var(--muted);display:flex;gap:4px;align-items:center}
.kpis{display:flex;flex-wrap:wrap;gap:10px;margin:0 0 10px}
.kpi{background:#f1f4f8;border-radius:8px;padding:8px 14px;min-width:120px}.kpi b{display:block;font-size:20px}.kpi span{font-size:12px;color:var(--muted)}
.kpi small{display:block;font-size:11.5px;color:var(--ink);margin-top:3px;border-top:1px solid var(--line);padding-top:3px}
.wrap{overflow:auto;max-height:78vh;border:1px solid var(--line);border-radius:0 0 6px 6px}
table{border-collapse:separate;border-spacing:0;width:max-content;min-width:100%;font-size:12.5px}
th{position:sticky;top:0;background:var(--head);color:#fff;padding:6px 8px;text-align:left;cursor:pointer;white-space:nowrap;user-select:none;z-index:2;border-right:1px solid rgba(255,255,255,.12)}
th.num{text-align:right}th .arr{opacity:.7;font-size:10px;margin-left:3px}
th.hg-grey{background:#d9d9d9;color:#1c2430}th.hg-yellow{background:#ffe699;color:#1c2430}th.hg-green{background:#c6e0b4;color:#1c2430}th.hg-orange{background:#f8cbad;color:#1c2430}
td.mclink{cursor:pointer;color:#1f3864;font-weight:600}td.mclink:hover{text-decoration:underline}
.modal{position:fixed;inset:0;background:rgba(15,23,42,.45);display:flex;align-items:center;justify-content:center;z-index:100;padding:16px}
.modal .card{background:#fff;border-radius:14px;box-shadow:0 24px 70px rgba(0,0,0,.35);width:min(900px,96vw);max-height:94vh;overflow:auto;padding:18px 22px 16px}
.mhead{display:flex;justify-content:space-between;align-items:flex-start;gap:12px;margin-bottom:10px}
.mtitle{font-size:20px;font-weight:700;color:#1f3864}.msub{font-size:12.5px;color:var(--muted);margin-top:2px}
.mclose{border:none;background:#f1f4f8;border-radius:50%;width:34px;height:34px;font-size:22px;line-height:1;cursor:pointer;color:#4a5c7a}.mclose:hover{background:#e3e9f1}
.chips{display:flex;flex-wrap:wrap;gap:8px;margin:0 0 12px}.chip{background:#f1f4f8;border-radius:10px;padding:6px 12px;min-width:110px}.chip span{display:block;font-size:11px;color:var(--muted)}.chip b{font-size:16px;color:#1c2430}
.legend{font-size:12px;color:var(--muted);margin-top:6px;display:flex;flex-wrap:wrap;gap:6px;align-items:center}
.lg{display:inline-block;width:16px;height:12px;border-radius:3px;vertical-align:middle;margin:0 2px 0 6px}.lg.solid{background:#1f3864}.lg.fc{background:rgba(31,56,100,.18);border:1px dashed rgba(31,56,100,.6)}
details.calc{margin-top:10px;background:#f7f8fa;border-radius:10px;padding:8px 14px;font-size:12.5px;color:var(--ink)}details.calc summary{cursor:pointer;font-weight:600;color:#1f3864}details.calc ol{margin:8px 0 2px 18px;padding:0}details.calc li{margin:3px 0}
.prevwrap{max-height:none!important}
table.prev tr.gen{cursor:pointer}table.prev tr.gen td{background:#eef2f6;font-weight:600}table.prev tr.gen:hover td{background:#e3e9f1}
table.prev tr.gen td.sticky{background:#eef2f6}table.prev .tri{display:inline-block;width:14px;color:var(--muted)}
table.prev td small{color:var(--muted);font-size:10.5px;margin-left:5px;font-weight:400}
table.prev td.generic{font-style:italic;color:var(--muted)}table.prev td.heat{font-variant-numeric:tabular-nums}
table.prev th.num,table.prev td.num{text-align:right}
table.prev th{overflow:hidden;text-overflow:ellipsis}table.prev td{overflow:hidden;text-overflow:ellipsis}
.subpanel{margin-top:22px;border-top:1px solid var(--line);padding-top:12px}.subpanel h3{font-size:14px;margin:0 0 8px;color:var(--muted);font-weight:600}
.prevsec{margin-bottom:34px}.prevsec>h2{font-size:19px;color:#1f3864;margin:4px 0 12px;letter-spacing:.6px;border-left:5px solid #1f3864;padding-left:10px}
.prevsec .wrap{max-height:none!important}
.kpis:empty{display:none}
.btn.primary{background:#1f3864;color:#fff;border-color:#1f3864}.btn.primary:hover{background:#2c4a7c}
th.selcol,td.selcol{width:36px;text-align:center;padding:4px 6px;overflow:visible}
th.selcol input,td.selcol input{width:16px;height:16px;margin:0;cursor:pointer;accent-color:#1f3864;vertical-align:middle}
tr.sel td{background:#dde8f7}tr.sel:hover td{background:#cfdff3}tr.sel td.repo{background:#c5e3b6}tr.sel td.sticky{background:#dde8f7}
.selinfo{font-size:12.5px;font-weight:600;color:var(--ink)}
.btn.small{padding:5px 10px;font-size:12.5px}
td.empty{padding:18px 14px;color:var(--muted);font-style:italic;white-space:normal}
th{overflow:hidden}th .rs{position:absolute;top:0;right:0;width:8px;height:100%;cursor:col-resize;user-select:none}
th .rs:hover,th.resizing .rs{background:rgba(255,255,255,.45)}th.resizing{background:#2c4a7c}
td{overflow:hidden;text-overflow:ellipsis}
[hidden]{display:none!important}
.btn{padding:7px 12px;border:1px solid var(--line);border-radius:6px;background:#fff;cursor:pointer;font-weight:600;color:var(--ink)}
.colwrap{position:relative}
.colpick{position:absolute;top:110%;left:0;z-index:20;background:#fff;border:1px solid var(--line);border-radius:8px;box-shadow:0 8px 24px rgba(0,0,0,.15);padding:10px;min-width:560px;max-height:60vh;overflow:auto}
.cp-grid{display:grid;grid-template-columns:repeat(3,minmax(160px,1fr));gap:4px 14px;font-size:12.5px}
.cp-grid label{display:flex;gap:6px;align-items:center;white-space:nowrap;cursor:pointer}
.cp-actions{display:flex;gap:8px;align-items:center;margin-bottom:8px;font-size:12px;color:var(--muted)}
.cp-actions button{padding:4px 10px;border:1px solid var(--line);border-radius:6px;background:#f1f4f8;cursor:pointer}
.topscroll{overflow-x:auto;overflow-y:hidden;height:18px;border:1px solid var(--line);border-bottom:none;border-radius:6px 6px 0 0;background:#fff}
.topscroll>div{height:1px}
.wrap::-webkit-scrollbar,.topscroll::-webkit-scrollbar{height:14px;width:14px}
.wrap::-webkit-scrollbar-thumb,.topscroll::-webkit-scrollbar-thumb{background:#8a97a6;border-radius:8px;border:3px solid #fff}
.wrap::-webkit-scrollbar-track,.topscroll::-webkit-scrollbar-track{background:#e9edf2}
th.sticky{left:0;z-index:4}
td.sticky{position:sticky;left:0;background:#fff;z-index:1;box-shadow:1px 0 0 var(--line)}
tr:hover td.sticky{background:#f4f7fb}
tfoot td.sticky{background:#eef2f6;z-index:3}
td{padding:4px 8px;border-bottom:1px solid var(--line);white-space:nowrap}td.num{text-align:right;font-variant-numeric:tabular-nums}
tr:hover td{background:#f4f7fb}td.repo{background:#e2f0d9;font-weight:600}td.no{color:var(--bad)}td.neg{color:#8a94a0}
td.low,tr:hover td.low{background:#ffc7ce;color:#9c0006}
tfoot td{position:sticky;bottom:0;background:#eef2f6;font-weight:600;border-top:2px solid #c9d1db;z-index:1}
td.key{background:#fffbea}
.muted{color:var(--muted);font-size:12px}
.count{margin-left:auto;font-size:12.5px;color:var(--muted)}
</style></head><body>
<header><h1>__TITLE__</h1><div class="sub">__SUBTITLE__</div></header>
__WARNINGS__
<div class="tabs"><div class="tab active" data-t="mc">Per model_color</div><div class="tab" data-t="sku">Detall per SKU</div><div class="tab" data-t="prev">Previsió demanda</div></div>
<div id="p-mc" class="panel active"></div>
<div id="p-sku" class="panel"></div>
<div id="p-prev" class="panel"></div>
<script>
const DATA = __DATA__;
const NUMFMT = new Intl.NumberFormat('ca-ES');
const STORE_KEY = 'repo-zld-cols-shared';
const WIDTH_KEY = 'repo-zld-widths';
const SEL_KEY = DATA.selKey || 'repo-zld-sel';
const VIEWS = {};
let HIDDEN = new Set();
let WIDTHS = {};
let SEL = new Set();   // model_color seleccionats per reposar (es desa al navegador amb la data de la repo)
function storeGet(k){ try { return localStorage.getItem(k); } catch(e) { return null; } }
function storeSet(k, v){ try { localStorage.setItem(k, v); return true; } catch(e) { return false; } }
try {
  const s = storeGet(STORE_KEY);
  if(s) HIDDEN = new Set(JSON.parse(s));
  else { ['repo-zld-cols-mc','repo-zld-cols-sku'].forEach(k => { const o = storeGet(k); if(o) JSON.parse(o).forEach(c => HIDDEN.add(c)); try { localStorage.removeItem(k); } catch(e) {} }); }
  const w = storeGet(WIDTH_KEY); if(w) WIDTHS = JSON.parse(w) || {};
  const sl = storeGet(SEL_KEY); if(sl) SEL = new Set(JSON.parse(sl));
} catch(e) {}
let STORE_OK = true;
function saveHidden(){ storeSet(STORE_KEY, JSON.stringify([...HIDDEN])); }
function saveWidths(){ storeSet(WIDTH_KEY, JSON.stringify(WIDTHS)); }
function saveSel(){ STORE_OK = storeSet(SEL_KEY, JSON.stringify([...SEL])); }
function setHidden(next){ HIDDEN = next; saveHidden(); Object.values(VIEWS).forEach(v => v.refresh()); }
function resetWidths(){ WIDTHS = {}; saveWidths(); Object.values(VIEWS).forEach(v => v.refresh()); }
function setSel(next){ SEL = next; saveSel(); Object.values(VIEWS).forEach(v => v.onSel()); }
function esc(v){ return String(v).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/"/g,'&quot;'); }
const MINW = 40, MAXW_AUTO = 360, SELW = 36;
const REPO_BY_MC = {}; DATA.mc.forEach(r => { REPO_BY_MC[r.model_color] = r.REPO || 0; });

// ---------- Escriptor XLSX sense dependències (zip "stored" + XML) ----------
const CRC_TABLE = (() => { const t = new Uint32Array(256); for(let n = 0; n < 256; n++){ let c = n; for(let k = 0; k < 8; k++) c = (c & 1) ? (0xEDB88320 ^ (c >>> 1)) : (c >>> 1); t[n] = c >>> 0; } return t; })();
function crc32(u8){ let c = 0xFFFFFFFF; for(let i = 0; i < u8.length; i++) c = CRC_TABLE[(c ^ u8[i]) & 0xFF] ^ (c >>> 8); return (c ^ 0xFFFFFFFF) >>> 0; }
function zipStore(files){
  const enc = new TextEncoder(); const parts = [], central = []; let offset = 0;
  const dosTime = 0, dosDate = (1 << 5) | 1;
  for(const f of files){
    const name = enc.encode(f.name), crc = crc32(f.data), size = f.data.length;
    const lh = new DataView(new ArrayBuffer(30));
    lh.setUint32(0, 0x04034b50, true); lh.setUint16(4, 20, true); lh.setUint16(6, 0x0800, true); lh.setUint16(8, 0, true);
    lh.setUint16(10, dosTime, true); lh.setUint16(12, dosDate, true); lh.setUint32(14, crc, true); lh.setUint32(18, size, true); lh.setUint32(22, size, true);
    lh.setUint16(26, name.length, true); lh.setUint16(28, 0, true);
    parts.push(new Uint8Array(lh.buffer), name, f.data);
    const ch = new DataView(new ArrayBuffer(46));
    ch.setUint32(0, 0x02014b50, true); ch.setUint16(4, 20, true); ch.setUint16(6, 20, true); ch.setUint16(8, 0x0800, true); ch.setUint16(10, 0, true);
    ch.setUint16(12, dosTime, true); ch.setUint16(14, dosDate, true); ch.setUint32(16, crc, true); ch.setUint32(20, size, true); ch.setUint32(24, size, true);
    ch.setUint16(28, name.length, true); ch.setUint16(30, 0, true); ch.setUint16(32, 0, true); ch.setUint16(34, 0, true); ch.setUint16(36, 0, true); ch.setUint32(38, 0, true); ch.setUint32(42, offset, true);
    central.push(new Uint8Array(ch.buffer), name);
    offset += 30 + name.length + size;
  }
  const cdSize = central.reduce((a, p) => a + p.length, 0);
  const eocd = new DataView(new ArrayBuffer(22));
  eocd.setUint32(0, 0x06054b50, true); eocd.setUint16(4, 0, true); eocd.setUint16(6, 0, true); eocd.setUint16(8, files.length, true); eocd.setUint16(10, files.length, true);
  eocd.setUint32(12, cdSize, true); eocd.setUint32(16, offset, true); eocd.setUint16(20, 0, true);
  return new Blob([...parts, ...central, new Uint8Array(eocd.buffer)], {type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'});
}
function xmlEsc(s){ return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;'); }
function colName(n){ let s = ''; n++; while(n > 0){ const m = (n - 1) % 26; s = String.fromCharCode(65 + m) + s; n = Math.floor((n - 1) / 26); } return s; }
function sheetXml(header, rows, widths){
  const cell = (v, r, c, style) => {
    if(v === null || v === undefined || v === '') return '';
    const ref = colName(c) + r, st = style ? ' s="' + style + '"' : '';
    if(typeof v === 'number' && isFinite(v)) return '<c r="' + ref + '"' + st + '><v>' + v + '</v></c>';
    return '<c r="' + ref + '"' + st + ' t="inlineStr"><is><t xml:space="preserve">' + xmlEsc(v) + '</t></is></c>';
  };
  let x = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">';
  x += '<sheetViews><sheetView workbookViewId="0"><pane ySplit="1" topLeftCell="A2" activePane="bottomLeft" state="frozen"/></sheetView></sheetViews>';
  x += '<cols>' + header.map((h, i) => '<col min="' + (i + 1) + '" max="' + (i + 1) + '" width="' + (widths[i] || 12) + '" customWidth="1"/>').join('') + '</cols><sheetData>';
  x += '<row r="1">' + header.map((h, i) => cell(h, 1, i, 1)).join('') + '</row>';
  rows.forEach((r, ri) => { x += '<row r="' + (ri + 2) + '">' + r.map((v, ci) => cell(v, ri + 2, ci, 0)).join('') + '</row>'; });
  x += '</sheetData><autoFilter ref="A1:' + colName(header.length - 1) + (rows.length + 1) + '"/></worksheet>';
  return x;
}
function buildXlsx(sheets){
  const enc = new TextEncoder(); const files = [];
  const X = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>';
  files.push({name: '[Content_Types].xml', data: enc.encode(X + '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/><Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/>' + sheets.map((s, i) => '<Override PartName="/xl/worksheets/sheet' + (i + 1) + '.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>').join('') + '</Types>')});
  files.push({name: '_rels/.rels', data: enc.encode(X + '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/></Relationships>')});
  files.push({name: 'xl/workbook.xml', data: enc.encode(X + '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><sheets>' + sheets.map((s, i) => '<sheet name="' + xmlEsc(s.name) + '" sheetId="' + (i + 1) + '" r:id="rId' + (i + 1) + '"/>').join('') + '</sheets></workbook>')});
  files.push({name: 'xl/_rels/workbook.xml.rels', data: enc.encode(X + '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">' + sheets.map((s, i) => '<Relationship Id="rId' + (i + 1) + '" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet' + (i + 1) + '.xml"/>').join('') + '<Relationship Id="rId' + (sheets.length + 1) + '" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/></Relationships>')});
  files.push({name: 'xl/styles.xml', data: enc.encode(X + '<styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><fonts count="2"><font><sz val="11"/><name val="Calibri"/></font><font><b/><sz val="11"/><color rgb="FFFFFFFF"/><name val="Calibri"/></font></fonts><fills count="3"><fill><patternFill patternType="none"/></fill><fill><patternFill patternType="gray125"/></fill><fill><patternFill patternType="solid"><fgColor rgb="FF1F3864"/></patternFill></fill></fills><borders count="1"><border><left/><right/><top/><bottom/><diagonal/></border></borders><cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/></cellStyleXfs><cellXfs count="2"><xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0"/><xf numFmtId="0" fontId="1" fillId="2" borderId="0" xfId="0" applyFont="1" applyFill="1"/></cellXfs><cellStyles count="1"><cellStyle name="Normal" xfId="0" builtinId="0"/></cellStyles></styleSheet>')});
  sheets.forEach((s, i) => files.push({name: 'xl/worksheets/sheet' + (i + 1) + '.xml', data: enc.encode(sheetXml(s.header, s.rows, s.widths || []))}));
  return zipStore(files);
}
function downloadBlob(blob, filename){
  const a = document.createElement('a'); a.href = URL.createObjectURL(blob); a.download = filename;
  document.body.appendChild(a); a.click(); setTimeout(() => { URL.revokeObjectURL(a.href); a.remove(); }, 1500);
}

// ---------- Gràfic per model_color: venda real (sòlid) + previsió (translúcid) per mes ----------
const MES_CURT = ['gen','feb','mar','abr','mai','jun','jul','ago','set','oct','nov','des'];
const MC_INFO = {}; DATA.mc.forEach(r => { MC_INFO[r.model_color] = r; });
function openChart(mc){
  const C = DATA.chart || {}; const info = MC_INFO[mc] || {}; const actual = (C.months && C.months[mc]) ? C.months[mc] : new Array(12).fill(0);
  const fc = C.forecast && C.forecast[mc]; const cover = C.coverEnd ? new Date(C.coverEnd) : null; const cm = cover ? cover.getMonth() + 1 : 0;
  const forecast = new Array(12).fill(0);
  if(fc && fc.curve){
    const tot = fc.curve.slice(8, 12).reduce((a,v)=>a+v, 0) || 1;
    for(let m = 9; m <= 12; m++){
      const f = fc.total * fc.curve[m-1] / tot;
      if(m < cm) continue;                                   // mes ja tancat: només real
      forecast[m-1] = (m === cm) ? Math.max(0, f - actual[m-1]) : f;   // mes en curs: la part que falta
    }
  }
  const totalsBar = actual.map((a,i) => a + forecast[i]);
  const maxV = Math.max(1, ...totalsBar);
  const W = 820, H = 380, L = 56, R = 18, T = 26, B = 46, cw = (W - L - R) / 12, bw = cw * 0.62;
  const step = niceStep(maxV / 4); const yMax = Math.ceil(maxV / step) * step; const y = v => T + (H - T - B) * (1 - v / yMax);
  let s = '<svg viewBox="0 0 '+W+' '+H+'" width="100%" height="auto" role="img" aria-label="Venda mensual '+esc(mc)+'">';
  s += '<defs><linearGradient id="gA" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#2c4a7c"/><stop offset="1" stop-color="#1f3864"/></linearGradient>'
     + '<pattern id="pF" width="6" height="6" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><rect width="6" height="6" fill="rgba(31,56,100,.16)"/><line x1="0" y1="0" x2="0" y2="6" stroke="rgba(31,56,100,.28)" stroke-width="2"/></pattern></defs>';
  for(let v = 0; v <= yMax + 1e-9; v += step){
    s += '<line x1="'+L+'" x2="'+(W-R)+'" y1="'+y(v)+'" y2="'+y(v)+'" stroke="#e6eaf0"/>';
    s += '<text x="'+(L-8)+'" y="'+(y(v)+4)+'" text-anchor="end" font-size="11" fill="#66717f">'+NUMFMT.format(v)+'</text>';
  }
  for(let i = 0; i < 12; i++){
    const x = L + i*cw + (cw - bw)/2; const a = actual[i], f = forecast[i]; const m = i + 1;
    const past = cover && (m < cm || (m === cm));
    if(a > 0){ s += '<rect x="'+x+'" y="'+y(a)+'" width="'+bw+'" height="'+(y(0)-y(a))+'" rx="3" fill="url(#gA)"><title>'+MESOS_CA[i]+': '+NUMFMT.format(a)+' parells venuts</title></rect>'; }
    if(f > 0){ s += '<rect x="'+x+'" y="'+y(a+f)+'" width="'+bw+'" height="'+(y(a)-y(a+f))+'" rx="3" fill="url(#pF)" stroke="#1f3864" stroke-opacity=".55" stroke-dasharray="4 3"><title>'+MESOS_CA[i]+': previsió '+NUMFMT.format(Math.round(f))+' parells'+(a>0?' (a més dels '+NUMFMT.format(a)+' ja venuts)':'')+'</title></rect>'; }
    if(a + f > 0){ s += '<text x="'+(x+bw/2)+'" y="'+(y(a+f)-6)+'" text-anchor="middle" font-size="11.5" font-weight="600" fill="'+(f>0?'#4a5c7a':'#1f3864')+'">'+NUMFMT.format(Math.round(a+f))+'</text>'; }
    s += '<text x="'+(x+bw/2)+'" y="'+(H-B+18)+'" text-anchor="middle" font-size="12" fill="'+(m===cm?'#1f3864':'#66717f')+'" font-weight="'+(m===cm?'700':'400')+'">'+MES_CURT[i]+'</text>';
    if(m === cm && cover){ s += '<text x="'+(x+bw/2)+'" y="'+(H-B+33)+'" text-anchor="middle" font-size="10" fill="#8a94a0">fins '+cover.getDate()+'/'+cm+'</text>'; }
  }
  s += '<line x1="'+L+'" x2="'+(W-R)+'" y1="'+y(0)+'" y2="'+y(0)+'" stroke="#c9d1db"/></svg>';
  const acum = actual.reduce((a,v)=>a+v,0), prevTot = Math.round(forecast.reduce((a,v)=>a+v,0));
  const chips = [['Venda '+(C.year||''), NUMFMT.format(acum)], ["Des de l'1/9", NUMFMT.format(info['ACUM HI']||0)], ['Previsió fins 31/12', fc ? NUMFMT.format(prevTot) : '—'],
                 ['Stock Zalando', NUMFMT.format((info['STOCK ZLD']||0) + (info['ENV PENDENTS']||0))], ['Corba', fc ? fc.src : 'sense previsió']];
  let html = '<div class="modal" id="chart-modal"><div class="card">'
    + '<div class="mhead"><div><div class="mtitle">'+esc(mc)+'</div><div class="msub">'+esc([info['GÈNERE'], info['COL·LECCIÓ'], info['SEASON'], info['TEMPORADA']].filter(Boolean).join(' · '))+'</div></div><button type="button" class="mclose" title="Tancar (Esc)">×</button></div>'
    + '<div class="chips">'+chips.map(c => '<div class="chip"><span>'+esc(c[0])+'</span><b>'+esc(c[1])+'</b></div>').join('')+'</div>'
    + s
    + '<div class="legend"><span class="lg solid"></span> venda real '+(C.year||'')+' <span class="lg fc"></span> previsió (corba de la col·lecció aplicada a la venda des de l’1 de setembre)'
    + (fc ? '' : ' · <i>aquest model no té previsió: no és d’hivern o no ha venut des de l’1 de setembre</i>')+'</div>';
  if(fc && fc.curve && cover){
    const pct = v => (v*100).toFixed(1).replace('.', ',') + ' %';
    const dim = new Date(cover.getFullYear(), cm, 0).getDate(); const day = cover.getDate();
    const tot = fc.curve.slice(8, 12).reduce((a,v)=>a+v, 0);
    let f = 0; for(let m = 9; m < cm; m++) f += fc.curve[m-1]; f += fc.curve[cm-1] * day / dim;
    const acumHI = info['ACUM HI'] || 0;
    const perMes = [9,10,11,12].map(m => { const tm = fc.total * fc.curve[m-1] / tot; return MES_CURT[m-1] + ' ' + NUMFMT.format(Math.round(tm)) + (m === cm ? ' ('+NUMFMT.format(actual[m-1])+' venuts + '+NUMFMT.format(Math.round(Math.max(0, tm - actual[m-1])))+' previstos)' : (m < cm ? ' (tancat)' : '')); });
    html += '<details class="calc"><summary>Com s’ha calculat</summary><ol>'
      + '<li>Corba <b>'+esc(fc.src)+'</b> (% de la venda 2025 de la col·lecció): set '+pct(fc.curve[8])+' · oct '+pct(fc.curve[9])+' · nov '+pct(fc.curve[10])+' · des '+pct(fc.curve[11])+' → de setembre a desembre <b>'+pct(tot)+'</b> de l’any.</li>'
      + '<li>Part de la corba ja transcorreguda des de l’1/9 fins al '+day+'/'+cm+': '+(cm > 9 ? 'mesos tancats + ' : '')+pct(fc.curve[cm-1])+' × '+day+'/'+dim+' = <b>'+pct(f)+'</b>.</li>'
      + '<li>Venda total prevista set–des = venda des de l’1/9 ÷ part transcorreguda × % set–des = '+NUMFMT.format(acumHI)+' ÷ '+pct(f)+' × '+pct(tot)+' = <b>'+NUMFMT.format(Math.round(fc.total))+'</b> parells.</li>'
      + '<li>Previsió fins al 31/12 = '+NUMFMT.format(Math.round(fc.total))+' − '+NUMFMT.format(acumHI)+' ja venuts = <b>'+NUMFMT.format(Math.max(0, Math.round(fc.total - acumHI)))+'</b> parells.</li>'
      + '<li>Repartiment per mes (total × % del mes ÷ % set–des): '+perMes.join(' · ')+'.</li>'
      + '</ol></details>';
  }
  html += '</div></div>';
  const old = document.getElementById('chart-modal'); if(old) old.remove();
  document.body.insertAdjacentHTML('beforeend', html);
  const modal = document.getElementById('chart-modal');
  const close = () => { modal.remove(); document.removeEventListener('keydown', onKey); };
  const onKey = e => { if(e.key === 'Escape') close(); };
  modal.addEventListener('click', e => { if(e.target === modal) close(); });
  modal.querySelector('.mclose').addEventListener('click', close);
  document.addEventListener('keydown', onKey);
}
function niceStep(raw){ const p = Math.pow(10, Math.floor(Math.log10(Math.max(raw, 1)))); const n = raw / p; return (n <= 1 ? 1 : n <= 2 ? 2 : n <= 5 ? 5 : 10) * p; }

function build(id, spec, rows){
  const panel = document.getElementById('p-'+id);
  if(spec.seasonPrefix) rows = rows.filter(r => String(r.SEASON || '').toUpperCase().startsWith(spec.seasonPrefix));
  const hasSel = !!spec.select;
  const selFilter = !!spec.selectFilter;
  const stickyLeft = hasSel ? SELW : 0;
  // selecció de columnes: compartida (HIDDEN) o pròpia de la vista (spec.ownCols, desada amb spec.colsKey)
  const own = !!spec.ownCols;
  let hiddenOwn = null;
  if(own){
    const s = storeGet(spec.colsKey);
    if(s){ try { hiddenOwn = new Set(JSON.parse(s)); } catch(e) { hiddenOwn = null; } }
    if(!hiddenOwn){ const vis = new Set(spec.defaultVisible || []); hiddenOwn = new Set(spec.cols.filter(c => !vis.has(c.k)).map(c => c.k)); }
  }
  const getHidden = () => own ? hiddenOwn : HIDDEN;
  function applyHidden(next){
    if(own){ hiddenOwn = next; storeSet(spec.colsKey, JSON.stringify([...next])); renderPicker(); renderHead(); render(); }
    else setHidden(next);
  }
  const state = {q:'', sortKey: spec.defaultSort, sortDir: -1, onlyRepo: spec.onlyRepoDefault, filters:{}};
  let suppressSort = false, lastOut = [], dirty = false;
  const facets = spec.facets.map(f => ({key:f, values:[...new Set(rows.map(r=>r[f]).filter(v=>v!==null && v!==''))].sort()}));
  let html = '<div class="kpis" id="k-'+id+'"></div><div class="bar">';
  html += '<input type="text" id="q-'+id+'" placeholder="Cerca (model, color, EAN, SKU...)">';
  facets.forEach(f => { html += '<select data-f="'+esc(f.key)+'"><option value="">'+esc(f.key)+': tots</option>'+f.values.map(v=>'<option>'+esc(v)+'</option>').join('')+'</select>'; });
  html += '<label><input type="checkbox" id="r-'+id+'" '+(state.onlyRepo?'checked':'')+'> només REPO &gt; 0</label>';
  html += '<div class="colwrap"><button type="button" class="btn" id="cb-'+id+'">Columnes ▾</button><div class="colpick" id="cp-'+id+'" hidden></div></div>';
  html += '<span class="selinfo" id="si-'+id+'"></span>';
  if(hasSel) html += '<button type="button" class="btn small" id="sc-'+id+'" title="Treu la marca de tots els model_color, també els que no es veuen pel filtre">Desmarcar tot</button>';
  if(selFilter) html += '<button type="button" class="btn primary" id="xl-'+id+'" title="Excel amb els SKU que es veuen (model_color marcats + filtres), un resum per model_color i la llista per a SAP">Generar excel REPO</button>';
  html += '<span class="count" id="c-'+id+'"></span></div>';
  html += '<div class="topscroll" id="ts-'+id+'"><div></div></div>';
  html += '<div class="wrap" id="w-'+id+'"><table id="t-'+id+'"><colgroup></colgroup><thead><tr></tr></thead><tbody></tbody><tfoot><tr></tr></tfoot></table></div>';
  panel.innerHTML = html;
  const wrap = panel.querySelector('.wrap'), table = panel.querySelector('table'), colgroup = panel.querySelector('colgroup');
  const thead = panel.querySelector('thead tr'), tbody = panel.querySelector('tbody'), tfoot = panel.querySelector('tfoot tr');
  const topscroll = panel.querySelector('.topscroll'), topinner = topscroll.firstElementChild;
  const colpick = panel.querySelector('.colpick'), colbtn = panel.querySelector('#cb-'+id);
  const selinfo = panel.querySelector('#si-'+id);
  function visCols(){ const H = getHidden(); const v = spec.cols.filter(c => !H.has(c.k)); return v.length ? v : [spec.cols[0]]; }
  function renderPicker(){
    const H = getHidden(); const vis = visCols().length;
    let h = '<div class="cp-actions"><button type="button" data-a="all">Totes</button><button type="button" data-a="none">Cap</button>';
    if(own) h += '<button type="button" data-a="default">Per defecte</button>';
    h += '<button type="button" data-a="widths">Amplades automàtiques</button>';
    h += '<span>'+vis+' de '+spec.cols.length+' columnes visibles · '+(own ? 'selecció pròpia d’aquesta secció' : 'la selecció i les amplades es comparteixen amb l’altra pestanya')+'</span></div><div class="cp-grid">';
    spec.cols.forEach(c => { h += '<label><input type="checkbox" data-c="'+esc(c.k)+'" '+(H.has(c.k)?'':'checked')+'> '+esc(c.l)+'</label>'; });
    colpick.innerHTML = h + '</div>';
    colpick.querySelectorAll('input').forEach(i => i.addEventListener('change', e => {
      const k = e.target.dataset.c; const next = new Set(getHidden());
      if(e.target.checked) next.delete(k); else next.add(k);
      if(!spec.cols.some(c => !next.has(c.k))){ e.target.checked = true; return; }
      applyHidden(next);
    }));
    colpick.querySelectorAll('button').forEach(b => b.addEventListener('click', () => {
      if(b.dataset.a === 'all') applyHidden(new Set());
      else if(b.dataset.a === 'widths') resetWidths();
      else if(b.dataset.a === 'default'){ const vis = new Set(spec.defaultVisible || []); applyHidden(new Set(spec.cols.filter(c => !vis.has(c.k)).map(c => c.k))); }
      else { const next = new Set(getHidden()); spec.cols.slice(1).forEach(c => next.add(c.k)); next.delete(spec.cols[0].k); applyHidden(next); }
    }));
  }
  function totalWidth(){ return visCols().reduce((a,c) => a + (WIDTHS[c.k] || 100), 0) + (hasSel ? SELW : 0); }
  function applyWidths(){
    const cols = visCols();
    if(cols.some(c => !WIDTHS[c.k])){
      table.style.tableLayout = 'auto'; table.style.width = 'max-content'; table.style.minWidth = '0';
      colgroup.innerHTML = '';
      const ths = [...thead.children].filter(t => !t.classList.contains('selcol'));
      cols.forEach((c,i) => {
        if(WIDTHS[c.k]) return;
        const th = ths[i]; const w = th && th.getBoundingClientRect ? th.getBoundingClientRect().width : 120;
        WIDTHS[c.k] = Math.max(MINW + 8, Math.min(MAXW_AUTO, Math.ceil(w || 120)));
      });
      saveWidths();
    }
    colgroup.innerHTML = (hasSel ? '<col style="width:'+SELW+'px">' : '') + cols.map(c => '<col style="width:'+WIDTHS[c.k]+'px">').join('');
    table.style.tableLayout = 'fixed'; table.style.minWidth = '0'; table.style.width = totalWidth() + 'px';
  }
  function renderHead(){
    const cols = visCols();
    let h = hasSel ? '<th class="selcol sticky" style="left:0" title="Marca o desmarca tots els model_color de la vista actual (respecta filtres i cerca)"><input type="checkbox" id="sa-'+id+'"></th>' : '';
    h += cols.map((c,i) => '<th class="'+(c.n?'num':'')+(c.hg?' hg-'+c.hg:'')+(i===0?' sticky':'')+'"'+(i===0?' style="left:'+stickyLeft+'px"':'')+' data-k="'+esc(c.k)+'" title="'+esc(c.h||c.l)+'">'+esc(c.l)+'<span class="arr"></span><span class="rs" title="Arrossega per canviar l’amplada · doble clic: ajustar"></span></th>').join('');
    thead.innerHTML = h;
    thead.querySelectorAll('th[data-k]').forEach(th => th.addEventListener('click', () => {
      if(suppressSort) return;
      const k = th.dataset.k;
      if(state.sortKey===k) state.sortDir*=-1; else { state.sortKey=k; state.sortDir = spec.cols.find(c=>c.k===k).n ? -1 : 1; }
      render();
    }));
    thead.querySelectorAll('th .rs').forEach((hnd,i) => {
      hnd.addEventListener('click', e => e.stopPropagation());
      hnd.addEventListener('dblclick', e => { e.stopPropagation(); const c = visCols()[i]; delete WIDTHS[c.k]; applyWidths(); fitHeight(); });
      hnd.addEventListener('mousedown', e => {
        e.preventDefault(); e.stopPropagation();
        const c = visCols()[i]; const startX = e.clientX; const startW = WIDTHS[c.k] || 100; const th = hnd.parentElement;
        th.classList.add('resizing');
        const off = hasSel ? 1 : 0;
        const move = ev => {
          WIDTHS[c.k] = Math.max(MINW, Math.round(startW + ev.clientX - startX));
          if(colgroup.children[i+off]) colgroup.children[i+off].style.width = WIDTHS[c.k] + 'px';
          table.style.width = totalWidth() + 'px';
        };
        const up = () => {
          document.removeEventListener('mousemove', move); document.removeEventListener('mouseup', up);
          th.classList.remove('resizing'); saveWidths(); fitHeight();
          suppressSort = true; setTimeout(() => { suppressSort = false; }, 0);
          Object.values(VIEWS).forEach(v => { if(v !== VIEWS[id]) v.syncWidths(); });
        };
        document.addEventListener('mousemove', move); document.addEventListener('mouseup', up);
      });
    });
    const sa = panel.querySelector('#sa-'+id);
    if(sa) sa.addEventListener('change', () => {
      const keys = lastOut.map(r => r.model_color); const next = new Set(SEL);
      const all = keys.length > 0 && keys.every(k => SEL.has(k));
      if(all) keys.forEach(k => next.delete(k)); else keys.forEach(k => next.add(k));
      setSel(next);
    });
  }
  function fitHeight(){
    const top = wrap.getBoundingClientRect().top;
    wrap.style.maxHeight = Math.max(240, window.innerHeight - top - 16) + 'px';
    topinner.style.width = table.scrollWidth + 'px';
  }
  function renderKpis(){
    const out = lastOut;
    const k = document.getElementById('k-'+id);
    const repoRows = out.filter(r=>r.REPO>0);
    const sum = key => out.reduce((a,r)=>a+(Number(r[key])||0),0);
    const selRows = hasSel ? rows.filter(r => SEL.has(r.model_color)) : [];
    const sumSel = key => selRows.reduce((a,r)=>a+(Number(r[key])||0),0);
    const small = (label, val) => '<small>'+esc(label)+': <b style="display:inline;font-size:13px">'+NUMFMT.format(val)+'</b></small>';
    k.innerHTML = spec.kpis.map(x => {
      const v = x.k==='__rows__' ? repoRows.length : sum(x.k);
      if(x.total !== undefined && x.total !== null) return '<div class="kpi"><b>'+NUMFMT.format(x.total)+'</b><span>'+esc(x.l)+'</span>'+small(x.sub||'llistat', v)+'</div>';
      if(x.selsub && hasSel){ const vs = x.k==='__rows__' ? selRows.length : sumSel(x.k); return '<div class="kpi"><b>'+NUMFMT.format(v)+'</b><span>'+esc(x.l)+'</span>'+small('seleccionats', vs)+'</div>'; }
      return '<div class="kpi"><b>'+NUMFMT.format(v)+'</b><span>'+esc(x.l)+'</span></div>';
    }).join('');
  }
  function updateSelUI(){
    const sa = panel.querySelector('#sa-'+id);
    if(sa){
      const keys = lastOut.map(r => r.model_color); const n = keys.filter(k => SEL.has(k)).length;
      sa.checked = keys.length > 0 && n === keys.length; sa.indeterminate = n > 0 && n < keys.length;
    }
    const pares = [...SEL].reduce((a,k) => a + (REPO_BY_MC[k] || 0), 0);
    const warn = STORE_OK ? '' : ' · ⚠ el navegador no deixa desar la selecció';
    if(hasSel) selinfo.textContent = (SEL.size ? SEL.size + ' model_color marcats · ' + NUMFMT.format(pares) + ' parells REPO' : 'Cap model_color marcat') + warn;
    else selinfo.textContent = SEL.size ? 'SKU dels ' + SEL.size + ' model_color marcats' : '';
  }
  function exportXlsx(){
    const cols = visCols(); const out = lastOut;
    if(!out.length){ alert('No hi ha cap SKU per exportar: marca model_color a la pestanya «Per model_color».'); return; }
    const sheet1 = { name: 'REPO SKU', header: cols.map(c => c.l), rows: out.map(r => cols.map(c => (r[c.k] === null || r[c.k] === undefined) ? '' : r[c.k])),
                     widths: cols.map(c => Math.min(45, Math.max(8, Math.round((WIDTHS[c.k] || 100) / 7)))) };
    const mcSel = DATA.mc.filter(r => SEL.has(r.model_color)).map(r => [r.model_color, r['GÈNERE'], r['VENDA SET'], r.NIVELL, r.HAURIA, r['STOCK ZLD'], r['ENV PENDENTS'], r.REPO, r.PREPARABLE, r.DTE || '']);
    const sheet2 = { name: 'MODEL_COLOR', header: ['model_color','GÈNERE','VENDA SET','NIVELL','HAURIA','STOCK ZLD','ENV PENDENTS','REPO','PREPARABLE','DTE %'], rows: mcSel, widths: [24,10,10,8,9,10,13,8,12,7] };
    const sap = out.filter(r => r.REPO > 0).map(r => [r.EAN, r.SKU, r.model_color, r.talla, r.REPO, r.PREPARABLE]);
    const sheet3 = { name: 'SAP', header: ['EAN','SKU','model_color','talla','REPO','PREPARABLE'], rows: sap, widths: [16,26,24,8,8,12] };
    downloadBlob(buildXlsx([sheet1, sheet2, sheet3]), 'REPO ZALANDO ' + (DATA.dateLabel || '') + ' - seleccio.xlsx');
  }
  function render(){
    const cols = visCols();
    const q = state.q.toLowerCase();
    let out = rows.filter(r => {
      if(selFilter && !SEL.has(r.model_color)) return false;
      if(state.onlyRepo && !(r.REPO > 0)) return false;
      for(const k in state.filters){ if(state.filters[k] && String(r[k]) !== state.filters[k]) return false; }
      if(!q) return true;
      return spec.search.some(k => r[k] !== null && String(r[k]).toLowerCase().includes(q));
    });
    const sk = state.sortKey, sd = state.sortDir;
    out.sort((a,b) => { const x=a[sk], y=b[sk]; if(x===y) return 0; if(x===null||x===undefined) return 1; if(y===null||y===undefined) return -1; return (x>y?1:-1)*sd; });
    lastOut = out;
    thead.querySelectorAll('th[data-k]').forEach(th => { const a = th.querySelector('.arr'); if(a) a.textContent = th.dataset.k===sk ? (sd>0?'▲':'▼') : ''; });
    const MAX = 6000; const shown = out.slice(0, MAX);
    let h = '';
    if(selFilter && SEL.size === 0){
      h = '<tr><td class="empty" colspan="'+cols.length+'">Cap model_color marcat. Marca’ls amb les caselles de la pestanya «Per model_color» i aquí apareixeran les seves talles.</td></tr>';
    }
    for(const r of shown){
      const selected = SEL.has(r.model_color);
      h += '<tr'+(hasSel && selected ? ' class="sel"' : '')+'>';
      if(hasSel) h += '<td class="selcol sticky" style="left:0"><input type="checkbox" data-mc="'+esc(r.model_color)+'"'+(selected?' checked':'')+'></td>';
      cols.forEach((c,i) => {
        let v = r[c.k]; let cls = c.n ? 'num' : '';
        if(c.k === 'REPO' && v > 0) cls += ' repo';
        if(c.k === 'CREAT A ZLD?' && v === 'NO CONSTA') cls += ' no';
        if(c.k === 'DIF' && v < 0) cls += ' neg';
        if(c.key) cls += ' key';
        if(spec.red[c.k] !== undefined && typeof v === 'number' && v < spec.red[c.k]) cls += ' low';
        if(i===0) cls += ' sticky';
        if(c.k === 'model_color') cls += ' mclink';
        if(v === null || v === undefined) v = '';
        else if(c.fmt === 'pct') v = (typeof v === 'number' && v > 0) ? NUMFMT.format(v) + '%' : '';
        else if(c.n && typeof v === 'number') v = Number.isInteger(v) ? NUMFMT.format(v) : v.toFixed(1);
        h += '<td class="'+cls+'"'+(i===0?' style="left:'+stickyLeft+'px"':'')+' title="'+esc(v)+'">'+esc(v)+'</td>';
      });
      h += '</tr>';
    }
    tbody.innerHTML = h;
    let f = hasSel ? '<td class="selcol sticky" style="left:0"></td>' : '';
    cols.forEach((c,i) => {
      const st = i===0 ? ' sticky' : ''; const stl = i===0 ? ' style="left:'+stickyLeft+'px"' : '';
      if(c.sum){ const s = out.reduce((a,r)=>a+(Number(r[c.k])||0),0); f += '<td class="num'+st+'"'+stl+'>'+NUMFMT.format(s)+'</td>'; }
      else f += '<td class="'+st.trim()+'"'+stl+'>'+(i===0 ? 'TOTAL ('+NUMFMT.format(out.length)+' files)' : '')+'</td>';
    });
    tfoot.innerHTML = f;
    document.getElementById('c-'+id).textContent = out.length + ' files' + (out.length>MAX ? ' (es mostren '+MAX+')' : '');
    renderKpis();
    updateSelUI();
    applyWidths();
    fitHeight();
    dirty = false;
  }
  if(hasSel){
    tbody.addEventListener('change', e => {
      const cb = e.target; if(!cb.matches || !cb.matches('input[data-mc]')) return;
      const next = new Set(SEL); if(cb.checked) next.add(cb.dataset.mc); else next.delete(cb.dataset.mc);
      SEL = next; saveSel();
      cb.closest('tr').classList.toggle('sel', cb.checked);
      updateSelUI(); renderKpis();
      Object.values(VIEWS).forEach(v => { if(v !== VIEWS[id]) v.onSel(); });
    });
    panel.querySelector('#sc-'+id).addEventListener('click', () => setSel(new Set()));
  }
  if(selFilter) panel.querySelector('#xl-'+id).addEventListener('click', exportXlsx);
  tbody.addEventListener('click', e => { const td = e.target.closest ? e.target.closest('td.mclink') : null; if(td) openChart(td.textContent.trim()); });
  panel.querySelector('#q-'+id).addEventListener('input', e => { state.q = e.target.value; render(); });
  panel.querySelector('#r-'+id).addEventListener('change', e => { state.onlyRepo = e.target.checked; render(); });
  panel.querySelectorAll('select').forEach(s => s.addEventListener('change', e => { state.filters[e.target.dataset.f] = e.target.value; render(); }));
  colbtn.addEventListener('click', e => { e.stopPropagation(); colpick.hidden = !colpick.hidden; });
  colpick.addEventListener('click', e => e.stopPropagation());
  document.addEventListener('click', () => { colpick.hidden = true; });
  let syncing = false;
  topscroll.addEventListener('scroll', () => { if(syncing) return; syncing = true; wrap.scrollLeft = topscroll.scrollLeft; syncing = false; });
  wrap.addEventListener('scroll', () => { if(syncing) return; syncing = true; topscroll.scrollLeft = wrap.scrollLeft; syncing = false; });
  window.addEventListener('resize', fitHeight);
  renderPicker(); renderHead(); render();
  return {
    fit: fitHeight,
    refresh(){ renderPicker(); renderHead(); render(); },
    syncWidths(){ applyWidths(); fitHeight(); },
    onSel(){ if(panel.classList.contains('active')) render(); else dirty = true; },
    show(){ if(dirty) render(); else { applyWidths(); fitHeight(); } },
    exportXlsx, buildForTest(){ return { cols: visCols(), out: lastOut }; }
  };
}
// columnes noves que han d'aparèixer ocultes la primera vegada a les vistes compartides (després mana l'usuari)
const KNOWN_KEY = 'repo-zld-known-cols';
let KNOWN = new Set(); try { KNOWN = new Set(JSON.parse(storeGet(KNOWN_KEY) || '[]')); } catch(e) {}
function applyDefaultHidden(spec){
  let changed = false;
  (spec.defaultHidden || []).forEach(k => { if(!KNOWN.has(k)){ HIDDEN.add(k); KNOWN.add(k); changed = true; } });
  if(changed){ storeSet(KNOWN_KEY, JSON.stringify([...KNOWN])); saveHidden(); }
}
applyDefaultHidden(DATA.mcSpec); applyDefaultHidden(DATA.skuSpec);
VIEWS.mc = build('mc', DATA.mcSpec, DATA.mc);
VIEWS.sku = build('sku', DATA.skuSpec, DATA.sku);

// ---------- Pestanya Previsió demanda: % mensual de venda per col·lecció (blocs DONA / HOME / NEN desplegables) ----------
const MESOS_CA = ['gener','febrer','març','abril','maig','juny','juliol','agost','setembre','octubre','novembre','desembre'];
function prevCells(pct){
  if(!pct) return '<td class="num" colspan="13"><i>sense dades</i></td>';
  const s = pct.reduce((a,v)=>a+v,0);
  return pct.map(v => '<td class="num heat" style="background:rgba(31,56,100,'+Math.min(0.6, v*2.4).toFixed(2)+')'+(v >= 0.17 ? ';color:#fff' : '')+'">'+(v*100).toFixed(1)+'%</td>').join('')
       + '<td class="num"><b>'+Math.round(s*100)+'%</b></td>';
}
function prevTable(P, blocks, sec, temp){
  if(!blocks || !blocks.length) return '<p class="muted">No hi ha el full «'+esc(temp)+'» al fitxer «Càlcul venda per col·leccio». Executa previsio_colleccions.py --temporada '+esc(temp)+'.</p>';
  const W = {col: 230, mes: 84, total: 72, unit: 110};
  const totalW = W.col + 12 * W.mes + W.total + W.unit;
  let h = '<p class="muted" style="margin:4px 0 10px">Distribució mensual de la venda '+P.any+' per col·lecció dels models '+esc(temp)+' (mes de la data de comanda). Clica un gènere per desplegar-ne les col·leccions. Les files en cursiva usen la corba genèrica del gènere perquè tenen poques dades o cap venda '+P.any+'; passa el ratolí per veure el motiu.</p>';
  h += '<div class="wrap prevwrap"><table class="prev" style="table-layout:fixed;width:'+totalW+'px;min-width:0"><colgroup><col style="width:'+W.col+'px">'
     + MESOS_CA.map(() => '<col style="width:'+W.mes+'px">').join('')
     + '<col style="width:'+W.total+'px"><col style="width:'+W.unit+'px"></colgroup>'
     + '<thead><tr><th class="sticky" style="left:0">Col·lecció</th>'
     + MESOS_CA.map(m => '<th class="num">'+m+'</th>').join('')
     + '<th class="num">Total</th><th class="num">Unitats '+P.any+'</th></tr></thead><tbody>';
  blocks.forEach((b, bi) => {
    const tot = b.rows.find(r => r.total) || {pct:null, unitats:0};
    const n = b.rows.filter(r => !r.total).length; const key = sec + bi;
    h += '<tr class="gen" data-b="'+key+'" title="Clica per desplegar o plegar"><td class="sticky" style="left:0"><span class="tri">▸</span><b>'+esc(b.genere)+'</b> <small>'+n+' col·leccions</small></td>'
       + prevCells(tot.pct) + '<td class="num"><b>'+NUMFMT.format(tot.unitats)+'</b></td></tr>';
    b.rows.filter(r => !r.total).forEach(r => {
      h += '<tr class="col b'+key+'" hidden'+(r.nota ? ' title="'+esc(r.nota)+'"' : '')+'><td class="sticky'+(r.nota ? ' generic' : '')+'" style="left:0">'+esc(r.colleccio)+(r.nota ? ' <small>genèrica</small>' : '')+'</td>'
         + prevCells(r.pct) + '<td class="num">'+NUMFMT.format(r.unitats)+'</td></tr>';
    });
  });
  return h + '</tbody></table></div>';
}
function buildPrev(){
  const panel = document.getElementById('p-prev'); const P = DATA.prev || {seasons: {}};
  const seasons = P.seasons || {};
  const hiKey = Object.keys(seasons).find(k => k.startsWith('HI')) || 'HI26';
  const esKey = Object.keys(seasons).find(k => k.startsWith('ES')) || 'ES26';
  let h = '<div class="prevsec"><h2>HIVERN</h2>' + prevTable(P, seasons[hiKey], 'h', hiKey)
        + '<div class="subpanel"><h3>Model_color d’hivern, ordenats per la venda de la setmana</h3><div id="p-pmc"></div></div></div>';
  h += '<div class="prevsec"><h2>ESTIU</h2>' + prevTable(P, seasons[esKey], 'e', esKey)
     + '<div class="subpanel"><h3>Model_color d’estiu, ordenats per la venda de la setmana</h3><div id="p-pmce"></div></div></div>';
  if(P.fitxer) h += '<p class="muted" style="margin-top:10px">Font de les corbes: '+esc(P.fitxer)+'.</p>';
  panel.innerHTML = h;
  panel.querySelectorAll('tr.gen').forEach(tr => tr.addEventListener('click', () => {
    const open = tr.classList.toggle('open');
    panel.querySelectorAll('tr.b'+tr.dataset.b).forEach(x => { x.hidden = !open; });
    tr.querySelector('.tri').textContent = open ? '▾' : '▸';
  }));
}
buildPrev();
const NOVIEW = { fit(){}, refresh(){}, syncWidths(){}, onSel(){}, show(){} };
VIEWS.pmc = (DATA.pmcSpec && document.getElementById('p-pmc')) ? build('pmc', DATA.pmcSpec, DATA.mc) : NOVIEW;
VIEWS.pmce = (DATA.pmceSpec && document.getElementById('p-pmce')) ? build('pmce', DATA.pmceSpec, DATA.mc) : NOVIEW;
VIEWS.prev = { fit(){ VIEWS.pmc.fit(); VIEWS.pmce.fit(); }, refresh(){}, syncWidths(){ VIEWS.pmc.syncWidths(); VIEWS.pmce.syncWidths(); }, onSel(){},
               show(){ VIEWS.pmc.show(); VIEWS.pmce.show(); } };
document.querySelectorAll('.tab').forEach(t => t.addEventListener('click', () => {
  document.querySelectorAll('.tab').forEach(x=>x.classList.toggle('active', x===t));
  document.querySelectorAll('.panel').forEach(p=>p.classList.toggle('active', p.id==='p-'+t.dataset.t));
  VIEWS[t.dataset.t].show();
}));
window.addEventListener('pageshow', () => { const sl = storeGet(SEL_KEY); if(sl){ try { const s = new Set(JSON.parse(sl)); if(s.size !== SEL.size) setSel(s); } catch(e) {} } });
</script></body></html>
"""


def write_html(sku: pd.DataFrame, mc: pd.DataFrame, title: str, subtitle: str, warnings: list[str], path: str, totals: dict | None = None,
               sel_key: str = "", prev: dict | None = None, mc_prev: pd.DataFrame | None = None, chart: dict | None = None):
    totals = totals or {}
    if mc_prev is None:
        mc_prev = mc
    sku = sku.drop(columns=[c for c in HTML_HIDE if c in sku.columns])
    mc = mc.drop(columns=[c for c in HTML_HIDE if c in mc.columns])

    def recs(df):
        out, cols = [], list(df.columns)
        for row in df.itertuples(index=False, name=None):
            rec = {}
            for k, v in zip(cols, row):
                if v is None or v is pd.NA or (isinstance(v, float) and np.isnan(v)):
                    rec[k] = None
                elif isinstance(v, np.integer):
                    rec[k] = int(v)
                elif isinstance(v, np.floating):
                    rec[k] = float(v)
                else:
                    rec[k] = v
            out.append(rec)
        return out
    num_sku = {c for c in sku.columns if pd.api.types.is_numeric_dtype(sku[c])}
    num_mc = {c for c in mc.columns if pd.api.types.is_numeric_dtype(mc[c])}
    sum_cols = {"HAURIA", "STOCK ZLD", "OFFERABLE", "ENV PENDENTS", "DIF", "REPO", "PREPARABLE", "FALTA STOCK TP", "STOCK TP 01 02",
                "DISPO 30 DIES", "DISPO 59 DIES", "VENDA SET", "VENDA SKU 1 SETM", "ACUM'25", "ACUM'26", "VENDA 4 SETM"}
    key_cols = {"HAURIA", "DIF", "REPO", "PREPARABLE"}
    def spec(df, nums, default_sort, only_repo, facets, search, kpis, sum_ok, header_groups=(), red=None, cols=None, extra=None):
        names = list(cols or df.columns)
        hg = {}
        for start, end, cls in header_groups:
            if start in names and end in names:
                for k in range(names.index(start), names.index(end) + 1):
                    hg[names[k]] = cls
        out = {"cols": [{"k": c, "l": c, "n": c in nums, "sum": c in sum_ok, "key": c in key_cols, "hg": hg.get(c, ""), "h": col_help(c),
                         "fmt": "pct" if c == "DTE" else ""} for c in names],
               "defaultSort": default_sort, "onlyRepoDefault": only_repo, "facets": facets, "search": search, "kpis": kpis, "red": red or {},
               "select": df is mc, "selectFilter": df is sku}
        out.update(extra or {})
        return out
    mc_sums = sum_cols - {"VENDA SET", "VENDA 4 SETM"} | {"VENDA SET"}
    num_prev = {c for c in mc_prev.columns if pd.api.types.is_numeric_dtype(mc_prev[c])}
    prev_default = ["model_color", "SEASON", "TEMPORADA", "COL·LECCIÓ", "VENDA SET", "ACUM'25", "ACUM'26", "ACUM HI", "STOCK ZLD", "OFFERABLE",
                    "ENV PENDENTS", "COBERTURA SET", "STOCK TP 01 02", "DISPO 30 DIES", "DISPONIBLE ALMACÉN", "PREVISIÓ", "A COMPRAR"]
    orange_cols = ("DTE", "DTE", "orange"), ("PREVISIÓ", "A COMPRAR", "orange")
    data = {
        "selKey": f"repo-zld-sel-{sel_key}" if sel_key else "repo-zld-sel",
        "dateLabel": sel_key,
        "prev": prev,
        "chart": chart or {},
        "pmcSpec": spec(mc_prev, num_prev, "VENDA SET", False, ["GÈNERE", "SEASON", "TEMPORADA", "COL·LECCIÓ", "CREAT A ZLD?", "CREAT HI26"],
                        ["model_color", "model", "color", "COL·LECCIÓ", "AVÍS"], [], mc_sums | {"DISPONIBLE ALMACÉN", "ACUM HI", "PREVISIÓ", "A COMPRAR"},
                        (("model_color", "CREAT HI26", "grey"), ("VENDA SET", "OBJECTIU", "yellow"), ("DIF", mc_prev.columns[-1], "green")) + orange_cols,
                        red=RED_RULES_MC, cols=list(mc_prev.columns),
                        extra={"ownCols": True, "colsKey": "repo-zld-cols-prev", "defaultVisible": prev_default, "select": False, "selectFilter": False,
                               "seasonPrefix": "HI"}),
        "pmceSpec": spec(mc_prev, num_prev, "VENDA SET", False, ["GÈNERE", "SEASON", "TEMPORADA", "COL·LECCIÓ", "CREAT A ZLD?", "CREAT HI26"],
                         ["model_color", "model", "color", "COL·LECCIÓ", "AVÍS"], [], mc_sums | {"DISPONIBLE ALMACÉN", "ACUM HI", "PREVISIÓ", "A COMPRAR"},
                         (("model_color", "CREAT HI26", "grey"), ("VENDA SET", "OBJECTIU", "yellow"), ("DIF", mc_prev.columns[-1], "green")) + orange_cols,
                         red=RED_RULES_MC, cols=list(mc_prev.columns),
                         extra={"ownCols": True, "colsKey": "repo-zld-cols-prev-es", "defaultVisible": prev_default, "select": False, "selectFilter": False,
                                "seasonPrefix": "ES"}),
        "mc": recs(mc_prev), "sku": recs(sku),
        "mcSpec": spec(mc, num_mc, "VENDA SET", False, ["GÈNERE", "SEASON", "TEMPORADA", "COL·LECCIÓ", "CREAT A ZLD?", "CREAT HI26"], ["model_color", "model", "color", "COL·LECCIÓ", "AVÍS"],
                       [{"k": "__rows__", "l": "model_color amb REPO", "selsub": True}, {"k": "REPO", "l": "parells REPO", "selsub": True},
                        {"k": "PREPARABLE", "l": "preparables (stock 30d)", "selsub": True},
                        {"k": "VENDA SET", "l": "venda setmana (tot Zalando)", "total": totals.get("venda_setm"), "sub": "del llistat"},
                        {"k": "STOCK ZLD", "l": "stock Zalando (tot)", "total": totals.get("stock_zld"), "sub": "del llistat"},
                        {"k": "ENV PENDENTS", "l": "env. pendents"}], mc_sums,
                       (("model_color", "CREAT HI26", "grey"), ("VENDA SET", "OBJECTIU", "yellow"), ("DIF", mc.columns[-1], "green")) + orange_cols, red=RED_RULES_MC,
                       extra={"defaultHidden": ["ACUM HI", "PREVISIÓ", "A COMPRAR"]}),
        "skuSpec": spec(sku, num_sku, "VENDA SET", True, ["GÈNERE", "SEASON", "TEMPORADA", "CREAT A ZLD?", "CREAT HI26"], ["EAN", "SKU", "model_color", "model", "color", "talla", "AVÍS"],
                        [{"k": "__rows__", "l": "SKUs amb REPO"}, {"k": "REPO", "l": "parells REPO"}, {"k": "PREPARABLE", "l": "preparables (stock 30d)"},
                         {"k": "STOCK ZLD", "l": "stock Zalando (tot)", "total": totals.get("stock_zld"), "sub": "del llistat"}], sum_cols - {"VENDA SET", "VENDA 4 SETM", "ACUM'25", "ACUM'26"},
                        (("EAN", "CREAT HI26", "grey"), ("VENDA SET", "OBJECTIU", "yellow"), ("DIF", sku.columns[-1], "green"), ("DTE", "DTE", "orange")),
                        extra={"defaultHidden": ["ACUM HI"]}),
    }
    warn_html = "".join(f'<div class="warn">{html.escape(w)}</div>' for w in warnings)
    page = (HTML_TEMPLATE.replace("__TITLE__", html.escape(title)).replace("__SUBTITLE__", html.escape(subtitle))
            .replace("__WARNINGS__", warn_html).replace("__DATA__", json.dumps(data, ensure_ascii=False).replace("</", "<\\/")))
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(page)


# --------------------------------------------------------------------------------------
def main():
    here = os.path.dirname(os.path.abspath(__file__))
    ap = argparse.ArgumentParser(description="Càlcul de reposició Zalando")
    ap.add_argument("--data", default=here, help="carpeta amb les fonts")
    ap.add_argument("--out", default=None, help="carpeta on es crea REPO/ amb les sortides (per defecte la de dades)")
    ap.add_argument("--mult", type=float, default=None, help="multiplicador de la venda setmanal; si no es dona, el del mes a VENTA POR MES.xlsx (o 3)")
    ap.add_argument("--min-level", type=int, default=6, help="nivell mínim per dona i home encara que no hi hagi venda (6; 0 = cap)")
    ap.add_argument("--min-level-kids", type=int, default=2, help="nivell mínim per nens (2; 0 = cap)")
    ap.add_argument("--max-level", type=int, default=None, help="nivell màxim (cap = sense límit)")
    ap.add_argument("--date", default=dt.date.today().strftime("%d.%m"), help="etiqueta de data pels fitxers de sortida (dd.mm)")
    ap.add_argument("--snapshot", action="append", default=[], help="fitxer(s) de snapshot addicional(s) a considerar")
    args = ap.parse_args()
    data, out = args.data, args.out or args.data
    os.makedirs(out, exist_ok=True)
    cache_dir = CACHE_DIR

    print("Llegint fonts...")
    models = load_models(readable_copy(os.path.join(data, "Models a reposar.xlsx")))
    levels = load_levels(readable_copy(os.path.join(data, "NIVEL.xlsx")))
    lines, sources = load_sales(data, cache_dir)
    venda25 = next((p for p in [os.path.join(data, "Vendes", "2025", "Venda 2025.xlsx"), os.path.join(data, "Venda 2025.xlsx")]
                    if os.path.exists(p)), None)
    if venda25 is None:
        raise SystemExit("No trobo 'Vendes/2025/Venda 2025.xlsx'")
    acum25 = load_sales_2025(readable_copy(venda25))
    stock_tp, tp_file = load_stock_tp(os.path.join(data, "Stock Toni Pons"))
    snap, snap_meta = load_snapshot(os.path.join(data, "Stock Zalando"), args.snapshot)
    pending, pend_labels = load_pending(os.path.join(data, "Enviaments pendents"))
    adjust = load_adjustments(os.path.join(data, "Ajustos repo.xlsx"))
    creats_path = os.path.join(data, "Creats Zalando HI26.xlsx")
    created = load_created_hi26(readable_copy(creats_path)) if os.path.exists(creats_path) else set()
    if not os.path.exists(creats_path):
        print("AVÍS: no trobo 'Creats Zalando HI26.xlsx'; la columna CREAT HI26 quedarà buida")
    zinfo, zinfo_meta = load_zalando_info(os.path.join(data, "Informació models zalando"))
    if not zinfo_meta:
        print("AVÍS: cap CSV a 'Informació models zalando'; la columna DTE quedarà a 0")
    prev = load_previsio(os.path.join(data, "Previsió demanda"))
    if prev is None:
        print("AVÍS: no trobo 'Previsió demanda/Càlcul venda per col·leccio <any>.xlsx'; la pestanya Previsió demanda sortirà buida")
    almacen, almacen_meta = load_almacen(os.path.join(data, "Previsió demanda"))
    if not almacen_meta:
        print("AVÍS: no trobo 'Previsió demanda/almacen_taula.xlsx'; DISPONIBLE ALMACÉN quedarà a 0")

    # multiplicador: línia d'ordres > VENTA POR MES.xlsx (mes de la data de càlcul) > 3
    mult, mult_src = args.mult, "línia d'ordres"
    month = int(args.date.split(".")[1]) if re.fullmatch(r"\d{1,2}\.\d{1,2}", args.date) else dt.date.today().month
    vpm = os.path.join(data, "VENTA POR MES.xlsx")
    if mult is None and os.path.exists(vpm):
        table = load_month_mult(readable_copy(vpm))
        if month in table:
            mult, mult_src = table[month], f"VENTA POR MES.xlsx, {MONTH_NAMES_CA[month]}"
        else:
            print("AVÍS: VENTA POR MES.xlsx no té el mes", month)
    if mult is None:
        mult, mult_src = 3.0, "per defecte"

    # inici de la temporada d'hivern: 1 de setembre (de l'any de càlcul si ja hi som, si no de l'any anterior)
    calc_year = dt.date.today().year
    hi_start = dt.date(calc_year if month >= 9 else calc_year - 1, 9, 1)

    print("Calculant...")
    sku, mc, fora, info = compute(models, levels, lines, acum25, stock_tp, snap, pending, pend_labels, adjust,
                                  mult, args.min_level, args.min_level_kids, args.max_level, created=created, zinfo=zinfo,
                                  hi_start=hi_start)

    # model_color per a la secció de Previsió demanda: les mateixes columnes + DISPONIBLE ALMACÉN (només HTML)
    disp_mc = sku[["SKU", "model_color"]].merge(almacen, on="SKU", how="left").fillna({"DISPONIBLE ALMACÉN": 0}) \
        .groupby("model_color")["DISPONIBLE ALMACÉN"].sum()
    mc_prev = mc.copy()
    mc_prev.insert(list(mc_prev.columns).index("DISPO 30 DIES") + 1, "DISPONIBLE ALMACÉN",
                   mc_prev["model_color"].map(disp_mc).fillna(0).astype(int))
    # PREVISIÓ fins al 31/12 i A COMPRAR (net del stock que ja tenim), a les dues taules de model_color
    cover_end = dt.date.fromisoformat(info["setmana_fi"])
    previsio, prev_avisos, prev_detail = previsio_fins_desembre(mc_prev, prev, hi_start, cover_end)
    a_comprar = (previsio - mc_prev["STOCK ZLD"] - mc_prev["ENV PENDENTS"] - mc_prev["DISPONIBLE ALMACÉN"]).clip(lower=0)
    for frame in (mc, mc_prev):
        pos = list(frame.columns).index("AVÍS")
        frame.insert(pos, "PREVISIÓ", pd.array(previsio.round(), dtype="Int64"))
        frame.insert(pos + 1, "A COMPRAR", pd.array(a_comprar.round(), dtype="Int64"))
    for av in prev_avisos:
        print("AVÍS:", av)

    warnings = []
    if snap_meta["rebutjats"]:
        warnings.append("Snapshots de stock Zalando rebutjats per EANs no íntegres (notació científica 8,43453E+12 en desar des d'Excel): "
                        + ", ".join(snap_meta["rebutjats"]) + ". Cal desar el CSV original de Zalando sense obrir-lo amb Excel.")
    snap_date = dt.date.fromisoformat(snap_meta["data"])
    if (dt.date.today() - snap_date).days > 3:
        warnings.append(f"El snapshot de stock Zalando utilitzat és del {snap_date.strftime('%d.%m.%Y')} ({(dt.date.today()-snap_date).days} dies).")
    no_created = int((mc["CREAT A ZLD?"] == "NO CONSTA").sum())
    unmatched_env = int(pending.loc[~pending["EAN"].isin(set(models["EAN"].dropna())), "ENV PENDENTS"].sum()) if len(pending) else 0
    if unmatched_env:
        warnings.append(f"{unmatched_env} parells dels enviaments pendents tenen EANs que no són a 'Models a reposar' (no es resten enlloc).")
    if len(adjust):
        warnings.append(f"S'han aplicat {len(adjust)} ajustos de 'Ajustos repo.xlsx' (multiplicador / nivell forçat).")

    week_lbl = f"{info['setmana_inici'][8:10]}.{info['setmana_inici'][5:7]} - {info['setmana_fi'][8:10]}.{info['setmana_fi'][5:7]}"
    params = [
        ("Data càlcul", dt.date.today().isoformat()),
        ("Setmana de venda utilitzada", f"{week_lbl} ({info['setmanes']} setmanes acumulades el 2026)"),
        ("Multiplicador", f"{mult:g} ({mult_src})"),
        ("Regla", f"objectiu = venda setmanal del model_color x {mult:g}; nivell = primer nivell de la taula del gènere amb què la suma de les talles del model (HAURIA) cobreix l'objectiu, o sigui HAURIA >= objectiu; HAURIA = desglossament per talla d'aquest nivell"),
        ("Nivell mínim adults / nens", f"{args.min_level} / {args.min_level_kids} (0 = sense venda no es reposa)"),
        ("Nivell màxim", str(args.max_level) if args.max_level else "sense límit (el de la taula)"),
        ("DIF", "per talla: HAURIA - STOCK ZLD (total, offerable + non-offerable) - ENV PENDENTS; a la vista model_color, net de totes les talles"),
        ("REPO", "per talla: DIF si és positiu (si no, 0); a la vista model_color, suma de les talles curtes; els HI26 NOU sense marca a 'es pot enviar?' (CREAT A ZLD? = NO CONSTA) es deixen a 0"),
        ("PREPARABLE", "min(REPO, Stock Disponible 30 Dies a Toni Pons), talla per talla"),
        ("COBERTURA SET", f"{COBERTURA_FACTOR} x (STOCK ZLD + ENV PENDENTS) / VENDA SET, en setmanes; el x{COBERTURA_FACTOR} compensa les devolucions, que tornen a estar disponibles. Només informativa"),
        ("Gèneres -> taula de nivells", "DONA, UNISEX -> MUJER (unisex 46-47 = talla 45) | HOME -> CABALLERO | NENS, MINI -> NIÑO (mini <25 = talla 25) | COMPLEMENTS -> objectiu directe"),
        ("Models a reposar", f"{len(models)} SKUs, {models['model_color'].nunique()} model_color"),
        ("Stock Zalando", f"{snap_meta['fitxer']} ({snap_meta['data']}), {snap_meta['eans']} EANs, {snap_meta['total']} parells"),
        ("Snapshots rebutjats", ", ".join(snap_meta["rebutjats"]) or "-"),
        ("Enviaments pendents", ", ".join(pend_labels) + f" = {int(pending['ENV PENDENTS'].sum()) if len(pending) else 0} parells"),
        ("Stock Toni Pons", tp_file),
        ("Vendes 2026", f"{len(sources)} fitxers setmanals (pestanya DADES2), {int(lines['units'].sum())} unitats"),
        ("Venda 2025", f"{int(acum25.sum())} unitats, {len(acum25)} model_color"),
        ("Model_color HI26 NOU que no consten creats a ZLD (REPO = 0)", str(no_created)),
        ("Creats Zalando HI26", f"{len(created)} model_color a la llista; {int((mc['CREAT HI26'] == 'SÍ').sum())} són a Models a reposar" if created else "fitxer no trobat"),
        ("Previsió demanda", f"{prev['fitxer']} ({len(prev['blocks'])} blocs)" if prev else "fitxer no trobat"),
        ("ACUM HI", f"unitats per data de comanda des del {hi_start.strftime('%d/%m/%Y')} fins al {info['setmana_fi']} (última setmana carregada)"),
        ("PREVISIÓ / A COMPRAR", f"PREVISIÓ = ACUM HI / (part de la corba de la col·lecció transcorreguda de l'1/9 al {info['setmana_fi']}) x (% set-des) - ACUM HI, "
                                 f"models HI; A COMPRAR = PREVISIÓ - STOCK ZLD - ENV PENDENTS - DISPONIBLE ALMACÉN (>= 0). "
                                 + (" | ".join(prev_avisos) if prev_avisos else "")),
        ("Disponible almacén (Previsió demanda)", f"{almacen_meta['fitxer']}: {almacen_meta['skus']} SKUs, {almacen_meta['total']} parells disponibles" if almacen_meta else "fitxer no trobat"),
        ("Informació models zalando (DTE)", (f"{zinfo_meta['fitxer']} ({zinfo_meta['data']}), país {zinfo_meta['pais']}: {zinfo_meta['eans']} EANs, "
                                             f"{zinfo_meta['amb_dte']} amb descompte; {int((mc['DTE'] > 0).sum())} model_color del llistat amb DTE")
                                            if zinfo_meta else "cap fitxer; DTE = 0"),
        ("Avisos", " | ".join(warnings) or "-"),
    ]

    print("Escrivint sortides...")
    year = info["setmana_fi"][:4]
    vendes_dir = os.path.join(data, "Vendes", year)
    repo_dir = os.path.join(out, "REPO")
    os.makedirs(vendes_dir, exist_ok=True)
    os.makedirs(repo_dir, exist_ok=True)
    venda_xlsx = safe_out(os.path.join(vendes_dir, f"Venda {year} {args.date}.xlsx"))
    write_vendes(lines, sources, acum25, venda_xlsx, info)
    xlsx = safe_out(os.path.join(repo_dir, f"REPO ZALANDO {args.date}.xlsx"))
    write_excel(sku, mc, fora, params, levels, xlsx)
    html_path = safe_out(os.path.join(repo_dir, f"REPO ZALANDO {args.date}.html"))
    title = f"Reposició Zalando {args.date}"
    subtitle = (f"Setmana {week_lbl} · stock Zalando {snap_meta['fitxer']} · enviaments pendents {', '.join(pend_labels) or 'cap'} · "
                f"regla venda x{mult:g} ({mult_src}) → nivell · generat {dt.datetime.now():%d/%m/%Y %H:%M}")
    write_html(sku, mc, title, subtitle, warnings, html_path,
               totals={"stock_zld": snap_meta["total"], "venda_setm": info["venda_setm_total"]}, sel_key=args.date, prev=prev,
               mc_prev=mc_prev, chart={"year": info["any"], "coverEnd": info["setmana_fi"], "months": info["mc_months"], "forecast": prev_detail})

    # resum
    print()
    print(f"Setmana: {week_lbl}   Snapshot: {snap_meta['fitxer']}   Pendents: {pend_labels}")
    print(f"SKUs: {len(sku)}   model_color: {len(mc)}   model_color amb venda: {(mc['VENDA SET']>0).sum()}   amb REPO: {(mc['REPO']>0).sum()}")
    print(f"REPO total: {int(sku['REPO'].sum())}   PREPARABLE: {int(sku['PREPARABLE'].sum())}   FALTA STOCK TP: {int((sku['REPO'] - sku['PREPARABLE']).sum())}")
    for w in warnings:
        print("AVÍS:", w)
    print("Sortides:", venda_xlsx, "|", xlsx, "|", html_path)


if __name__ == "__main__":
    main()
