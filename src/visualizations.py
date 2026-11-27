"""Graphiques Plotly et carte Folium aux couleurs de VoteScope."""
from __future__ import annotations

import folium
import pandas as pd
import plotly.graph_objects as go
from branca.colormap import LinearColormap

from config.settings import COLORS, MAJORITY, party_color, party_name

FONT = "DM Sans, sans-serif"


def _layout(fig: go.Figure, height: int = 360, **kw) -> go.Figure:
    fig.update_layout(
        height=height,
        margin=dict(l=10, r=10, t=10, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family=FONT, color="#526159", size=13),
        hoverlabel=dict(bgcolor=COLORS["navy"], font=dict(color="white", family=FONT)),
        legend=dict(orientation="h", y=-0.15, x=0),
        **kw,
    )
    fig.update_xaxes(gridcolor="#edf0ed", zeroline=False, linecolor="#e2e6e2")
    fig.update_yaxes(gridcolor="#edf0ed", zeroline=False, linecolor="#e2e6e2")
    return fig


def seat_bars(df: pd.DataFrame, value: str = "sieges", top: int = 10, height: int = 380) -> go.Figure:
    d = df.sort_values(value, ascending=False).head(top).iloc[::-1]
    fig = go.Figure(
        go.Bar(
            x=d[value],
            y=d["parti"],
            orientation="h",
            marker=dict(color=[party_color(p) for p in d["parti"]], cornerradius=6),
            text=d[value],
            textposition="outside",
            customdata=[party_name(p) for p in d["parti"]],
            hovertemplate="<b>%{customdata}</b><br>%{x} sièges<extra></extra>",
        )
    )
    fig.update_xaxes(showgrid=False, showticklabels=False)
    return _layout(fig, height, bargap=0.35)


def turnout_donut(value: float | None, height: int = 300) -> go.Figure:
    fig = go.Figure(
        go.Pie(
            values=[value, 100 - value],
            labels=["Participation", "Abstention"],
            hole=0.74,
            sort=False,
            marker=dict(colors=[COLORS["green"], "#e8ece8"]),
            textinfo="none",
            hovertemplate="%{label}: %{value:.2f}%<extra></extra>",
        )
    )
    fig.add_annotation(
        text=f"<b>{value:.1f}%</b><br><span style='font-size:11px;color:#96a19a'>PARTICIPATION</span>".replace(".", ","),
        showarrow=False,
        font=dict(size=28, color=COLORS["navy"], family="Manrope, DM Sans, sans-serif"),
    )
    return _layout(fig, height, showlegend=True)


def hemicycle(seats: pd.Series, height: int = 330) -> go.Figure:
    """Hémicycle de 395 sièges (points), coloré par parti."""
    import numpy as np

    seats = seats[seats > 0].sort_values(ascending=False)
    total = int(seats.sum())
    rows = 12
    radii = np.linspace(1.0, 2.2, rows)
    per_row = np.round(radii / radii.sum() * total).astype(int)
    per_row[-1] += total - per_row.sum()
    pts = []
    for r, n in zip(radii, per_row):
        for a in np.linspace(np.pi, 0, n):
            pts.append((a, r * np.cos(a), r * np.sin(a)))
    pts.sort(key=lambda p: -p[0])
    colors, labels = [], []
    for party, n in seats.items():
        colors += [party_color(party)] * int(n)
        labels += [f"{party} · {int(n)} sièges"] * int(n)
    fig = go.Figure(
        go.Scatter(
            x=[p[1] for p in pts],
            y=[p[2] for p in pts],
            mode="markers",
            marker=dict(size=7.5, color=colors[: len(pts)]),
            text=labels[: len(pts)],
            hovertemplate="%{text}<extra></extra>",
        )
    )
    fig.add_annotation(x=0, y=0.25, text=f"<b>{total}</b><br>sièges", showarrow=False,
                       font=dict(size=20, color=COLORS["navy"], family="Manrope, DM Sans, sans-serif"))
    fig.update_xaxes(visible=False)
    fig.update_yaxes(visible=False, scaleanchor="x")
    return _layout(fig, height, showlegend=False)


