import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from components.cards import dark_strip, fmt, html, kpi_row, page_intro, panel_title, section_heading
from components.footer import footer
from components.header import topbar
from config.settings import COLORS, MAJORITY, TURNOUT, party_color
from src.data_loader import load_gdp, load_national_indicators, load_party_profiles_by_turnout, seats_pivot
from src.forecast import (
    ELECTION_2031,
    coalition_probability,
    days_until_election,
    project_gdp,
    project_indicator,
    simulate_seats,
    summarize,
)
from src.predictions import scenario_continuity, scenario_recomposition, scenario_turnout
from src.statistics import effective_number_of_parties
from src.visualizations import _layout, compare_bars, hemicycle

CFG = {"displayModeBar": False}

topbar("Perspectives 2031")
page_intro(
    "Laboratoire prospectif",
    "Perspectives 2031",
    "Prochaines législatives attendues le <b>30 septembre 2031</b>. Cette page projette les indicateurs "
    "nationaux et la composition de la Chambre à partir des scrutins 2016, 2021 et 2026 "
    "et du contexte économique jusqu'en 2030.",
)
html(
    '<div class="beta-banner"><span>BETA</span><div><strong>Prévision exploratoire</strong>'
    "<p>Les chiffres ci-dessous sont des projections statistiques fondées sur trois scrutins : "
    "ce ne sont ni des résultats ni des sondages. Les fourchettes comptent autant que les valeurs centrales.</p></div></div>"
)

pv = seats_pivot()
profiles = load_party_profiles_by_turnout()
ind = load_national_indicators()

# ------------------------------------------------------------------ indicateurs projetés
turnout = project_indicator("Participation", TURNOUT, "%", floor=20, ceil=80)
women = project_indicator("Femmes élues", {y: float(ind[y]["femmes_elues"]) for y in (2016, 2021, 2026)})
parties_rep = project_indicator("Partis représentés", {y: float((pv[y] > 0).sum()) for y in (2016, 2021, 2026)})
enp = project_indicator("Nb effectif de partis", {y: effective_number_of_parties(pv[y]) for y in (2016, 2021, 2026)})
gdp = project_gdp(load_gdp(), until=2030)
gdp_proj = gdp[gdp["type"] == "Projeté"]

days = days_until_election()
kpi_row(
    [
        ("📅", "Jours avant le scrutin", fmt(days), f"Le {ELECTION_2031.strftime('%d/%m/%Y')}", COLORS["red"]),
        ("🗳️", "Participation projetée", f"{fmt(turnout.central, 1)}%",
         f"Fourchette {fmt(turnout.low, 0)}–{fmt(turnout.high, 0)} %", COLORS["green"]),
        ("♀", "Femmes élues projetées", fmt(women.central), f"+{fmt(women.slope_per_year, 1)} par an depuis 2016", COLORS["gold"]),
        ("👥", "Partis représentés", fmt(parties_rep.central), f"Fragmentation : {fmt(enp.central, 1)} partis effectifs", COLORS["navy"]),
        ("📈", "Croissance du PIB 2026-2030", f"{fmt(gdp_proj['pib_croissance_pct'].iloc[0], 1)}%/an",
         f"Fourchette {fmt(gdp_proj['bas'].iloc[0], 1)}–{fmt(gdp_proj['haut'].iloc[0], 1)} %", COLORS["blue"]),
    ]
)


def indicator_chart(p, color, suffix="", decimals=1, height=260):
    xs = [str(y) for y in p.history] + ["2031"]
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=xs[:-1], y=list(p.history.values()), mode="lines+markers+text", name="Observé",
        line=dict(color=color, width=3), marker=dict(size=10, color="white", line=dict(color=color, width=3)),
        text=[f"{v:.{decimals}f}{suffix}".replace(".", ",") for v in p.history.values()], textposition="top center",
        hovertemplate="%{x} : %{y:.2f}" + suffix + "<extra></extra>",
    ))
    fig.add_trace(go.Scatter(
        x=[xs[-2], "2031"], y=[list(p.history.values())[-1], p.central], mode="lines",
        line=dict(color=color, width=2, dash="dot"), hoverinfo="skip", showlegend=False,
    ))
    fig.add_trace(go.Scatter(
        x=["2031"], y=[p.central], mode="markers+text", name="Projection 2031",
        marker=dict(size=14, color=COLORS["red"], symbol="diamond"),
        error_y=dict(type="data", symmetric=False, array=[p.high - p.central], arrayminus=[p.central - p.low],
                     color=COLORS["red"], thickness=2, width=8),
        text=[f"{p.central:.{decimals}f}{suffix}".replace(".", ",")], textposition="middle right",
        textfont=dict(color=COLORS["red"], size=13),
        hovertemplate=f"2031 (projection) : %{{y:.2f}}{suffix}<br>fourchette {p.low:.1f} – {p.high:.1f}<extra></extra>",
    ))
    fig.update_xaxes(type="category")
    vals = list(p.history.values()) + [p.low, p.high]
    pad = (max(vals) - min(vals)) * 0.25 or 1
    fig.update_yaxes(range=[min(vals) - pad, max(vals) + pad])
    return _layout(fig, height, showlegend=False)


