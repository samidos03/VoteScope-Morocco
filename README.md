# 🇲🇦 VoteScope Morocco

**Comprendre les élections. Explorer les données. Anticiper les tendances.**

VoteScope Morocco est une plateforme interactive (Streamlit) d'analyse des élections législatives
marocaines de **2016, 2021 et 2026**, avec une page de **scénarios exploratoires pour 2031**.
L'interface reprend le design Figma Make « elections-2.0 » (palette rouge/vert/navy, typographies
Manrope & DM Sans, cartes KPI, sidebar éditoriale).

## Pages

| Page | Contenu |
|---|---|
| Vue d'ensemble | Hero, chronologie des 3 scrutins, chiffres clés, répartition des sièges, participation, hémicycle |
| Résultats électoraux | KPI, sièges par parti, hémicycle, tableau détaillé, progressions/régressions |
| Partis politiques | Fiches des partis (recherche), trajectoires 2016 → 2026, comparaison des sièges |
| Analyse régionale | **Carte Folium des 12 régions** (parti en tête, sièges, implantation d'un parti) avec infobulle + popup statistiques, fiche région, matrice région × parti |
| Comparaison des élections | Deux scrutins au choix : volatilité de Pedersen, nombre effectif de partis, basculements |
| Indicateurs nationaux | Participation, femmes élues, PIB, focus 2026 (urbanisation, profils partisans, fragmentation) |
| Perspectives 2031 | 3 scénarios réglables (continuité, recomposition, participation), hémicycle 2031, **simulateur de coalition** |
| À propos | Mission, **vidéo de la problématique**, objectifs, technologies |

Le bouton ▶ **« Problématique en vidéo »** (barre latérale, hero et page À propos) ouvre la première
vidéo listée dans `data/external/sources.txt`. Pour en choisir une autre, modifiez
`PROBLEMATIQUE_VIDEO_URL` dans `config/settings.py`.

## Lancer l'application

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Structure

```
app.py                  # navigation (st.navigation) + thème
config/settings.py      # chemins, palette, partis, vidéos
assets/css/style.css    # thème inspiré du design Figma
assets/maps/maroc.geojson
components/             # header (sidebar, topbar), cartes KPI, footer
src/data_loader.py      # chargement des CSV / GeoJSON (cache)
src/statistics.py       # nb effectif de partis, volatilité de Pedersen
src/predictions.py      # scénarios 2031 (total ramené à 395 sièges)
src/visualizations.py   # graphiques Plotly + carte Folium
pages/                  # 8 pages
data/                   # données brutes et traitées
```

## Sources des données

- Ministère de l'Intérieur (résultats 2016 et 2021)
- PCNS, Policy Paper 31/26 (élections 2026)
- Banque mondiale (croissance du PIB)

> Les scénarios 2031 ne sont ni des résultats ni des prédictions : ce sont des projections
> fondées sur des hypothèses explicites, à lire comme des ordres de grandeur.
