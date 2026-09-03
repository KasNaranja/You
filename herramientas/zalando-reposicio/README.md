# Reposició Zalando

Script `repo_zalando.py`: calcula la reposició setmanal a Zalando per SKU i per
model_color a partir de la venda setmanal, el stock a Zalando, els enviaments
pendents i el stock disponible a Toni Pons.

La còpia que s'executa viu a la carpeta de treball d'OneDrive
`CLAUDE\Zalando reposició` (amb les dades, que no es pugen aquí). Aquesta és la
còpia versionada.

## Fonts que espera a la carpeta de dades

| Fitxer / carpeta | Contingut |
|---|---|
| `Models a reposar.xlsx` | llista base de SKUs (EAN, SKU, SEASON, TEMPORADA, COL·LECCIÓ, GÈNERE, model_color, talla, season Zalando, `es pot enviar?`) |
| `NIVEL.xlsx` | nivells i desglossament per talla: blocs MUJER / CABALLERO / NIÑO |
| `Venda 2025.xlsx` | acumulat 2025 per model_color (pivot `Etiquetas de fila` / `INITIAL+SHIPPED`) |
| `Vendes 2026/<mes>/VENDES DEL dd.mm al dd.mm.xlsx` | vendes setmanals; es llegeix la pestanya **DADES2** (una línia per comanda). `Hoja1` és una còpia antiga idèntica a tots els fitxers i s'ignora |
| `Stock Toni Pons/*.txt` | export SAP UTF-16 amb tabuladors (`Stock 01 02`, `Stock Disponible 30/59 Dies`), sumat per EAN |
| `Stock Zalando/*.csv` o `*.xlsx` | stock snapshot de Zalando. Es descarten els fitxers amb EANs en notació científica (`8,43453E+12`, passa en desar el CSV des d'Excel) |
| `Enviaments pendents/*.csv` | `ean;quantity` dels enviaments ja fets però encara no al snapshot |
| `Ajustos repo.xlsx` (opcional) | `model_color`, `multiplicador`, `nivell`, `comentari` per forçar casos concrets |

## Regla

```
objectiu   = venda setmanal del model_color x MULT (2)
nivell     = primer nivell de la taula del gènere >= objectiu
HAURIA     = desglossament per talla d'aquest nivell
DIF        = HAURIA - stock Zalando (total) - enviaments pendents
REPO       = DIF si > 0 (HI26 NOU sense marca a "es pot enviar?" -> 0)
PREPARABLE = min(REPO, stock disponible 59 dies a Toni Pons)
```

Gèneres: DONA i UNISEX -> MUJER (unisex 46-47 pren la talla 45), HOME -> CABALLERO,
NENS i MINI -> NIÑO (mini < 25 pren la talla 25), COMPLEMENTS -> objectiu directe.

## Ús

```
python repo_zalando.py --date 03.09
python repo_zalando.py --mult 2 --min-level 6 --min-level-kids 2 --max-level 100
```

Sortides: `Vendes 2026.xlsx`, `REPO ZALANDO dd.mm.xlsx` (CÀLCUL SKU, MODEL_COLOR,
FORA LLISTA, PARÀMETRES, NIVELLS) i `REPO ZALANDO dd.mm.html` (les dues vistes,
filtrables i ordenables, sense dependències externes).