section_heading("Indicateurs projetés", "Où en sera le Maroc en 2031 ?",
                "Valeur centrale = tendance linéaire 2016 → 2026 ; fourchette = écart entre tendance, moyenne et dernier scrutin.")
c1, c2 = st.columns(2)
with c1:
    with st.container(border=True, key="panel_fc_turnout"):
        panel_title("Participation électorale", "2016 · 2021 · 2026 observés → 2031 projeté (%)")
        st.plotly_chart(indicator_chart(turnout, COLORS["green"], "%"), width="stretch", config=CFG)
with c2:
    with st.container(border=True, key="panel_fc_women"):
        panel_title("Femmes élues à la Chambre", "Nombre de députées")
        st.plotly_chart(indicator_chart(women, COLORS["gold"], decimals=0), width="stretch", config=CFG)
c3, c4 = st.columns(2)
with c3:
    with st.container(border=True, key="panel_fc_enp"):
        panel_title("Fragmentation parlementaire", "Nombre effectif de partis (Laakso-Taagepera)")
        st.plotly_chart(indicator_chart(enp, COLORS["navy"]), width="stretch", config=CFG)
with c4:
    with st.container(border=True, key="panel_fc_gdp"):
        panel_title("Contexte économique jusqu'en 2030", "Croissance du PIB (%) · projection = moyenne 2022-2025")
        obs = gdp[gdp["type"] == "Observé"]
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=list(gdp_proj["annee"]) + list(gdp_proj["annee"])[::-1],
            y=list(gdp_proj["haut"]) + list(gdp_proj["bas"])[::-1],
            mode="lines", fill="toself", fillcolor=COLORS["blue"] + "22", line=dict(width=0), hoverinfo="skip", name="Fourchette",
        ))
        fig.add_trace(go.Scatter(x=obs["annee"], y=obs["pib_croissance_pct"], mode="lines+markers", name="Observé",
                                 line=dict(color=COLORS["navy"], width=3), marker=dict(size=7),
                                 hovertemplate="%{x} : %{y:.2f}%<extra></extra>"))
        fig.add_trace(go.Scatter(x=[obs["annee"].iloc[-1]] + list(gdp_proj["annee"]),
                                 y=[obs["pib_croissance_pct"].iloc[-1]] + list(gdp_proj["pib_croissance_pct"]),
                                 mode="lines", name="Projeté", line=dict(color=COLORS["blue"], width=3, dash="dot"),
                                 hovertemplate="%{x} : %{y:.2f}% (projeté)<extra></extra>"))
        for yy in (2016, 2021, 2026):
            fig.add_vline(x=yy, line=dict(color=COLORS["red"], dash="dot", width=1))
        fig.add_vline(x=2031, line=dict(color=COLORS["red"], width=2),
                      annotation_text="Élections 2031", annotation_position="top left", annotation_font_color=COLORS["red"])
        fig.update_xaxes(range=[2015.5, 2031.5], dtick=1)
        st.plotly_chart(_layout(fig, 260, showlegend=False), width="stretch", config=CFG)

# ------------------------------------------------------------------ prévision d'ensemble
section_heading("Prévision d'ensemble", "La Chambre des représentants en 2031",
                "5 000 simulations mélangeant les trois scénarios ci-dessous, avec une participation et un aléa par parti tirés au hasard.")

with st.expander("⚙️ Hypothèses de la simulation", expanded=False):
    h1, h2, h3 = st.columns(3)
    with h1:
        t_mean = st.slider("Participation moyenne 2031 (%)", 25.0, 60.0, float(round(turnout.central, 1)), 0.5)
    with h2:
        t_sd = st.slider("Incertitude sur la participation (± points)", 0.0, 10.0, 5.0, 0.5)
    with h3:
        noise = st.slider("Volatilité propre à chaque parti", 0.10, 0.60, 0.35, 0.05,
                          help="Écart-type du choc multiplicatif (log). 0,35 ≈ variation typique observée entre deux scrutins.")


@st.cache_data(show_spinner="Simulation de 5 000 scrutins…")
def run_sim(t_mean, t_sd, noise):
    return simulate_seats(seats_pivot(), load_party_profiles_by_turnout(), t_mean, t_sd, noise)


