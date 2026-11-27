import plotly.graph_objects as go
import streamlit as st

from components.cards import fmt, kpi_row, page_intro, panel_title, year_picker
from components.footer import footer
from components.header import topbar
from config.settings import COLORS, TURNOUT
from src.data_loader import (
    load_circonscriptions_2026,
    load_fragmentation,
    load_gdp,
    load_national_indicators,
    load_national_seats,
    load_party_profiles_by_turnout,
    load_turnout_urbanisation,
)
from src.visualizations import _layout, line_chart, multi_line, seat_bars

topbar("Indicateurs nationaux")
c1, c2 = st.columns([3, 1], vertical_alignment="bottom")
with c1:
    page_intro(
        "Baromètre national",
        "Indicateurs nationaux",
        "Synthèse des indicateurs consolidés : participation, représentation, contexte économique "
        "et, pour 2026, profils territoriaux du vote.",
    )
with c2:
    year = year_picker("ind_year")

ind = load_national_indicators()[year]
seats = load_national_seats()
s_year = seats[seats["annee"] == year]


def _get(key, default="N/D"):
    v = ind.get(key)
    return default if v is None else v


inscrits = _get("electeurs_inscrits")
kpi_row(
    [
        ("🗳️", "Participation nationale", f"{fmt(TURNOUT[year], 2)}%", f"Scrutin du {_get('date_scrutin')}", COLORS["green"]),
        ("🏛️", "Sièges", "395", "305 locaux · 90 régionaux", COLORS["navy"]),
        ("👥", "Partis représentés", str(len(s_year)), f"{_get('partis_en_competition', '—')} en compétition" if year == 2016 else "Au moins un siège", COLORS["red"]),
        ("♀", "Femmes élues", str(_get("femmes_elues")), f"dont {_get('femmes_elues_locales')} en circ. locales" if year != 2016 else "Députées", COLORS["gold"]),
        ("📋", "Inscrits / candidats" if year == 2016 else "Circonscriptions locales",
         fmt(float(inscrits)) if year == 2016 else str(_get("circonscriptions_locales", "92")),
         f"{fmt(float(_get('candidats')))} candidats" if year == 2016 else "Découpage 2021-2026", COLORS["blue"]),
    ]
)

a, b = st.columns([2, 1])
with a:
    with st.container(border=True, key="panel_ind_turnout"):
        panel_title("Évolution de la participation", "Taux nationaux 2016 · 2021 · 2026")
        fig = go.Figure(
            go.Bar(
                x=["2016", "2021", "2026"], y=[TURNOUT[y] for y in (2016, 2021, 2026)],
                marker=dict(color=[COLORS["green"] if y == year else "#9dc5ad" for y in (2016, 2021, 2026)], cornerradius=8),
                text=[f"{fmt(TURNOUT[y], 1)}%" for y in (2016, 2021, 2026)], textposition="outside",
                hovertemplate="%{x}: %{y:.2f}%<extra></extra>",
            )
        )
        fig.update_yaxes(range=[0, 65], ticksuffix="%")
        st.plotly_chart(_layout(fig, 340, bargap=0.55), width="stretch", config={"displayModeBar": False})
with b:
    with st.container(border=True, key="panel_ind_seats"):
        panel_title("Répartition des sièges", f"Top 6 · {year}")
        st.plotly_chart(seat_bars(s_year, top=6, height=340), width="stretch", config={"displayModeBar": False})

with st.container(border=True, key="panel_ind_gdp"):
    gdp = load_gdp()
    panel_title("Contexte économique", "Croissance du PIB du Maroc (%, Banque mondiale) — années électorales en rouge")
    fig = line_chart(gdp["annee"], gdp["pib_croissance_pct"], "PIB", COLORS["navy"], height=280, suffix="%")
    for y in (2016, 2021, 2026):
        fig.add_vline(x=y, line=dict(color=COLORS["red"], dash="dot", width=1))
    st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})

if year == 2026:
    st.markdown('<div class="section-heading"><div><p class="eyebrow">Focus 2026</p><h2>Géographie de la participation</h2></div>'
                "<p>Données issues du Policy Paper PCNS 31/26.</p></div>", unsafe_allow_html=True)
    c, d = st.columns(2)
    with c:
        with st.container(border=True, key="panel_ind_urb"):
            urb = load_turnout_urbanisation()
            panel_title("Participation selon l'urbanisation", "Quintiles de circonscriptions (Q1 = plus rurales)")
            fig = go.Figure(go.Bar(
                x=urb["quintile_urbanisation"] + " · " + urb["urbanisation_moyenne_pct"].astype(str) + "% urb.",
                y=urb["participation_moyenne_pct"],
                marker=dict(color=COLORS["green"], cornerradius=6),
                text=urb["participation_moyenne_pct"].map(lambda v: f"{v:.1f}%"), textposition="outside",
            ))
            fig.update_yaxes(range=[0, 55], ticksuffix="%")
            st.plotly_chart(_layout(fig, 320, bargap=0.4), width="stretch", config={"displayModeBar": False})
    with d:
        with st.container(border=True, key="panel_ind_prof"):
            prof = load_party_profiles_by_turnout()
            panel_title("Score des partis selon la participation", "Plus la participation est faible, plus le PJD est fort")
            st.plotly_chart(
                multi_line(prof, "participation_moyenne_pct",
                           {"PAM_pct": "PAM", "RNI_pct": "RNI", "PI_pct": "PI", "PJD_pct": "PJD"}, height=320),
                width="stretch", config={"displayModeBar": False},
            )
    e, f = st.columns(2)
    with e:
        with st.container(border=True, key="panel_ind_frag"):
            fr = load_fragmentation()
            panel_title("Fragmentation selon la taille de la circonscription", "Nombre effectif de partis moyen")
            fig = go.Figure(go.Bar(x=fr["nb_sieges"].astype(str) + " sièges", y=fr["nombre_effectif_partis_moyen"],
                                   marker=dict(color=COLORS["gold"], cornerradius=6),
                                   text=fr["nombre_effectif_partis_moyen"], textposition="outside"))
            st.plotly_chart(_layout(fig, 300, bargap=0.4), width="stretch", config={"displayModeBar": False})
    with f:
        with st.container(border=True, key="panel_ind_circ"):
            circ = load_circonscriptions_2026().dropna(subset=["participation_pct"]).sort_values("participation_pct")
            panel_title("Participation par circonscription", "Cas documentés (min. 21 % · max. 88 %)")
            fig = go.Figure(go.Bar(
                x=circ["participation_pct"], y=circ["circonscription"], orientation="h",
                marker=dict(color=[COLORS["red"] if v < 30 else COLORS["green"] for v in circ["participation_pct"]], cornerradius=4),
                text=circ["participation_pct"].map(lambda v: f"{v:.1f}%"), textposition="outside",
                customdata=circ["parti_en_tete"], hovertemplate="%{y}<br>%{x:.2f}% · en tête : %{customdata}<extra></extra>",
            ))
            fig.update_xaxes(range=[0, 100])
            st.plotly_chart(_layout(fig, 300), width="stretch", config={"displayModeBar": False})

footer()
