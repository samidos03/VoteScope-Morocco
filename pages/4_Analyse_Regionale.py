import json
from pathlib import Path

import folium
import pandas as pd
import streamlit as st
from branca.colormap import LinearColormap
from streamlit_folium import st_folium

st.set_page_config(page_title="Carte électorale", layout="wide")
st.title("🇲🇦 Carte électorale par région")

BASE_DIR = Path(__file__).resolve().parents[1]
geo = BASE_DIR / "data" / "raw" / "dataset" / "resultats-elections-legislatives-regions-maroc-2016-2026.geojson"

if not geo.exists():
    st.error(f"Fichier introuvable : {geo}")
    st.stop()

gj = json.load(open(geo, encoding="utf-8"))
df = pd.DataFrame([f["properties"] for f in gj["features"]])

year_col = next((c for c in df.columns if "ann" in c.lower() or "year" in c.lower()), None)
if year_col:
    year = st.sidebar.selectbox("Année", sorted(df[year_col].astype(str).unique()))
    keep = df[year_col].astype(str) == year
    df = df[keep]
    gj["features"] = [f for f, k in zip(gj["features"], keep) if k]

cols = [c for c in df.select_dtypes("number").columns if c != year_col]
metric = st.sidebar.selectbox("Indicateur", cols)

vmin, vmax = df[metric].min(), df[metric].max()
cmap = LinearColormap(["#fff2cc", "#e6a23c", "#a00000"], vmin=vmin, vmax=max(vmax, vmin + 1))

m = folium.Map(location=[31.8, -6.5], zoom_start=5, tiles="CartoDB positron")
folium.GeoJson(
    gj,
    style_function=lambda f: {
        "fillColor": cmap(f["properties"].get(metric) or vmin),
        "color": "#555", "weight": 1, "fillOpacity": 0.75,
    },
    tooltip=folium.GeoJsonTooltip(fields=[metric]),
).add_to(m)
cmap.add_to(m)

st_folium(m, height=600, use_container_width=True, returned_objects=[])
st.dataframe(df, use_container_width=True)
