import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from components.cards import dark_strip, fmt, html, kpi_row, page_intro, panel_title
from components.footer import footer
from components.header import topbar
from config.settings import COLORS, MAJORITY, TURNOUT, party_color, party_name
from src.data_loader import load_party_profiles_by_turnout, seats_pivot
from src.predictions import scenario_continuity, scenario_recomposition, scenario_turnout
from src.visualizations import _layout, compare_bars, hemicycle

topbar("Perspectives 2031")
page_intro(
    "Laboratoire prospectif",
    "Perspectives 2031",
    "Trois scénarios exploratoires construits à partir des scrutins 2016, 2021 et 2026. "
    "Réglez les hypothèses et observez la Chambre des représentants qui en résulterait.",
)
html(
    '<div class="beta-banner"><span>BETA</span><div><strong>Analyse exploratoire</strong>'
    "<p>Ces projections ne sont ni des résultats ni des prédictions : ce sont des scénarios "
    "fondés sur des hypothèses explicites, à lire comme des ordres de grandeur.</p></div></div>"
)
st.write("")

pv = seats_pivot()
profiles = load_party_profiles_by_turnout()

# ------------------------------------------------------------------ scénarios
sc_defs = {
    "continuite": ("01", "Scénario de continuité", COLORS["navy"],
                   "La dynamique 2021 → 2026 se prolonge : chaque parti conserve une part de sa tendance récente."),
    "recomposition": ("02", "Scénario de recomposition", COLORS["red"],
                      "Retour vers l'équilibre de long terme : moyenne pondérée des trois derniers scrutins."),
    "participation": ("03", "Scénario de participation", COLORS["green"],
                      "La mobilisation électorale change. On utilise le lien observé en 2026 entre participation et score des partis."),
}

cols = st.columns(3)
params = {}
for col, (key, (num, title, color, text)) in zip(cols, sc_defs.items()):
    with col:
        with st.container(border=True, key=f"panel_sc_{key}"):
            html(f'<div class="scenario-head"><span class="scenario-num" style="color:{color};background:{color}14">{num}</span>'
                 f"<h3>{title}</h3></div><p class='scenario-text'>{text}</p>")
            if key == "continuite":
                params[key] = st.slider("Poids de la tendance récente", 0.0, 1.0, 0.5, 0.1,
                                        help="0 = 2031 identique à 2026 ; 1 = on répète entièrement l'écart 2021→2026")
            elif key == "recomposition":
                w = st.select_slider("Poids donné au scrutin le plus récent",
                                     options=["Égal (1-1-1)", "Modéré (1-2-3)", "Fort (1-2-5)"], value="Modéré (1-2-3)")
                params[key] = {"Égal (1-1-1)": (1, 1, 1), "Modéré (1-2-3)": (1, 2, 3), "Fort (1-2-5)": (1, 2, 5)}[w]
            else:
                params[key] = st.slider("Participation en 2031 (%)", 25.0, 60.0, 45.0, 0.5,
                                        help=f"2016 : {TURNOUT[2016]} % · 2021 : {TURNOUT[2021]} % · 2026 : {TURNOUT[2026]} %")

results = {
    "continuite": scenario_continuity(pv, params["continuite"]),
    "recomposition": scenario_recomposition(pv, params["recomposition"]),
}
results["participation"], fits = scenario_turnout(pv, profiles, params["participation"], TURNOUT[2026])

# ------------------------------------------------------------------ choix du scénario à détailler
st.write("")
labels = {k: v[1] for k, v in sc_defs.items()}
chosen = st.segmented_control("Scénario affiché", list(labels), format_func=labels.get, default="continuite",
                              key="sc_choice") or "continuite"
res = results[chosen].sort_values(ascending=False)
res = res[res > 0]
base = pv[2026]
leader = res.index[0]
delta = (res - base.reindex(res.index, fill_value=0)).sort_values()

kpi_row(
    [
        ("🥇", "Parti en tête (scénario)", leader, f"{int(res.iloc[0])} sièges · {party_name(leader)}", party_color(leader)),
        ("🏛️", "Écart à la majorité", str(MAJORITY - int(res.iloc[0])), "Sièges manquants au premier parti", COLORS["navy"]),
        ("↗", "Plus forte hausse vs 2026", delta.index[-1], f"{int(delta.iloc[-1]):+d} sièges", COLORS["green"]),
        ("↘", "Plus forte baisse vs 2026", delta.index[0], f"{int(delta.iloc[0]):+d} sièges", COLORS["red"]),
    ]
)

a, b = st.columns([1.4, 1])
with a:
    with st.container(border=True, key="panel_sc_bars"):
        panel_title(f"2026 observé vs 2031 · {labels[chosen]}", "Sièges par parti (total ramené à 395)")
        keep = res.index.union(base[base > 0].index)
        st.plotly_chart(compare_bars(base.reindex(keep, fill_value=0), res.reindex(keep, fill_value=0),
                                     "2026 (observé)", "2031 (scénario)", height=400),
                        width="stretch", config={"displayModeBar": False})