sim = run_sim(t_mean, t_sd, noise)
summ = summarize(sim)
top, second = summ.sort_values("p_tete", ascending=False).index[:2]
seat_cols = sim.drop(columns="_participation")

kpi_row(
    [
        ("🥇", "Favori pour la 1re place", top, f"1er dans {fmt(summ.loc[top, 'p_tete'], 0)} % des simulations", party_color(top)),
        ("🥈", "Principal challenger", second, f"1er dans {fmt(summ.loc[second, 'p_tete'], 0)} % des simulations", party_color(second)),
        ("🏛️", f"Sièges médians {top}", fmt(summ.loc[top, "mediane"]),
         f"80 % des cas entre {fmt(summ.loc[top, 'p10'])} et {fmt(summ.loc[top, 'p90'])}", COLORS["navy"]),
        ("⚖️", "Majorité d'un seul parti", f"{fmt((seat_cols.max(axis=1) >= MAJORITY).mean() * 100, 1)} %",
         "Probabilité qu'un parti atteigne 198 sièges", COLORS["gold"]),
    ]
)

a, b = st.columns([1.5, 1])
with a:
    with st.container(border=True, key="panel_fc_seats"):
        panel_title("Sièges projetés en 2031", "Médiane et intervalle 10 %–90 % · comparaison avec 2026 observé")
        d = summ.head(10)
        fig = go.Figure()
        fig.add_trace(go.Bar(x=d.index, y=[pv.loc[p, 2026] for p in d.index], name="2026 (observé)",
                             marker=dict(color="#cbd3dc", cornerradius=4)))
        fig.add_trace(go.Bar(
            x=d.index, y=d["mediane"], name="2031 (médiane projetée)",
            marker=dict(color=[party_color(p) for p in d.index], cornerradius=4),
            error_y=dict(type="data", symmetric=False, array=d["p90"] - d["mediane"],
                         arrayminus=d["mediane"] - d["p10"], color="#526159", thickness=1.5, width=5),
            customdata=d[["p10", "p90"]].to_numpy(),
            hovertemplate="<b>%{x}</b><br>médiane %{y}<br>80 % : %{customdata[0]:.0f} – %{customdata[1]:.0f}<extra></extra>",
        ))
        st.plotly_chart(_layout(fig, 400, barmode="group", bargap=0.25), width="stretch", config=CFG)
with b:
    with st.container(border=True, key="panel_fc_first"):
        panel_title("Qui arrive en tête\u00a0?", "Part des simulations où le parti est 1er")
        d2 = summ[summ["p_tete"] >= 0.5].sort_values("p_tete")
        fig = go.Figure(go.Bar(
            x=d2["p_tete"], y=d2.index, orientation="h",
            marker=dict(color=[party_color(p) for p in d2.index], cornerradius=5),
            text=[f"{v:.0f} %" for v in d2["p_tete"]], textposition="outside",
            hovertemplate="%{y} : %{x:.1f} %<extra></extra>",
        ))
        fig.update_xaxes(range=[0, 110], showticklabels=False, showgrid=False)
        st.plotly_chart(_layout(fig, 400, bargap=0.35), width="stretch", config=CFG)

with st.container(border=True, key="panel_fc_coal"):
    panel_title("Probabilité de coalition majoritaire en 2031",
                "Choisissez des partis : part des simulations où ils totalisent au moins 198 sièges")
    coal = st.multiselect("Coalition", list(summ.index), default=[p for p in ["PAM", "RNI", "PI"] if p in summ.index],
                          format_func=lambda p: f"{p} (médiane {int(summ.loc[p, 'mediane'])})", key="fc_coal")
    prob = coalition_probability(sim, coal)
    med = int(sim[coal].sum(axis=1).median()) if coal else 0
    ok = prob >= 50
    html(
        f'<div class="data-alert" style="{"" if ok else "background:#fbeeee;border-color:#f0d3d5;color:#b8202a"}">'
        f"<span>{'✔' if ok else '✖'}</span><p><b>{fmt(prob, 1)} %</b> des simulations donnent la majorité à cette coalition "
        f"(médiane : <b>{med} sièges</b> sur 395, majorité à 198).</p></div>"
    )

