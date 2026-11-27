import base64

import streamlit as st

from components.cards import fmt, html, kpi_row, panel_title, section_heading, year_picker
from components.footer import footer
from components.header import PLAY_SVG, topbar
from config.settings import COLORS, LOGO_FILE, MAJORITY, PROBLEMATIQUE_VIDEO_URL, TURNOUT
from src.data_loader import load_national_indicators, load_national_seats
from src.visualizations import hemicycle, seat_bars, turnout_donut

topbar("Vue d'ensemble")

seats = load_national_seats()
ind = load_national_indicators()
hero_b64 = base64.b64encode((LOGO_FILE.parent / "hero-background.jpg").read_bytes()).decode()

# ---------------------------------------------------------------- Hero
html(
    f"""
<section class="hero" style="background-image:url(data:image/jpeg;base64,{hero_b64})">
  <div class="hero-shade"></div>
  <div class="hero-content">
    <div class="hero-tag"><span></span> Intelligence électorale · Maroc</div>
    <div class="hero-title">VoteScope <em>Morocco</em></div>
    <div class="hero-sub">Comprendre les élections. Explorer les données. Anticiper les tendances.</div>
    <p>Une plateforme interactive dédiée à l'analyse des élections législatives marocaines
    de 2016, 2021 et 2026 : résultats, dynamiques régionales, participation et scénarios pour 2031.</p>
    <div class="hero-actions">
      <a class="primary" href="/resultats" target="_self">Explorer les données →</a>
      <a class="video" href="{PROBLEMATIQUE_VIDEO_URL}" target="_blank" rel="noopener">
        <span class="play-dot">{PLAY_SVG}</span> Voir la problématique</a>
      <a class="secondary" href="/perspectives-2031" target="_self">Perspectives 2031</a>
    </div>
    <div class="hero-foot"><span>3 scrutins</span><span>12 régions</span><span>92 circonscriptions locales</span><span>395 sièges</span></div>
  </div>
</section>
"""
)

# ---------------------------------------------------------------- Chronologie
section_heading(
    "Chronologie électorale",
    "Les élections législatives marocaines",
    "Trois cycles électoraux, trois paysages politiques : de la domination du PJD (2016) "
    "à la victoire du RNI (2021) puis à la première place du PAM (2026).",
)

summaries = {
    2016: "Le PJD arrive en tête pour la deuxième fois consécutive et dirige le gouvernement.",
    2021: "Effondrement du PJD (125 → 13) et large victoire du RNI ; le paysage est recomposé.",
    2026: "Le PAM arrive en tête, le PJD remonte à 54 sièges ; participation en net recul.",
}
gradients = {
    2016: "linear-gradient(0deg,#5c4317ee,#c69b4566)",
    2021: "linear-gradient(0deg,#0b1c27ee,#10293f66)",
    2026: "linear-gradient(0deg,#7d1219ee,#b8202a66)",
}
positions = {2016: "15% center", 2021: "50% 20%", 2026: "85% center"}
cards = ""
for y in (2016, 2021, 2026):
    top = seats[seats["annee"] == y].iloc[0]
    cards += f"""
    <article class="vs-card election-card">
      <div class="election-image" style="background:{gradients[y]}, url(data:image/jpeg;base64,{hero_b64}) {positions[y]} / 700px">
        <span>Élection législative · {ind[y].get('date_scrutin', '')}</span><strong>{y}</strong>
      </div>
      <div class="election-body">
        <p>{summaries[y]}</p>
        <div class="mini-stats">
          <div><span>Parti en tête</span><strong>{top['parti']}</strong></div>
          <div><span>Sièges</span><strong>{top['sieges']}</strong></div>
          <div><span>Participation</span><strong>{fmt(TURNOUT[y], 1)}%</strong></div>
        </div>
      </div>
    </article>"""
html(f'<div class="timeline-cards">{cards}</div>')

# ---------------------------------------------------------------- KPIs
c1, c2 = st.columns([3, 1], vertical_alignment="bottom")
with c1:
    section_heading("Tableau de bord", "Les chiffres clés")
with c2:
    year = year_picker("home_year")

s_year = seats[seats["annee"] == year]
leader = s_year.iloc[0]
kpi_row(
    [
        ("🏛️", "Sièges parlementaires", "395", "Chambre des représentants", COLORS["navy"]),
        ("🥇", "Parti en tête", leader["parti"], f"{leader['sieges']} sièges · {MAJORITY - leader['sieges']} sous la majorité", COLORS["red"]),
        ("🗳️", "Participation", f"{fmt(TURNOUT[year], 2)}%", "Taux national", COLORS["green"]),
        ("👥", "Partis représentés", str(len(s_year)), "Au moins un siège", COLORS["gold"]),
        ("♀", "Femmes élues", str(ind[year].get("femmes_elues", "N/D")), "Députées", COLORS["blue"]),
    ]
)

col_a, col_b = st.columns([2, 1])
with col_a:
    with st.container(border=True, key="panel_home_bars"):
        panel_title("Répartition des sièges", f"Principaux partis · {year}")
        st.plotly_chart(seat_bars(s_year, top=8), width="stretch", config={"displayModeBar": False})
with col_b:
    with st.container(border=True, key="panel_home_turnout"):
        panel_title("Participation nationale", f"Scrutin {year}")
        st.plotly_chart(turnout_donut(TURNOUT[year]), width="stretch", config={"displayModeBar": False})

with st.container(border=True, key="panel_home_hemi"):
    panel_title("Hémicycle", f"Composition de la Chambre des représentants · {year}")
    st.plotly_chart(hemicycle(s_year.set_index("parti")["sieges"]), width="stretch",
                    config={"displayModeBar": False})

footer()