def slope_chart(pivot: pd.DataFrame, parties: list[str], years: list[int], height: int = 420) -> go.Figure:
    fig = go.Figure()
    for p in parties:
        fig.add_trace(
            go.Scatter(
                x=[str(y) for y in years],
                y=[pivot.loc[p, y] for y in years],
                mode="lines+markers+text",
                name=p,
                line=dict(color=party_color(p), width=3),
                marker=dict(size=10, color="white", line=dict(color=party_color(p), width=3)),
                text=[f"{pivot.loc[p, y]}" for y in years],
                textposition="top center",
                textfont=dict(color=party_color(p), size=11),
                hovertemplate=f"<b>{p}</b> · %{{x}}<br>%{{y}} sièges<extra></extra>",
            )
        )
    fig.add_hline(y=MAJORITY, line=dict(color=COLORS["red"], dash="dot", width=1),
                  annotation_text="Majorité absolue (198)", annotation_font_color=COLORS["red"])
    fig.update_xaxes(type="category")
    return _layout(fig, height)


def grouped_bars(pivot: pd.DataFrame, parties: list[str], years: list[int], height: int = 380) -> go.Figure:
    shades = {2016: "#cbd3dc", 2021: "#8b99a7", 2026: COLORS["navy"], "2031": COLORS["red"]}
    fig = go.Figure()
    for y in years:
        fig.add_trace(
            go.Bar(
                name=str(y),
                x=parties,
                y=[pivot.loc[p, y] if p in pivot.index else 0 for p in parties],
                marker=dict(color=shades.get(y, COLORS["gold"]), cornerradius=4),
                hovertemplate=f"{y} · %{{x}}: %{{y}} sièges<extra></extra>",
            )
        )
    return _layout(fig, height, barmode="group", bargap=0.25)


def line_chart(x, y, name: str, color: str, height: int = 300, suffix: str = "") -> go.Figure:
    fig = go.Figure(
        go.Scatter(
            x=x, y=y, mode="lines+markers", name=name,
            line=dict(color=color, width=3, shape="spline"),
            marker=dict(size=8, color="white", line=dict(color=color, width=2.5)),
            fill="tozeroy", fillcolor=color + "14",
            hovertemplate=f"%{{x}}: %{{y:.2f}}{suffix}<extra></extra>",
        )
    )
    fig.update_xaxes(type="category")
    return _layout(fig, height, showlegend=False)


def multi_line(df: pd.DataFrame, x: str, cols: dict[str, str], height: int = 340, suffix: str = "%") -> go.Figure:
    fig = go.Figure()
    for col, party in cols.items():
        fig.add_trace(
            go.Scatter(
                x=df[x], y=df[col], name=party, mode="lines+markers",
                line=dict(color=party_color(party), width=3),
                marker=dict(size=8),
                hovertemplate=f"<b>{party}</b> · participation %{{x}}%<br>score %{{y}}{suffix}<extra></extra>",
            )
        )
    return _layout(fig, height)


def compare_bars(a: pd.Series, b: pd.Series, label_a: str, label_b: str, height: int = 380) -> go.Figure:
    parties = list(b.sort_values(ascending=False).index)
    fig = go.Figure()
    fig.add_trace(go.Bar(name=label_a, x=parties, y=[a.get(p, 0) for p in parties],
                         marker=dict(color="#cbd3dc", cornerradius=4)))
    fig.add_trace(go.Bar(name=label_b, x=parties, y=[b.get(p, 0) for p in parties],
                         marker=dict(color=[party_color(p) for p in parties], cornerradius=4),
                         text=[b.get(p, 0) for p in parties], textposition="outside"))
    return _layout(fig, height, barmode="group", bargap=0.25)


# --------------------------------------------------------------------------- #
# Carte Folium
# --------------------------------------------------------------------------- #
def _party_table_html(props: dict) -> str:
    seats = sorted(
        ((k[6:].upper(), v) for k, v in props.items() if k.startswith("seats_") and k != "seats_total" and v),
        key=lambda kv: -kv[1],
    )
    total = props["seats_total"] or 1
    rows = "".join(
        f"<tr><td><span style='display:inline-block;width:9px;height:9px;border-radius:50%;"
        f"background:{party_color(p)};margin-right:6px'></span><b>{p}</b></td>"
        f"<td style='text-align:right'>{n}</td>"
        f"<td style='width:90px'><div style='height:6px;border-radius:6px;background:#edf0ed'>"
        f"<div style='height:6px;border-radius:6px;width:{n / total * 100:.0f}%;background:{party_color(p)}'></div>"
        f"</div></td></tr>"
        for p, n in seats
    )
    return rows


