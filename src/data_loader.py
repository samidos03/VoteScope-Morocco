"""Chargement (mis en cache) des données du projet."""
from __future__ import annotations

import json

import pandas as pd
import streamlit as st

from config.settings import (
    GEOJSON_FILE,
    PROCESSED_DIR,
    RAW_2026_DIR,
    TOTAL_SEATS,
    TURNOUT,
    party_name,
)


def _csv(path) -> pd.DataFrame:
    return pd.read_csv(path, encoding="utf-8-sig")


# --------------------------------------------------------------------------- #
# Géographie + résultats régionaux
# --------------------------------------------------------------------------- #
def _round_coords(coords, ndigits=3):
    if isinstance(coords[0], (int, float)):
        return [round(coords[0], ndigits), round(coords[1], ndigits)]
    return [_round_coords(c, ndigits) for c in coords]


@st.cache_data(show_spinner=False)
def load_geojson() -> dict:
    """GeoJSON des 12 régions × 3 scrutins (coordonnées allégées pour l'affichage)."""
    gj = json.loads(GEOJSON_FILE.read_text(encoding="utf-8"))
    for feat in gj["features"]:
        geom = feat["geometry"]
        geom["coordinates"] = _round_coords(geom["coordinates"])
        props = feat["properties"]
        feat["id"] = f"{props['year']}-{props['region_code']}"
    return gj


@st.cache_data(show_spinner=False)
def load_regional() -> pd.DataFrame:
    """Une ligne par (année, région, parti) avec le nombre de sièges."""
    gj = json.loads(GEOJSON_FILE.read_text(encoding="utf-8"))
    rows = []
    for feat in gj["features"]:
        p = feat["properties"]
        for key, val in p.items():
            if key.startswith("seats_") and key != "seats_total":
                rows.append(
                    {
                        "annee": int(p["year"]),
                        "region": p["region_fr"].replace("’", "'"),
                        "region_ar": p["region_ar"],
                        "region_code": p["region_code"],
                        "feature_id": f"{p['year']}-{p['region_code']}",
                        "parti": key[6:].upper(),
                        "sieges": int(val or 0),
                        "sieges_region": int(p["seats_total"]),
                        "parti_en_tete": p["lead_party"],
                    }
                )
    return pd.DataFrame(rows)


@st.cache_data(show_spinner=False)
def load_regions_summary() -> pd.DataFrame:
    reg = load_regional()
    base = (
        reg.groupby(["annee", "region", "region_ar", "region_code", "feature_id", "parti_en_tete"])
        ["sieges"].sum().reset_index().rename(columns={"sieges": "sieges_total"})
    )
    struct = _csv(PROCESSED_DIR / "circonscriptions_regionales_maroc.csv")
    struct["region"] = struct["region"].str.replace("’", "'")
    return base.merge(struct, on="region", how="left", suffixes=("", "_struct"))


# --------------------------------------------------------------------------- #
# Résultats nationaux par parti
# --------------------------------------------------------------------------- #
@st.cache_data(show_spinner=False)
def load_national_seats() -> pd.DataFrame:
    """Sièges nationaux par parti et par année (395 sièges par scrutin).

    - 2016 : resultats_partis_2016_2021_2026.csv (le GeoJSON 2016 ne contient que les sièges locaux)
    - 2021, 2026 : agrégation du GeoJSON régional (ventilation complète, 395 sièges)
    """
    res = _csv(PROCESSED_DIR / "resultats_partis_2016_2021_2026.csv")
    s2016 = res[res["annee"] == 2016][["annee", "parti", "sieges_total"]].rename(
        columns={"sieges_total": "sieges"}
    )
    reg = load_regional()
    s_recent = (
        reg[reg["annee"].isin([2021, 2026])].groupby(["annee", "parti"])["sieges"].sum().reset_index()
    )
    df = pd.concat([s2016, s_recent], ignore_index=True)
    df["parti"] = df["parti"].replace({"APFGD": "FGD"})
    df = df.groupby(["annee", "parti"], as_index=False)["sieges"].sum()
    df = df[df["sieges"] > 0].copy()
    df["sieges"] = df["sieges"].astype(int)
    df["nom"] = df["parti"].map(party_name)
    df["part_sieges"] = df["sieges"] / TOTAL_SEATS * 100

    # Pourcentages de voix (disponibles pour 2021 partiellement et 2026)
    votes = _csv(PROCESSED_DIR / "1_partis_2021_2026.csv")[["annee", "parti", "pct_voix_locales"]]
    df = df.merge(votes, on=["annee", "parti"], how="left")
    return df.sort_values(["annee", "sieges"], ascending=[True, False]).reset_index(drop=True)


@st.cache_data(show_spinner=False)
def seats_pivot() -> pd.DataFrame:
    """Tableau parti × année (0 si absent)."""
    df = load_national_seats()
    pv = df.pivot_table(index="parti", columns="annee", values="sieges", fill_value=0).astype(int)
    return pv.sort_values(pv.columns[-1], ascending=False)


# --------------------------------------------------------------------------- #
# Indicateurs nationaux
# --------------------------------------------------------------------------- #
@st.cache_data(show_spinner=False)
def load_national_indicators() -> dict[int, dict[str, str]]:
    df = _csv(PROCESSED_DIR / "indicateurs_nationaux.csv")
    out: dict[int, dict[str, str]] = {}
    for _, r in df.iterrows():
        out.setdefault(int(r["annee"]), {})[r["indicateur"]] = r["valeur"]
    for year, value in TURNOUT.items():
        out.setdefault(year, {})["taux_participation_pct"] = value
    return out


@st.cache_data(show_spinner=False)
def load_indicators_2026() -> pd.DataFrame:
    return _csv(RAW_2026_DIR / "3_indicateurs_2026.csv")


@st.cache_data(show_spinner=False)
def load_gdp() -> pd.DataFrame:
    return _csv(PROCESSED_DIR / "indicateurs_socioeco_2016_2026.csv").dropna()


@st.cache_data(show_spinner=False)
def load_turnout_urbanisation() -> pd.DataFrame:
    return _csv(RAW_2026_DIR / "4_participation_par_urbanisation.csv")


@st.cache_data(show_spinner=False)
def load_party_profiles_by_turnout() -> pd.DataFrame:
    return _csv(RAW_2026_DIR / "5_profils_partisans_par_participation.csv")


@st.cache_data(show_spinner=False)
def load_fragmentation() -> pd.DataFrame:
    return _csv(RAW_2026_DIR / "6_fragmentation_par_nb_sieges.csv")


@st.cache_data(show_spinner=False)
def load_circonscriptions_2026() -> pd.DataFrame:
    df = _csv(PROCESSED_DIR / "2_circonscriptions.csv")
    return df[df["annee"] == 2026]


@st.cache_data(show_spinner=False)
def load_votes_2026() -> pd.DataFrame:
    return _csv(RAW_2026_DIR / "1_partis_2026.csv")
