# src/scraper_indicateurs.py
import io
from pathlib import Path

import pandas as pd
import requests

BASE_DIR = Path(__file__).resolve().parents[1]
OUT_FULL = BASE_DIR / "data" / "processed" / "indicateurs_socioeco_2016_2026.csv"
OUT_SUMMARY = BASE_DIR / "data" / "processed" / "indicateurs_socioeco_resume.csv"
YEARS = range(2016, 2027)

# Indicateurs Banque mondiale (pays : MAR)
WB = {
    "pib_croissance_pct": "NY.GDP.MKTP.KD.ZG",
    "pib_constant_usd": "NY.GDP.MKTP.KD",
    "pib_par_habitant_usd": "NY.GDP.PCAP.KD",
    "inflation_ipc_pct": "FP.CPI.TOTL.ZG",
    "chomage_pct": "SL.UEM.TOTL.ZS",
    "population": "SP.POP.TOTL",
    "croissance_population_pct": "SP.POP.GROW",
    "urbanisation_pct": "SP.URB.TOTL.IN.ZS",
    "pop_0_14_pct": "SP.POP.0014.TO.ZS",
    "pop_65_plus_pct": "SP.POP.65UP.TO.ZS",
    "esperance_vie": "SP.DYN.LE00.IN",
    "mortalite_infantile": "SP.DYN.IMRT.IN",
    "fecondite": "SP.DYN.TFRT.IN",
    "alphabetisation_adultes_pct": "SE.ADT.LITR.ZS",
    "scolarisation_secondaire_pct": "SE.SEC.ENRR",
    "activite_femmes_pct": "SL.TLF.CACT.FE.ZS",
}

HDI_URL = ("https://hdr.undp.org/sites/default/files/2025_HDR/"
           "HDR25_Composite_indices_complete_time_series.csv")
HEADERS = {"User-Agent": "Mozilla/5.0"}


def worldbank(code: str) -> pd.Series:
    url = f"https://api.worldbank.org/v2/country/MAR/indicator/{code}"
    r = requests.get(url, params={"format": "json", "date": "2016:2026",
                                  "per_page": 100}, headers=HEADERS, timeout=30)
    r.raise_for_status()
    data = r.json()
    if len(data) < 2 or not data[1]:
        return pd.Series(dtype=float)
    return pd.Series({int(d["date"]): d["value"] for d in data[1]}, dtype=float)


def idh() -> pd.Series:
    r = requests.get(HDI_URL, headers=HEADERS, timeout=60)
    r.raise_for_status()
    h = pd.read_csv(io.StringIO(r.content.decode("latin-1")))
    row = h[h["iso3"] == "MAR"].iloc[0]
    return pd.Series({y: row.get(f"hdi_{y}") for y in YEARS}, dtype=float)


def latest(s: pd.Series, year: int):
    """Dernière valeur disponible jusqu'à `year` (2026 n'est pas encore publié)."""
    s = s.loc[:year].dropna()
    return (s.iloc[-1], s.index[-1]) if len(s) else (None, None)


# 1) Collecte
df = pd.DataFrame(index=list(YEARS))
for name, code in WB.items():
    try:
        df[name] = worldbank(code)
        print("OK ", name)
    except Exception as e:
        print("ERR", name, e)

try:
    df["idh"] = idh()
    print("OK  idh")
except Exception as e:
    print("ERR idh", e)

df.index.name = "annee"
df.to_csv(OUT_FULL, encoding="utf-8-sig")

# 2) Résumé sur 3 dates : 2016 / 2021 / 2026
rows = []
for col in df.columns:
    r = {"indicateur": col}
    for y in (2016, 2021, 2026):
        r[f"val_{y}"], r[f"annee_{y}"] = latest(df[col], y)
    rows.append(r)

res = pd.DataFrame(rows)
res["ecart_2016_2021"] = res["val_2021"] - res["val_2016"]
res["ecart_2021_2026"] = res["val_2026"] - res["val_2021"]
res.to_csv(OUT_SUMMARY, index=False, encoding="utf-8-sig")

print(res.to_string(index=False))
print("\nFichiers créés :", OUT_FULL.name, "et", OUT_SUMMARY.name)