"""Composants HTML réutilisables (cartes KPI, titres, encadrés…)."""
from __future__ import annotations

from html import escape

import streamlit as st

from config.settings import YEARS


def html(markup: str) -> None:
    st.markdown(markup, unsafe_allow_html=True)


def page_intro(eyebrow: str, title: str, description: str) -> None:
    html(
        f'<div class="page-intro"><div><p class="eyebrow">{eyebrow}</p>'
        f'<h1>{title}</h1><p class="page-description">{description}</p></div></div>'
    )


def section_heading(eyebrow: str, title: str, text: str = "") -> None:
    right = f"<p>{text}</p>" if text else ""
    html(
        f'<div class="section-heading"><div><p class="eyebrow">{eyebrow}</p>'
        f"<h2>{title}</h2></div>{right}</div>"
    )


def panel_title(title: str, subtitle: str = "") -> None:
    sub = f"<p>{subtitle}</p>" if subtitle else ""
    html(f'<div class="panel-title"><h3>{title}</h3>{sub}</div>')


def kpi_html(icon: str, label: str, value: str, note: str, accent: str) -> str:
    return (
        f'<div class="vs-card kpi"><span class="kpi-line" style="background:{accent}"></span>'
        f'<span class="kpi-icon" style="color:{accent}">{icon}</span>'
        f"<p>{label}</p><strong>{value}</strong><small>{note}</small></div>"
    )


def kpi_row(items: list[tuple[str, str, str, str, str]]) -> None:
    cards = "".join(kpi_html(*item) for item in items)
    html(f'<div class="kpi-grid" style="--cols:{len(items)}">{cards}</div>')


def insight_row(items: list[tuple[str, str, str, str, str]]) -> None:
    """items: (classe up/down/neutral, icône, petit titre, valeur, texte)"""
    cards = "".join(
        f'<div class="vs-card insight"><span class="insight-icon {k}">{i}</span>'
        f"<div><small>{s}</small><strong>{v}</strong><p>{t}</p></div></div>"
        for k, i, s, v, t in items
    )
    html(f'<div class="insight-grid">{cards}</div>')


def data_alert(text: str, icon: str = "ⓘ") -> None:
    html(f'<div class="data-alert"><span>{icon}</span><p>{text}</p></div>')


def empty_data(title: str, text: str) -> None:
    html(f'<div class="empty-data"><span>🗄️</span><div><strong>{escape(title)}</strong><p>{escape(text)}</p></div></div>')


def dark_strip(title: str, text: str, icon: str = "✦") -> None:
    html(f'<div class="dark-strip"><span class="ico">{icon}</span><div><strong>{title}</strong><p>{text}</p></div></div>')


def year_picker(key: str, default: int = 2026, years: list[int] | None = None) -> int:
    years = years or YEARS
    value = st.segmented_control(
        "Année", options=years, default=default, key=key, label_visibility="collapsed"
    )
    return value or default


def fmt(n: float, decimals: int = 0) -> str:
    s = f"{n:,.{decimals}f}".replace(",", " ").replace(".", ",")
    return s
