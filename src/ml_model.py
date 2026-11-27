"""Modèle de Machine Learning simple : prévoir la part des sièges de chaque parti dans chaque région.

- Données : sièges par région, par parti et par scrutin (carte régionale, 12 régions × 3 scrutins).
- Variables explicatives : part du parti dans la région aux deux scrutins précédents
  (t-2, t-1) + le parti (variables indicatrices).
- Cible : part du parti dans la région au scrutin suivant.
- Modèle : régression Ridge (scikit-learn).
- Évaluation : on apprend avec (2016, 2021) → 2026 et on teste en « laissant une région de côté »
  (leave-one-region-out) : le modèle prédit chaque région sans l'avoir vue.
- Prévision 2031 : modèle réentraîné sur toutes les régions, appliqué à (2021, 2026).
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error

from src.data_loader import load_regional
from src.predictions import largest_remainder

ML_PARTIES = ["PAM", "RNI", "PI", "PJD", "USFP", "MP", "PPS", "UC"]


def _shares() -> tuple[pd.DataFrame, pd.DataFrame]:
    r = load_regional().copy()
    r["parti"] = r["parti"].replace({"APFGD": "FGD"})
    seats = r.groupby(["region", "parti", "annee"])["sieges"].sum().unstack("annee", fill_value=0)
    totals = r.groupby(["region", "annee"])["sieges"].sum().unstack("annee")
    share = seats.div(totals.reindex(seats.index.get_level_values("region")).to_numpy()) * 100
    return share, totals


def _features(df: pd.DataFrame, y2: int, y1: int) -> pd.DataFrame:
    x = df[[y2, y1]].set_axis(["part_t_2", "part_t_1"], axis=1).reset_index(drop=True)
    dummies = pd.get_dummies(df.index.get_level_values("parti")).reindex(columns=ML_PARTIES, fill_value=0)
    return pd.concat([x, dummies.astype(float).reset_index(drop=True)], axis=1)


def run_ml(alpha: float = 1.0) -> dict:
    share, totals = _shares()
    data = share[share.index.get_level_values("parti").isin(ML_PARTIES)]
    regions = data.index.get_level_values("region").to_numpy()
    X, y = _features(data, 2016, 2021), data[2026].to_numpy()

    # ---- évaluation leave-one-region-out
    pred = np.zeros(len(y))
    for reg in np.unique(regions):
        test = regions == reg
        model = Ridge(alpha=alpha).fit(X[~test], y[~test])
        pred[test] = model.predict(X[test])
    pred = np.clip(pred, 0, None)
    scores = pd.DataFrame(
        {
            "Méthode": ["Ridge (ML)", "Persistance : comme 2021", "Moyenne 2016-2021"],
            "Erreur moyenne (points de %)": [
                mean_absolute_error(y, pred),
                mean_absolute_error(y, data[2021]),
                mean_absolute_error(y, (data[2016] + data[2021]) / 2),
            ],
        }
    )
    backtest = pd.DataFrame({
        "region": regions, "parti": data.index.get_level_values("parti"),
        "reel_2026": y, "predit_2026": pred,
    })

    # ---- modèle final + prévision 2031
    model = Ridge(alpha=alpha).fit(X, y)
    pred31 = np.clip(model.predict(_features(data, 2021, 2026)), 0, None)
    p31 = pd.Series(pred31, index=data.index)

    rows = []
    for reg in totals.index:
        seats_reg = int(totals.loc[reg, 2026])
        others = share.loc[reg, 2026].drop(ML_PARTIES, errors="ignore")  # petits partis : part 2026
        s = pd.concat([p31.loc[reg], others])
        alloc = largest_remainder(s, seats_reg)
        for party, n in alloc.items():
            rows.append({"region": reg, "parti": party, "sieges_2031": int(n),
                         "sieges_2026": int(round(share.loc[(reg, party), 2026] * seats_reg / 100))
                         if (reg, party) in share.index else 0})
    regional31 = pd.DataFrame(rows)
    national31 = regional31.groupby("parti")[["sieges_2026", "sieges_2031"]].sum()
    national31 = national31[national31.sum(axis=1) > 0].sort_values("sieges_2031", ascending=False)

    coefs = pd.Series(model.coef_, index=X.columns)
    return {"scores": scores, "backtest": backtest, "regional31": regional31, "national31": national31,
            "coefs": coefs, "intercept": float(model.intercept_)}


def geojson_2031(gj: dict, regional31: pd.DataFrame) -> dict:
    """Copie les géométries 2026 et y place les sièges prévus pour 2031 (pour la carte Folium)."""
    feats = []
    for f in gj["features"]:
        p = f["properties"]
        if p["year"] != 2026:
            continue
        reg = p["region_fr"].replace("’", "'")
        d = regional31[regional31["region"] == reg].set_index("parti")["sieges_2031"]
        props = {k: v for k, v in p.items() if not k.startswith("seats_")}
        props.update({f"seats_{k.lower()}": int(v) for k, v in d.items()})
        props["seats_total"] = int(d.sum())
        top = d.sort_values(ascending=False)
        props["lead_party"] = top.index[0] if len(top) < 2 or top.iloc[0] > top.iloc[1] else "ÉGALITÉ"
        props["lead_seats"] = int(top.iloc[0])
        props["year"] = 2031
        feats.append({"type": "Feature", "geometry": f["geometry"], "properties": props})
    return {"type": "FeatureCollection", "features": feats}
