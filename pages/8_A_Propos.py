import base64

import streamlit as st

from components.cards import dark_strip, html, page_intro, panel_title
from components.footer import footer
from components.header import PLAY_SVG, topbar
from config.settings import LOGO_FILE, PROBLEMATIQUE_VIDEO_FILE, PROBLEMATIQUE_VIDEO_URL, VIDEO_LINKS

topbar("À propos du projet")
page_intro(
    "Le projet",
    "À propos de VoteScope Morocco",
    "Un projet académique de data science et de visualisation consacré à l'analyse des élections législatives marocaines.",
)

logo_b64 = base64.b64encode(LOGO_FILE.read_bytes()).decode()
a, b = st.columns([0.8, 1.2], vertical_alignment="center")
with a:
    html(f'<div class="vs-card" style="display:grid;place-items:center;min-height:340px;'
         f'background:radial-gradient(circle,#fff,#eceee9)"><img src="data:image/png;base64,{logo_b64}" '
         f'style="width:80%;max-width:330px;mix-blend-mode:multiply"></div>')
with b:
    html(
        """<p class="eyebrow">Notre mission</p>
        <h2 style="margin:8px 0 14px;font:800 28px/1.25 Manrope, DM Sans, sans-serif">Transformer les données électorales en informations accessibles</h2>
        <p style="color:#6e7c74;line-height:1.8">VoteScope Morocco transforme les données électorales en informations
        compréhensibles grâce à des visualisations interactives, des analyses statistiques et une exploration géographique.</p>
        <p style="color:#6e7c74;line-height:1.8">À travers les élections de 2016, 2021 et 2026, la plateforme étudie
        l'évolution des partis politiques, les dynamiques régionales, la participation et les transformations du paysage politique.</p>
        <p style="color:#6e7c74;line-height:1.8">Le projet combine Data Analysis, Data Visualization et Machine Learning
        exploratoire pour explorer différents scénarios à l'horizon 2031.</p>"""
    )

# ------------------------------------------------------------------ problématique en vidéo
st.write("")
with st.container(border=True, key="panel_about_video"):
    panel_title("La problématique en vidéo", "Cliquez sur le symbole ▶ pour ouvrir la vidéo de présentation")
    v1, v2 = st.columns([1.3, 1])
    with v1:
        st.video(str(PROBLEMATIQUE_VIDEO_FILE))
    with v2:
        html(
            f'<a class="video-card" href="{PROBLEMATIQUE_VIDEO_URL}" target="_blank" rel="noopener">'
            f'<span class="play-dot">{PLAY_SVG}</span><span><strong>Présentation de la problématique</strong>'
            f"<small>Boujmaa · 54 s · ouvrir en plein écran</small></span></a>"
        )
        html("<p style='color:#738078;margin:16px 0 6px;font-size:13px'><b>Ressources vidéo complémentaires</b></p>")
        for i, url in enumerate(VIDEO_LINKS, start=1):
            html(
                f'<a class="video-card" style="margin-bottom:8px" href="{url}" target="_blank" rel="noopener">'
                f'<span class="play-dot" style="background:#10293f;box-shadow:none">{PLAY_SVG}</span>'
                f"<span><strong>Ressource YouTube {i}</strong><small>{url.replace('https://www.', '')}</small></span></a>"
            )

c, d = st.columns([1.1, 0.9])
with c:
    with st.container(border=True, key="panel_about_goals"):
        goals = [
            "Rendre les données électorales accessibles.",
            "Comprendre l'évolution du paysage politique marocain.",
            "Comparer les performances des partis politiques.",
            "Explorer les différences régionales.",
            "Analyser les tendances de participation.",
            "Expérimenter des scénarios prospectifs pour 2031.",
        ]
        html('<p class="eyebrow">Objectifs</p><h3 style="margin:8px 0 0;font:700 20px Manrope, DM Sans, sans-serif">Objectifs du projet</h3>'
             '<ul class="goal-list">' + "".join(f"<li><span>✓</span>{g}</li>" for g in goals) + "</ul>")
with d:
    with st.container(border=True, key="panel_about_tech"):
        tech = ["Python", "Pandas", "NumPy", "Plotly", "Streamlit", "Folium", "Scikit-learn", "Jupyter"]
        html('<p class="eyebrow">Outils & méthodes</p><h3 style="margin:8px 0 0;font:700 20px Manrope, DM Sans, sans-serif">Technologies utilisées</h3>'
             '<div class="tech-tags">' + "".join(f"<span>{t}</span>" for t in tech) + "</div>"
             "<p style='color:#8a958f;margin-top:16px;font-size:13px'>Design de l'interface : maquette Figma Make « elections-2.0 ».</p>")

dark_strip(
    "Un projet de Master en Intelligence Artificielle & Data Science",
    "Conçu comme une plateforme de data journalism, au croisement de la statistique, du design d'information et de l'analyse politique. "
    "Sources : Ministère de l'Intérieur, PCNS (Policy Paper 31/26), Banque mondiale.",
)

footer()
