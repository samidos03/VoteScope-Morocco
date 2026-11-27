import pandas as pd
import streamlit as st

from components.cards import fmt, insight_row, kpi_row, page_intro, panel_title, year_picker
from components.footer import footer
from components.header import topbar
from config.settings import COLORS, MAJORITY, TOTAL_SEATS, TURNOUT
from src.data_loader import load_national_seats, seats_pivot
from src.statistics import concentration_top, effective_number_of_parties
from src.visualizations import hemicycle, seat_bars, turnout_donut

topbar("Résultats électoraux")
c1, c2 = st.columns([3, 1], vertical_alignment="bottom")
with c1:
    page_intro(
        "Analyse électorale",
        "Résultats électoraux",
        "Distribution des 395 sièges de la Chambre des représentants, participation et "
        "principales variations entre les scrutins.",
    )
with c2:
    year = year_picker("res_year")

seats = load_national_seats()
pv = seats_pivot()
s = seats[seats["annee"] == year].reset_index(drop=True)
leader = s.iloc[0]
enp = effective_number_of_parties(s["sieges"])

kpi_row(
    [
        ("🥇", "Parti arrivé en tête", leader["parti"], f"{leader['sieges']} sièges", COLORS["red"]),
        ("🏛️", "Majorité absolue", str(MAJORITY), f"Seuil sur {TOTAL_SEATS} sièges", COLORS["navy"]),
        ("🗳️", "Participation", f"{fmt(TURNOUT[year], 2)}%", "Taux national", COLORS["green"]),
        ("📐", "Nb effectif de partis", fmt(enp, 2), "Indice Laakso-Taagepera", COLORS["gold"]),
    ]
)

a, b = st.columns([2, 1])
with a:
    with st.container(border=True, key="panel_res_bars"):
        panel_title("Sièges obtenus par parti", "Survolez les barres pour afficher le détail")
        st.plotly_chart(seat_bars(s, top=14, height=440), width="stretch", config={"displayModeBar": False})
with b:
    with st.container(border=True, key="panel_res_turnout"):
        panel_title("Participation électorale", "Part nationale des votants")
        st.plotly_chart(turnout_donut(TURNOUT[year], height=250), width="stretch", config={"displayModeBar": False})
    with st.container(border=True, key="panel_res_hemi"):
        panel_title("Hémicycle", f"{year}")
        st.plotly_chart(hemicycle(s.set_index("parti")["sieges"], height=200), width="stretch",
                        config={"displayModeBar": False})

# --------------------------------------------------------------- tableau
prev = {2016: None, 2021: 2016, 2026: 2021}[year]
table = s[["parti", "nom", "sieges", "part_sieges", "pct_voix_locales"]].copy()
table.insert(0, "Rang", range(1, len(table) + 1))
if prev:
    table["Évolution"] = table["parti"].map(lambda p: int(pv.loc[p, year] - pv.loc[p, prev]) if p in pv.index else None)
table = table.rename(
    columns={"parti": "Parti", "nom": "Nom", "sieges": "Sièges", "part_sieges": "Part des 395 sièges (%)",
             "pct_voix_locales": "% voix (listes locales)"}
)
with st.container(border=True, key="panel_res_table"):
    panel_title("Tableau détaillé", "% des voix renseignés uniquement lorsqu'ils figurent dans les sources du projet")
    st.dataframe(
        table,
        hide_index=True,
        width="stretch",
        column_config={
            "Sièges": st.column_config.ProgressColumn("Sièges", format="%d", min_value=0, max_value=int(s["sieges"].max())),
            "Part des 395 sièges (%)": st.column_config.NumberColumn(format="%.1f %%"),
            "% voix (listes locales)": st.column_config.NumberColumn(format="%.1f %%"),
            "Évolution": st.column_config.NumberColumn(format="%+d"),
        },
    )

# --------------------------------------------------------------- insights
if prev:
    delta = (pv[year] - pv[prev]).sort_values()
    up, down = delta.index[-1], delta.index[0]
    insight_row(
        [
            ("up", "↗", "Plus forte progression", f"{up} · +{int(delta[up])} sièges", f"Comparaison {prev} → {year}"),
            ("down", "↘", "Plus forte régression", f"{down} · {int(delta[down])} sièges", f"Comparaison {prev} → {year}"),
            ("neutral", fmt(concentration_top(s.set_index('parti')['sieges']), 0) + "%", "Concentration",
             "Part des 3 premiers partis", "Aucun parti n'atteint seul la majorité absolue"),
        ]
    )
else:
    insight_row(
        [
            ("up", "1", "Parti en tête", f"PJD · {leader['sieges']} sièges", "Deuxième victoire consécutive"),
            ("neutral", "2", "Deuxième force", f"{s.iloc[1]['parti']} · {s.iloc[1]['sieges']} sièges", "Principal parti d'opposition"),
            ("neutral", fmt(concentration_top(s.set_index('parti')['sieges']), 0) + "%", "Concentration",
             "Part des 3 premiers partis", "Majorité absolue : 198 sièges"),
        ]
    )

footer()
