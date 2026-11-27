"""Prévision exploratoire des législatives du 30 septembre 2031.

Deux briques, toutes deux construites uniquement à partir des fichiers de data/processed :

1. `project_indicator` : projection d'un indicateur national (participation, femmes élues,
   partis représentés, fragmentation…) à partir des scrutins 2016, 2021 et 2026, par trois
   méthodes simples (tendance linéaire, moyenne, persistance). On retient la tendance
   linéaire comme valeur centrale et l'écart entre méthodes comme fourchette.

2. `simulate_seats` : simulation Monte Carlo de la Chambre 2031. Chaque tirage mélange les
   trois scénarios de src/predictions.py (continuité, recomposition, participation) avec des
   poids aléatoires, ajoute un aléa propre à chaque parti, puis répartit 395 sièges.
   On en déduit, pour chaque parti, une médiane, une fourchette 10 %–90 % et la probabilité
   d'arriver en tête.

Avec trois scrutins observés seulement, ces chiffres sont des ordres de grandeur.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date

import numpy as np
import pandas as pd

from config.settings import TOTAL_SEATS, TURNOUT

ELECTION_2031 = date(2031, 9, 30)
YEARS = np.array([2016, 2021, 2026])


def days_until_election(today: date | None = None) -> int:
    return (ELECTION_2031 - (today or date.today())).days


# --------------------------------------------------------------------------- indicateurs
@dataclass
class Projection:
    name: str
    unit: str
    history: dict[int, float]
    linear: float
    mean: float
    last: float
    slope_per_year: float

    @property
    def central(self) -> float:
        return self.linear

    @property
    def low(self) -> float:
        return min(self.linear, self.mean, self.last)

    @property
    def high(self) -> float:
        return max(self.linear, self.mean, self.last)


def project_indicator(name: str, values: dict[int, float], unit: str = "", target: int = 2031,
                      floor: float | None = None, ceil: float | None = None) -> Projection:
    years = np.array(sorted(values))
    y = np.array([values[k] for k in years], dtype=float)
    slope, intercept = np.polyfit(years, y, 1)
    lin = float(intercept + slope * target)
    if floor is not None:
        lin = max(lin, floor)
    if ceil is not None:
        lin = min(lin, ceil)
    return Projection(name, unit, {int(k): float(v) for k, v in values.items()}, lin, float(y.mean()),
                      float(y[-1]), float(slope))


def project_gdp(gdp: pd.DataFrame, until: int = 2030) -> pd.DataFrame:
    """Croissance du PIB : historique + projection jusqu'en `until`.

    Valeur centrale : moyenne 2022-2025 (après le rebond post-Covid de 2021).
    Fourchette : min / max observés sur cette même période.
    """
    hist = gdp.dropna().copy()
    hist["type"] = "Observé"
    ref = hist[hist["annee"].between(2022, 2025)]["pib_croissance_pct"]
    centre, lo, hi = ref.mean(), ref.min(), ref.max()
    last = int(hist["annee"].max())
    proj = pd.DataFrame({"annee": range(last + 1, until + 1)})
    proj["pib_croissance_pct"] = centre
    proj["bas"], proj["haut"] = lo, hi
    proj["type"] = "Projeté"
    return pd.concat([hist, proj], ignore_index=True)


# --------------------------------------------------------------------------- Monte Carlo
def _turnout_ratios(parties: pd.Index, profiles: pd.DataFrame, turnouts: np.ndarray, base: float) -> np.ndarray:
    """Ratio score(T) / score(base) pour chaque parti et chaque tirage (1 si non modélisé)."""
    x = profiles["participation_moyenne_pct"].to_numpy()
    ratios = np.ones((len(turnouts), len(parties)))
    for col in profiles.columns:
        if not col.endswith("_pct") or col == "participation_moyenne_pct":
            continue
        party = col[:-4]
        if party not in parties:
            continue
        b, a = np.polyfit(x, profiles[col].to_numpy(), 1)
        j = parties.get_loc(party)
        ratios[:, j] = np.maximum(a + b * turnouts, 0.1) / (a + b * base)
    return ratios


def _allocate(raw: np.ndarray, total: int = TOTAL_SEATS) -> np.ndarray:
    """Plus fort reste, vectorisé sur les tirages (lignes)."""
    raw = np.clip(raw, 0, None)
    quotas = raw / raw.sum(axis=1, keepdims=True) * total
    seats = np.floor(quotas).astype(int)
    rest = total - seats.sum(axis=1)
    order = np.argsort(-(quotas - seats), axis=1)
    for i, r in enumerate(rest):
        seats[i, order[i, :r]] += 1
    return seats


def simulate_seats(pivot: pd.DataFrame, profiles: pd.DataFrame, turnout_mean: float,
                   turnout_sd: float = 5.0, party_noise: float = 0.15, n: int = 5000,
                   seed: int = 2031) -> pd.DataFrame:
    """Renvoie un tableau (n tirages × partis) de sièges 2031 simulés."""
    rng = np.random.default_rng(seed)
    parties = pivot.index
    s16, s21, s26 = (pivot[y].to_numpy(float) for y in (2016, 2021, 2026))

    alpha = rng.uniform(0, 1, (n, 1))
    cont = np.clip(s26 + alpha * (s26 - s21), 0, None)
    reco = np.tile((s16 * 1 + s21 * 2 + s26 * 3) / 6, (n, 1))
    t = np.clip(rng.normal(turnout_mean, turnout_sd, n), 25, 65)
    turn = s26 * _turnout_ratios(parties, profiles, t, TURNOUT[2026])

    w = rng.dirichlet([1, 1, 1], n)
    mix = w[:, [0]] * cont + w[:, [1]] * reco + w[:, [2]] * turn
    mix *= rng.lognormal(0, party_noise, mix.shape)
    seats = _allocate(mix)
    out = pd.DataFrame(seats, columns=parties)
    out["_participation"] = t
    return out


def summarize(sim: pd.DataFrame) -> pd.DataFrame:
    seats = sim.drop(columns=[c for c in sim.columns if c.startswith("_")])
    leader = seats.to_numpy().argmax(axis=1)
    p_first = pd.Series(np.bincount(leader, minlength=seats.shape[1]) / len(seats), index=seats.columns)
    res = pd.DataFrame({
        "mediane": seats.median(),
        "p10": seats.quantile(0.10),
        "p90": seats.quantile(0.90),
        "p_tete": p_first * 100,
    })
    res = res[res["p90"] > 0]
    return res.sort_values("mediane", ascending=False)


def coalition_probability(sim: pd.DataFrame, parties: list[str], majority: int = 198) -> float:
    if not parties:
        return 0.0
    return float((sim[parties].sum(axis=1) >= majority).mean() * 100)
