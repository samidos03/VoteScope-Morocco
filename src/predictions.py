"""Scénarios exploratoires pour 2031.

Ces fonctions ne produisent PAS des prédictions : ce sont des scénarios transparents,
fondés sur des hypothèses explicites, pour discuter de futurs possibles.
Tous les résultats sont ramenés à 395 sièges par la méthode du plus fort reste.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from config.settings import TOTAL_SEATS


def largest_remainder(values: pd.Series, total: int = TOTAL_SEATS) -> pd.Series:
    """Répartit `total` sièges proportionnellement à `values` (plus fort reste)."""
    v = values.clip(lower=0).astype(float)
    if v.sum() == 0:
        return v.astype(int)
    quotas = v / v.sum() * total
    floors = np.floor(quotas).astype(int)
    rest = total - floors.sum()
    order = (quotas - floors).sort_values(ascending=False).index[:rest]
    floors.loc[order] += 1
    return floors


def scenario_continuity(pivot: pd.DataFrame, momentum: float = 0.5) -> pd.Series:
    """Prolonge la dynamique récente : 2026 + momentum × (2026 − 2021)."""
    raw = pivot[2026] + momentum * (pivot[2026] - pivot[2021])
    return largest_remainder(raw)


def scenario_recomposition(pivot: pd.DataFrame, weights=(1, 2, 3)) -> pd.Series:
    """Retour vers l'équilibre de long terme : moyenne pondérée des trois scrutins."""
    w = dict(zip([2016, 2021, 2026], weights))
    raw = sum(pivot[y] * w[y] for y in w) / sum(weights)
    return largest_remainder(raw)


def scenario_turnout(
    pivot: pd.DataFrame,
    profiles: pd.DataFrame,
    target_turnout: float,
    base_turnout: float = 38.08,
) -> tuple[pd.Series, pd.DataFrame]:
    """Sensibilité à la participation.

    En 2026, le score des grands partis varie avec la participation des circonscriptions
    (fichier 5_profils_partisans_par_participation.csv). On ajuste une droite
    score = a + b × participation pour chaque parti, puis on applique au nombre de
    sièges 2026 le ratio score(cible) / score(participation 2026).
    """
    x = profiles["participation_moyenne_pct"].to_numpy()
    seats = pivot[2026].astype(float).copy()
    fits = []
    for col in [c for c in profiles.columns if c.endswith("_pct") and c != "participation_moyenne_pct"]:
        party = col.replace("_pct", "")
        if party not in seats.index:
            continue
        b, a = np.polyfit(x, profiles[col].to_numpy(), 1)
        base = a + b * base_turnout
        target = max(a + b * target_turnout, 0.1)
        ratio = target / base
        seats[party] = seats[party] * ratio
        fits.append({"parti": party, "pente": b, "score_base": base, "score_cible": target, "ratio": ratio})
    return largest_remainder(seats), pd.DataFrame(fits)