# ------------------------------------------------------------------ scénarios réglables
section_heading("Explorer les scénarios", "Trois futurs possibles, réglables à la main")
sc_defs = {
    "continuite": ("01", "Scénario de continuité", COLORS["navy"],
                   "La dynamique 2021 → 2026 se prolonge : chaque parti conserve une part de sa tendance récente."),
    "recomposition": ("02", "Scénario de recomposition", COLORS["red"],
                      "Retour vers l'équilibre de long terme : moyenne pondérée des trois derniers scrutins."),
    "participation": ("03", "Scénario de participation", COLORS["green"],
                      "La mobilisation change. On utilise le lien observé en 2026 entre participation et score des partis."),
}
cols = st.columns(3)
params = {}
for col, (key, (num, title, color, text)) in zip(cols, sc_defs.items()):
    with col:
        with st.container(border=True, key=f"panel_sc_{key}"):
            html(f'<div class="scenario-head"><span class="scenario-num" style="color:{color};background:{color}14">{num}</span>'
                 f"<h3>{title}</h3></div><p class='scenario-text'>{text}</p>")
            if key == "continuite":
                params[key] = st.slider("Poids de la tendance récente", 0.0, 1.0, 0.5, 0.1)
            elif key == "recomposition":
                w = st.select_slider("Poids du scrutin le plus récent",
                                     options=["Égal (1-1-1)", "Modéré (1-2-3)", "Fort (1-2-5)"], value="Modéré (1-2-3)")
                params[key] = {"Égal (1-1-1)": (1, 1, 1), "Modéré (1-2-3)": (1, 2, 3), "Fort (1-2-5)": (1, 2, 5)}[w]
            else:
                params[key] = st.slider("Participation en 2031 (%)", 25.0, 60.0, float(round(turnout.central, 1)), 0.5,
                                        key="sc_turnout")

results = {
    "continuite": scenario_continuity(pv, params["continuite"]),
    "recomposition": scenario_recomposition(pv, params["recomposition"]),
}
results["participation"], fits = scenario_turnout(pv, profiles, params["participation"], TURNOUT[2026])
labels = {k: v[1] for k, v in sc_defs.items()}
chosen = st.segmented_control("Scénario affiché", list(labels), format_func=labels.get, default="continuite",
                              key="sc_choice") or "continuite"
res = results[chosen].sort_values(ascending=False)
res = res[res > 0]
base = pv[2026]
x, y = st.columns([1.4, 1])
with x:
    with st.container(border=True, key="panel_sc_bars"):
        panel_title(f"2026 observé vs 2031 · {labels[chosen]}", "Sièges par parti (total ramené à 395)")
        keep = res.index.union(base[base > 0].index)
        st.plotly_chart(compare_bars(base.reindex(keep, fill_value=0), res.reindex(keep, fill_value=0),
                                     "2026 (observé)", "2031 (scénario)", height=380), width="stretch", config=CFG)
with y:
    with st.container(border=True, key="panel_sc_hemi"):
        panel_title("Hémicycle 2031 (scénario)", labels[chosen])
        st.plotly_chart(hemicycle(res, height=380), width="stretch", config=CFG)

# ------------------------------------------------------------------ méthode
with st.expander("Méthode et données utilisées"):
    st.markdown(
        f"""
**Données (data/processed)** : `resultats_partis_2016_2021_2026.csv` et carte régionale (sièges),
`indicateurs_nationaux.csv` / `4_indicateurs_nationaux.csv` (participation, femmes élues, partis représentés),
`indicateurs_socioeco_2016_2026.csv` (croissance du PIB, Banque mondiale),
`data/raw/elections_2026/5_profils_partisans_par_participation.csv` (score des partis selon la participation en 2026).

**Indicateurs** : droite de tendance ajustée sur 2016, 2021 et 2026, prolongée jusqu'en 2031.
La fourchette couvre la tendance, la moyenne des trois scrutins et la valeur 2026.
PIB 2026-2030 : moyenne 2022-2025 ({fmt(gdp_proj['pib_croissance_pct'].iloc[0], 2)} %), fourchette min-max de cette période.

**Sièges (Monte Carlo, 5 000 tirages)** : pour chaque tirage, (1) un poids de tendance α ~ U(0, 1) pour la continuité,
(2) une participation ~ N({fmt(t_mean, 1)} ; {fmt(t_sd, 1)}), (3) un mélange aléatoire (Dirichlet) des trois scénarios,
(4) un choc par parti ~ LogNormal(0 ; {fmt(noise, 2)}), puis répartition de 395 sièges au plus fort reste.
"""
    )
    table = pd.DataFrame({
        "2016": pv[2016], "2021": pv[2021], "2026": pv[2026],
        "2031 médiane": summ["mediane"], "2031 p10": summ["p10"], "2031 p90": summ["p90"],
        "% en tête": summ["p_tete"].round(1),
    }).fillna(0)
    st.dataframe(table.sort_values("2026", ascending=False), width="stretch")

dark_strip(
    "Limites à retenir",
    "Trois scrutins seulement, des alliances, des candidatures et une campagne encore inconnues : "
    "ces projections montrent des ordres de grandeur et leur incertitude, pas le résultat du 30 septembre 2031.",
    "ⓘ",
)

footer()