with b:
    with st.container(border=True, key="panel_sc_hemi"):
        panel_title("Hémicycle 2031 (scénario)", labels[chosen])
        st.plotly_chart(hemicycle(res, height=400), width="stretch", config={"displayModeBar": False})

# ------------------------------------------------------------------ simulateur de coalition
with st.container(border=True, key="panel_sc_coalition"):
    panel_title("Simulateur de coalition", "Composez une majorité gouvernementale à partir du scénario choisi")
    default = [p for p in ["PAM", "RNI", "PI"] if p in res.index]
    coal = st.multiselect("Partis de la coalition", list(res.index), default=default,
                          format_func=lambda p: f"{p} ({int(res[p])})")
    total = int(res.reindex(coal, fill_value=0).sum())
    ok = total >= MAJORITY
    fig = go.Figure()
    for p in coal:
        fig.add_trace(go.Bar(x=[int(res[p])], y=["Coalition"], orientation="h", name=p,
                             marker=dict(color=party_color(p)), text=p, textposition="inside",
                             hovertemplate=f"{p}: {int(res[p])} sièges<extra></extra>"))
    fig.add_vline(x=MAJORITY, line=dict(color=COLORS["red"], width=2, dash="dash"),
                  annotation_text="Majorité 198", annotation_font_color=COLORS["red"])
    fig.update_xaxes(range=[0, 395])
    st.plotly_chart(_layout(fig, 150, barmode="stack", showlegend=False), width="stretch",
                    config={"displayModeBar": False})
    html(
        f'<div class="data-alert" style="{"" if ok else "background:#fbeeee;border-color:#f0d3d5;color:#b8202a"}">'
        f"<span>{'✔' if ok else '✖'}</span><p><b>{total} sièges</b> — "
        f"{'majorité absolue atteinte' if ok else f'il manque {MAJORITY - total} sièges pour la majorité absolue'}.</p></div>"
    )

# ------------------------------------------------------------------ transparence
with st.expander("Comment sont calculés les scénarios ?"):
    st.markdown(
        f"""
- **Continuité** : `sièges_2031 = sièges_2026 + α × (sièges_2026 − sièges_2021)`, avec α = {params['continuite']}.
- **Recomposition** : moyenne pondérée des sièges 2016, 2021 et 2026 avec les poids {params['recomposition']}.
- **Participation** : pour PAM, RNI, PI et PJD, on ajuste une droite *score = a + b × participation* sur les
  5 groupes de circonscriptions de 2026 (PCNS 31/26), puis on multiplie leurs sièges 2026 par
  `score(participation cible) / score({TURNOUT[2026]} %)`. Les autres partis gardent leurs sièges 2026.
- Dans tous les cas, le total est ramené à **395 sièges** par la méthode du plus fort reste.
"""
    )
    if chosen == "participation" and not fits.empty:
        f = fits.copy()
        f.columns = ["Parti", "Pente (pts de score / pt de participation)", f"Score estimé à {TURNOUT[2026]} %",
                     f"Score estimé à {params['participation']} %", "Coefficient appliqué"]
        st.dataframe(f.round(3), hide_index=True, width="stretch")
    table = pd.DataFrame({"2016": pv[2016], "2021": pv[2021], "2026": pv[2026],
                          "2031 · continuité": results["continuite"],
                          "2031 · recomposition": results["recomposition"],
                          "2031 · participation": results["participation"]}).fillna(0).astype(int)
    st.dataframe(table.sort_values("2026", ascending=False), width="stretch")

c, d = st.columns([1, 1])
with c:
    with st.container(border=True, key="panel_sc_method"):
        html('<p class="eyebrow">Cadre méthodologique</p><h3 style="margin:8px 0 6px;font:800 21px Manrope, DM Sans, sans-serif">'
             "Des projections transparentes et auditables</h3>"
             '<ol class="method-list"><li><span>01</span>Trois scrutins observés (2016, 2021, 2026)</li>'
             "<li><span>02</span>Hypothèses explicites et réglables</li>"
             "<li><span>03</span>Total contraint à 395 sièges (plus fort reste)</li>"
             "<li><span>04</span>Comparaison systématique avec 2026 observé</li></ol>")
with d:
    dark_strip(
        "Limites à retenir",
        "Une projection électorale dépend de facteurs absents de ce dépôt : candidatures, alliances, "
        "découpage, contexte socio-économique, campagne et mobilisation. Avec trois scrutins seulement, "
        "VoteScope privilégie l'explicabilité à la fausse précision.",
        "ⓘ",
    )

footer()
