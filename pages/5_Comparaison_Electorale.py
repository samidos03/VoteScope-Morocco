import streamlit as st

from components.cards import data_alert, fmt, html, kpi_row, page_intro, panel_title
from components.footer import footer
from components.header import topbar
from config.settings import COLORS, TURNOUT
from src.data_loader import seats_pivot
from src.statistics import effective_number_of_parties, pedersen_volatility
from src.visualizations import compare_bars, line_chart, slope_chart

topbar("Comparaison des élections")
page_intro(
    "Analyse longitudinale",
    "Comparaison des élections",
    "Comparez deux scrutins : basculements de sièges, volatilité électorale, fragmentation et participation.",
)

pv = seats_pivot()
c1, c2, _ = st.columns([1, 1, 2])
with c1:
    y_a = st.selectbox("Scrutin de référence", [2016, 2021, 2026], index=1)
with c2:
    y_b = st.selectbox("Scrutin comparé", [2016, 2021, 2026], index=2)
if y_a == y_b:
    data_alert("Choisissez deux scrutins différents pour lancer la comparaison.")
    st.stop()

delta = (pv[y_b] - pv[y_a]).sort_values()
vol = pedersen_volatility(pv[y_a], pv[y_b])
enp_a, enp_b = effective_number_of_parties(pv[y_a]), effective_number_of_parties(pv[y_b])
dt = TURNOUT[y_b] - TURNOUT[y_a]

kpi_row(
    [
        ("🗳️", f"Participation {y_a} → {y_b}", f"{fmt(TURNOUT[y_b], 1)}%",
         f"{'+' if dt >= 0 else ''}{fmt(dt, 1)} points", COLORS["green"] if dt >= 0 else COLORS["red"]),
        ("↗", "Plus forte hausse", delta.index[-1], f"+{int(delta.iloc[-1])} sièges", COLORS["navy"]),
        ("↘", "Plus forte baisse", delta.index[0], f"{int(delta.iloc[0])} sièges", COLORS["red"]),
        ("🔀", "Volatilité (Pedersen)", f"{fmt(vol, 1)}%", "Part des sièges ayant changé de camp", COLORS["gold"]),
        ("🧩", "Nb effectif de partis", f"{fmt(enp_a, 1)} → {fmt(enp_b, 1)}", "Fragmentation parlementaire", COLORS["blue"]),
    ]
)

a, b = st.columns(2)
with a:
    with st.container(border=True, key="panel_cmp_bars"):
        panel_title(f"Sièges {y_a} vs {y_b}", "Partis représentés au moins une fois")
        keep = pv[(pv[y_a] > 0) | (pv[y_b] > 0)]
        st.plotly_chart(compare_bars(keep[y_a], keep[y_b], str(y_a), str(y_b), height=420),
                        width="stretch", config={"displayModeBar": False})
with b:
    with st.container(border=True, key="panel_cmp_slope"):
        panel_title("Évolution du nombre de sièges", "Trajectoires sur les trois scrutins")
        st.plotly_chart(slope_chart(pv, ["PAM", "RNI", "PI", "PJD", "USFP"], [2016, 2021, 2026], height=420),
                        width="stretch", config={"displayModeBar": False})

with st.container(border=True, key="panel_cmp_turnout"):
    panel_title("Évolution de la participation", "Taux national par scrutin (%)")
    st.plotly_chart(line_chart(["2016", "2021", "2026"], [TURNOUT[y] for y in (2016, 2021, 2026)],
                               "Participation", COLORS["green"], suffix="%"),
                    width="stretch", config={"displayModeBar": False})

html(
    """<div class="vs-card" style="display:grid;grid-template-columns:1fr 70px 1fr 70px 1fr;align-items:center;padding:22px;margin-top:6px">
      <div><span class="eyebrow">2016</span><h4 style="margin:4px 0 0">Le PJD arrive en tête</h4><p style="color:#8c9791;margin:2px 0 0">125 sièges · 2e mandat</p></div>
      <i style="height:1px;background:#b9c4bd"></i>
      <div><span class="eyebrow">2021</span><h4 style="margin:4px 0 0">Recomposition parlementaire</h4><p style="color:#8c9791;margin:2px 0 0">Le RNI arrive en tête avec 102 sièges</p></div>
      <i style="height:1px;background:#b9c4bd"></i>
      <div><span class="eyebrow">2026</span><h4 style="margin:4px 0 0">Le PAM prend la tête</h4><p style="color:#8c9791;margin:2px 0 0">97 sièges · retour du PJD (54)</p></div>
    </div>"""
)

footer()
