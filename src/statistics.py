"""Indicateurs statistiques classiques en science politique."""
from __future__ import annotations

import pandas as pd


def effective_number_of_parties(seats: pd.Series) -> float:
    """Nombre effectif de partis (Laakso-Taagepera) calculé sur les sièges."""
    total = seats.sum()
    if total == 0:
        return 0.0
    shares = seats / total
    return float(1 / (shares**2).sum())


def pedersen_volatility(before: pd.Series, after: pd.Series) -> float:
    """Indice de volatilité de Pedersen (en points de %), calculé sur les parts de sièges."""
    idx = before.index.union(after.index)
    b = before.reindex(idx, fill_value=0)
    a = after.reindex(idx, fill_value=0)
    b = b / b.sum() * 100
    a = a / a.sum() * 100
    return float((a - b).abs().sum() / 2)


def concentration_top(seats: pd.Series, n: int = 3) -> float:
    """Part (%) des sièges détenue par les n premiers partis."""
    return float(seats.sort_values(ascending=False).head(n).sum() / seats.sum() * 100)
