"""Mise en page commune : CSS, barre latérale, barre supérieure."""
from __future__ import annotations

import streamlit as st

from config.settings import CSS_FILE, LOGO_FILE, PROBLEMATIQUE_VIDEO_URL

PLAY_SVG = (
    '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">'
    '<path d="M7 4.5v15a1 1 0 0 0 1.5.86l12.5-7.5a1 1 0 0 0 0-1.72L8.5 3.64A1 1 0 0 0 7 4.5Z"/></svg>'
)


def inject_css() -> None:
    st.markdown(f"<style>{CSS_FILE.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)


def video_button_html(label: str = "Problématique en vidéo", sub: str = "Comprendre le projet en 3 minutes") -> str:
    return (
        f'<a class="sidebar-video" href="{PROBLEMATIQUE_VIDEO_URL}" target="_blank" rel="noopener">'
        f'<span class="play-dot">{PLAY_SVG}</span>'
        f"<span><strong>{label}</strong><small>{sub}</small></span></a>"
    )


def render_sidebar_extras() -> None:
    st.logo(str(LOGO_FILE), size="large")
    with st.sidebar:
        st.markdown(video_button_html(), unsafe_allow_html=True)
        st.markdown(
            '<div class="sidebar-foot"><div class="morocco-flag">★</div>'
            "<div><strong>Royaume du Maroc</strong><small>Intelligence électorale</small></div></div>",
            unsafe_allow_html=True,
        )


def topbar(title: str) -> None:
    st.markdown(
        f"""<div class="topbar">
          <div class="crumb"><span>VoteScope Morocco</span><strong>{title}</strong></div>
          <div class="topbar-status"><i></i><span>Données du projet</span><b>2016 · 2021 · 2026</b></div>
        </div>""",
        unsafe_allow_html=True,
    )