def folium_region_map(gj: dict, year: int, metric: str, party: str | None = None) -> folium.Map:
    """Carte choroplèthe des 12 régions pour une année.

    metric = "seats_total" | "lead" | "party_share"
    """
    feats = [f for f in gj["features"] if f["properties"]["year"] == year]
    data = {"type": "FeatureCollection", "features": []}
    for f in feats:
        p = dict(f["properties"])
        p["region_fr"] = p["region_fr"].replace("’", "'")
        p["lead_party"] = p.get("lead_party") or "—"
        share = (p.get(f"seats_{party.lower()}", 0) or 0) / (p["seats_total"] or 1) * 100 if party else 0
        p["party_seats"] = p.get(f"seats_{party.lower()}", 0) or 0 if party else 0
        p["party_share"] = round(share, 1)
        p["popup_html"] = (
            f"<div style='font-family:DM Sans,sans-serif;min-width:240px'>"
            f"<div style='color:#b8202a;font-size:10px;font-weight:800;letter-spacing:.14em'>RÉGION · {year}</div>"
            f"<div style='color:#10293f;font:800 16px Manrope,sans-serif;margin:3px 0 2px'>{p['region_fr']}</div>"
            f"<div style='color:#738078;font-size:12px;margin-bottom:8px'>{p['region_ar']}</div>"
            f"<div style='display:flex;gap:14px;margin-bottom:8px'>"
            f"<div><div style='font-size:10px;color:#909b95'>SIÈGES</div><b style='font-size:18px;color:#10293f'>{p['seats_total']}</b></div>"
            f"<div><div style='font-size:10px;color:#909b95'>EN TÊTE</div><b style='font-size:18px;color:{party_color(p['lead_party'])}'>{p['lead_party']}</b></div>"
            f"<div><div style='font-size:10px;color:#909b95'>SIÈGES DU 1er</div><b style='font-size:18px;color:#10293f'>{p.get('lead_seats') or '—'}</b></div>"
            f"</div><table style='width:100%;font-size:12px;border-collapse:collapse'>{_party_table_html(p)}</table></div>"
        )
        data["features"].append({"type": "Feature", "geometry": f["geometry"], "properties": p})

    m = folium.Map(location=[28.6, -9.0], zoom_start=5, tiles=None, control_scale=True)
    folium.TileLayer(
        tiles="https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png",
        attr="&copy; OpenStreetMap contributors &copy; CARTO", name="Fond de carte", subdomains="abcd",
    ).add_to(m)

    if metric == "lead":
        def style(feat):
            return {"fillColor": party_color(feat["properties"]["lead_party"]), "color": "white",
                    "weight": 1.5, "fillOpacity": 0.78}
        legend_parties = sorted({f["properties"]["lead_party"] for f in data["features"]})
        legend = "".join(
            f"<div><span style='display:inline-block;width:11px;height:11px;border-radius:3px;"
            f"background:{party_color(p)};margin-right:6px'></span>{p}</div>"
            for p in legend_parties
        )
        m.get_root().html.add_child(folium.Element(
            "<div style='position:fixed;top:14px;right:14px;z-index:9999;background:#fffffff0;"
            "border:1px solid #e1e5e1;border-radius:9px;padding:10px 12px;font:12px DM Sans,sans-serif;color:#526159'>"
            f"<b style='color:#10293f'>Parti en tête</b>{legend}</div>"
        ))
    else:
        key = "seats_total" if metric == "seats_total" else "party_share"
        vals = [f["properties"][key] for f in data["features"]]
        end = party_color(party) if metric == "party_share" and party else "#10293f"
        cmap = LinearColormap(["#eef2ee", "#9dc5ad", end], vmin=min(vals), vmax=max(max(vals), min(vals) + 1))
        cmap.caption = "Sièges de la région" if key == "seats_total" else f"Part des sièges {party} (%)"
        cmap.add_to(m)

        def style(feat, key=key, cmap=cmap):
            return {"fillColor": cmap(feat["properties"][key]), "color": "white", "weight": 1.5, "fillOpacity": 0.8}

    tooltip_fields = ["region_fr", "seats_total", "lead_party"]
    aliases = ["Région", "Sièges", "Parti en tête"]
    if party:
        tooltip_fields += ["party_seats", "party_share"]
        aliases += [f"Sièges {party}", f"Part {party} (%)"]

    layer = folium.GeoJson(
        data,
        name="Régions",
        style_function=style,
        highlight_function=lambda _: {"weight": 3, "color": "#b8202a", "fillOpacity": 0.9},
        tooltip=folium.GeoJsonTooltip(
            fields=tooltip_fields, aliases=aliases, sticky=True,
            style="font-family:DM Sans,sans-serif;font-size:13px;border-radius:8px;",
        ),
        popup=folium.GeoJsonPopup(fields=["popup_html"], labels=False, max_width=330),
    )
    layer.add_to(m)
    m.fit_bounds(layer.get_bounds())
    return m
