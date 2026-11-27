import pandas as pd
import streamlit as st
from streamlit_folium import st_folium

from components.cards import data_alert, html, kpi_row, page_intro, panel_title, year_picker
from components.footer import footer
from components.header import topbar
from config.settings import COLORS, party_color, party_name
from src.data_loader import load_geojson, load_regional, load_regions_summary
from src.visualizations import _layout, folium_region_map

import plotly.graph_objects as go

topbar("Analyse régionale")
c1, c2 = st.columns([3, 1], vertical_alignment="bottom")
with c1:
    page_intro(
        "Lecture territoriale",
        "Analyse régionale",
        "Carte interactive des 12 régions du Royaume. Survolez une région pour ses statistiques clés, "
        "cliquez pour afficher le détail des sièges par parti.",
    )
with c2:
    year = year_picker("reg_year")

gj = load_geojson()
reg = load_regional()
summary = load_regions_summary()
r_year = reg[reg["annee"] == year]
s_year = summary[summary["annee"] == year].sort_values("sieges_total", ascending=False)

if year == 2016:
    data_alert("Pour 2016, les données régionales ne couvrent que les 305 sièges des circonscriptions locales "
               "(les 90 sièges de la liste nationale ne sont pas ventilés par région).")

# ---------------------------------------------------------------- contrôles carte
parties_in_year = (
    r_year.groupby("parti")["sieges"].sum().sort_values(ascending=False).loc[lambda s: s > 0].index.tolist()
)
m1, m2 = st.columns([2, 2])
with m1:
    mode = st.segmented_control(
        "Indicateur", ["Parti en tête", "Sièges de la région", "Implantation d'un parti"],
        default="Parti en tête", key="reg_mode",
    ) or "Parti en tête"
with m2:
    party = None
    if mode == "Implantation d'un parti":
        party = st.selectbox("Parti", parties_in_year, index=0, format_func=lambda p: f"{p} — {party_name(p)}")

metric = {"Parti en tête": "lead", "Sièges de la région": "seats_total", "Implantation d'un parti": "party_share"}[mode]

left, right = st.columns([1.35, 1])
with left:
    with st.container(border=True, key="panel_reg_map"):
        panel_title("Carte du Maroc par région", f"Scrutin {year} · Folium / OpenStreetMap")
        fmap = folium_region_map(gj, year, metric, party)
        out = st_folium(fmap, height=560, width="stretch",
                        returned_objects=["last_active_drawing"], key=f"map_{year}_{metric}_{party}")

clicked = None
if out and out.get("last_active_drawing"):
    clicked = out["last_active_drawing"]["properties"]["region_fr"].replace("’", "'")
regions = s_year["region"].tolist()
with right:
    with st.container(border=True, key="panel_reg_detail"):
        default_idx = regions.index(clicked) if clicked in regions else regions.index("Casablanca-Settat")
        region = st.selectbox("Région sélectionnée", regions, index=default_idx)
        row = s_year[s_year["region"] == region].iloc[0]
        detail = r_year[(r_year["region"] == region) & (r_year["sieges"] > 0)].sort_values("sieges", ascending=False)
        lead = row["parti_en_tete"]
        html(
            f'<p class="eyebrow">Région sélectionnée · {year}</p>'
            f'<h2 style="margin:6px 0 0;font:800 26px Manrope, DM Sans, sans-serif">{region}</h2>'
            f'<p style="color:#738078;margin:2px 0 10px">{row["region_ar"]}</p>'
        )
        kpi_row(
            [
                ("🏛️", "Sièges", str(int(row["sieges_total"])), "Total de la région", COLORS["navy"]),
                ("🥇", "En tête", lead if lead != "ÉGALITÉ" else "Égalité", f"{int(detail.iloc[0]['sieges'])} sièges", party_color(lead)),
                ("🗺️", "Circ. locales", str(int(row["nb_circ_locales"])) if pd.notna(row["nb_circ_locales"]) else "N/D",
                 f"{int(row['sieges_regionaux'])} sièges régionaux" if pd.notna(row["sieges_regionaux"]) else "", COLORS["green"]),
            ]
        )
        fig = go.Figure(
            go.Bar(
                x=detail["sieges"], y=detail["parti"], orientation="h",
                marker=dict(color=[party_color(p) for p in detail["parti"]], cornerradius=5),
                text=detail["sieges"], textposition="outside",
                hovertemplate="%{y}: %{x} sièges<extra></extra>",
            )
        )
        fig.update_yaxes(autorange="reversed")
        fig.update_xaxes(showticklabels=False, showgrid=False)
        st.plotly_chart(_layout(fig, 300, bargap=0.3), width="stretch", config={"displayModeBar": False})

# ---------------------------------------------------------------- tableaux
st.write("")
with st.container(border=True, key="panel_reg_heat"):
    panel_title("Sièges par région et par parti", f"Matrice complète · {year}")
    mat = r_year.pivot_table(index="region", columns="parti", values="sieges", aggfunc="sum", fill_value=0)
    mat = mat.loc[:, mat.sum().sort_values(ascending=False).index]
    mat = mat.loc[:, mat.sum() > 0]
    mat["Total"] = mat.sum(axis=1)
    mat = mat.sort_values("Total", ascending=False)
    heat = go.Figure(
        go.Heatmap(
            z=mat.drop(columns="Total").values, x=mat.columns[:-1], y=mat.index,
            colorscale=[[0, "#f6f7f3"], [0.35, "#9dc5ad"], [1, COLORS["navy"]]],
            text=mat.drop(columns="Total").values, texttemplate="%{text}",
            hovertemplate="%{y}<br>%{x}: %{z} sièges<extra></extra>", showscale=False,
        )
    )
    heat.update_yaxes(autorange="reversed")
    st.plotly_chart(_layout(heat, 470), width="stretch", config={"displayModeBar": False})

with st.expander("Voir les données régionales (tableau)"):
    st.dataframe(mat, width="stretch")

footer()
