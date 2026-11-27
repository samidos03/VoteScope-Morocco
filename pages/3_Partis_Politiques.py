import streamlit as st

from components.cards import html, page_intro, panel_title, year_picker
from components.footer import footer
from components.header import topbar
from config.settings import party_color, party_name
from src.data_loader import load_national_seats, seats_pivot
from src.visualizations import grouped_bars, slope_chart

topbar("Partis politiques")
c1, c2 = st.columns([3, 1], vertical_alignment="bottom")
with c1:
    page_intro(
        "Paysage politique",
        "Partis politiques",
        "Comparez les partis représentés à la Chambre et leur trajectoire parlementaire entre 2016, 2021 et 2026.",
    )
with c2:
    year = year_picker("parties_year")

pv = seats_pivot()
seats = load_national_seats()
votes = seats[seats["annee"] == year].set_index("parti")["pct_voix_locales"]

query = st.text_input("Rechercher", placeholder="🔍  Rechercher un parti ou un acronyme…", label_visibility="collapsed")
order = pv[year].sort_values(ascending=False)
order = order[order > 0]
prev = {2016: None, 2021: 2016, 2026: 2021}[year]

cards = ""
for rank, (party, n) in enumerate(order.items(), start=1):
    name = party_name(party)
    if query and query.lower() not in f"{party} {name}".lower():
        continue
    color = party_color(party)
    if prev is not None:
        d = int(pv.loc[party, year] - pv.loc[party, prev])
        delta = f'<strong class="{"positive" if d >= 0 else "negative"}">{d:+d}</strong>'
    else:
        delta = "<strong>—</strong>"
    v = votes.get(party)
    v_txt = f"{v:.1f}%".replace(".", ",") if v == v and v is not None else "N/D"
    cards += f"""
    <div class="vs-card party-card">
      <div class="party-head"><span class="party-badge" style="background:{color}">{party[:4]}</span>
      <span class="rank">#{rank}</span></div>
      <div><span class="eyebrow" style="color:{color} !important">{party}</span><h4>{name}</h4></div>
      <div class="party-stat">
        <div><small>Sièges · {year}</small><strong>{int(n)}</strong></div>
        <div><small>Évolution</small>{delta}</div>
        <div><small>% voix</small><strong>{v_txt}</strong></div>
      </div>
    </div>"""
html(f'<div class="party-grid">{cards or "<p>Aucun parti ne correspond.</p>"}</div>')

st.write("")
main = [p for p in ["PAM", "RNI", "PI", "PJD", "USFP", "MP", "PPS", "UC"] if p in pv.index]
a, b = st.columns(2)
with a:
    with st.container(border=True, key="panel_parties_slope"):
        panel_title("Trajectoires 2016 → 2021 → 2026", "Nombre de sièges des principaux partis")
        sel = st.multiselect("Partis", main, default=["PAM", "RNI", "PI", "PJD"], label_visibility="collapsed")
        st.plotly_chart(slope_chart(pv, sel, [2016, 2021, 2026]), width="stretch", config={"displayModeBar": False})
with b:
    with st.container(border=True, key="panel_parties_group"):
        panel_title("Évolution comparée des sièges", "Les trois scrutins côte à côte")
        st.plotly_chart(grouped_bars(pv, main, [2016, 2021, 2026], height=470), width="stretch",
                        config={"displayModeBar": False})

footer()
