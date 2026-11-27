"""VoteScope Morocco — point d'entrée Streamlit.

Lancer :  streamlit run app.py
"""
import streamlit as st

from components.header import inject_css, render_sidebar_extras
from config.settings import LOGO_FILE

st.set_page_config(
    page_title="VoteScope Morocco",
    page_icon=str(LOGO_FILE),
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_css()

pages = {
    "Navigation": [
        st.Page("pages/1_Accueil.py", title="Vue d'ensemble", icon=":material/home:", default=True),
        st.Page("pages/2_Resultats_Electoraux.py", title="Résultats électoraux", icon=":material/bar_chart:", url_path="resultats"),
        st.Page("pages/3_Partis_Politiques.py", title="Partis politiques", icon=":material/groups:", url_path="partis"),
        st.Page("pages/4_Analyse_Regionale.py", title="Analyse régionale", icon=":material/map:", url_path="regions"),
        st.Page("pages/5_Comparaison_Electorale.py", title="Comparaison des élections", icon=":material/compare_arrows:", url_path="comparaison"),
        st.Page("pages/6_Indicateurs_Nationaux.py", title="Indicateurs nationaux", icon=":material/monitoring:", url_path="indicateurs"),
        st.Page("pages/7_Perspectives_2031.py", title="Perspectives 2031", icon=":material/auto_awesome:", url_path="perspectives-2031"),
        st.Page("pages/8_A_Propos.py", title="À propos du projet", icon=":material/info:", url_path="a-propos"),
    ]
}

nav = st.navigation(pages)
render_sidebar_extras()
nav.run()
