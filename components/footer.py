import streamlit as st


def footer() -> None:
    st.markdown(
        '<div class="vs-footer"><strong>VoteScope Morocco</strong>'
        "<span>Plateforme académique d'analyse électorale</span>"
        "<p>Sources : Ministère de l'Intérieur, PCNS (Policy Paper 31/26), Banque mondiale. "
        "Les données indisponibles ne sont pas estimées.</p></div>",
        unsafe_allow_html=True,
    )
