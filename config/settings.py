"""Configuration centrale de VoteScope Morocco (chemins, palette, partis, liens)."""
from pathlib import Path

# --------------------------------------------------------------------------- #
# Chemins
# --------------------------------------------------------------------------- #
BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
PROCESSED_DIR = DATA_DIR / "processed"
RAW_DIR = DATA_DIR / "raw"
RAW_2026_DIR = RAW_DIR / "elections_2026"
ASSETS_DIR = BASE_DIR / "assets"
CSS_FILE = ASSETS_DIR / "css" / "style.css"
LOGO_FILE = ASSETS_DIR / "images" / "votescope-logo.png"
GEOJSON_FILE = ASSETS_DIR / "maps" / "maroc.geojson"
SOURCES_FILE = DATA_DIR / "external" / "sources.txt"

# --------------------------------------------------------------------------- #
# Identité visuelle (reprise du design Figma Make « elections-2.0 »)
# --------------------------------------------------------------------------- #
COLORS = {
    "navy": "#10293f",
    "red": "#b8202a",
    "green": "#087443",
    "gold": "#c69b45",
    "blue": "#52708d",
    "grey": "#8b99a7",
    "cream": "#f3f2ed",
    "ink": "#263830",
    "muted": "#738078",
    "line": "#dfe4df",
}

YEARS = [2016, 2021, 2026]
TOTAL_SEATS = 395
MAJORITY = 198  # majorité absolue à la Chambre des représentants

# Participation nationale (%). 2021 et 2026 : data/processed/4_indicateurs_nationaux.csv.
# 2016 : taux officiel annoncé par le ministère de l'Intérieur (≈ 43 %), absent des CSV.
TURNOUT = {2016: 43.0, 2021: 50.35, 2026: 38.08}

# --------------------------------------------------------------------------- #
# Partis : nom complet + couleur de repère
# --------------------------------------------------------------------------- #
PARTIES = {
    "RNI": ("Rassemblement National des Indépendants", "#10293f"),
    "PAM": ("Parti Authenticité et Modernité", "#b8202a"),
    "PI": ("Parti de l'Istiqlal", "#087443"),
    "PJD": ("Parti de la Justice et du Développement", "#c69b45"),
    "USFP": ("Union Socialiste des Forces Populaires", "#52708d"),
    "MP": ("Mouvement Populaire", "#6f8f3d"),
    "PPS": ("Parti du Progrès et du Socialisme", "#7b4f7a"),
    "UC": ("Union Constitutionnelle", "#a3623a"),
    "MDS": ("Mouvement Démocratique et Social", "#8b7d5b"),
    "FFD": ("Front des Forces Démocratiques", "#5f8c8a"),
    "AG": ("Alliance de gauche", "#c4545c"),
    "FGD": ("Fédération de la Gauche Démocratique", "#c4545c"),
    "APFGD": ("Fédération de la Gauche Démocratique", "#c4545c"),
    "AFG": ("Alliance de la Fédération de Gauche", "#c4545c"),
    "PSU": ("Parti Socialiste Unifié", "#d9878c"),
    "PUD": ("Parti Unité et Développement", "#9aa6b2"),
    "PGVM": ("Parti de la Gauche Verte Marocaine", "#7fae8e"),
    "PND": ("Parti de la Renaissance et de la Vertu", "#9aa6b2"),
    "P_EQUITE": ("Parti de l'Équité", "#9aa6b2"),
    "CNI": ("Congrès National Ittihadi", "#9aa6b2"),
}

MAIN_PARTIES = ["RNI", "PAM", "PI", "PJD", "USFP", "MP", "PPS", "UC"]


def party_name(code: str) -> str:
    return PARTIES.get(code.upper(), (code, None))[0]


def party_color(code: str) -> str:
    return PARTIES.get(code.upper(), (None, COLORS["grey"]))[1]


# --------------------------------------------------------------------------- #
# Vidéos : ressources YouTube (data/external/sources.txt) + vidéo de la problématique.
# --------------------------------------------------------------------------- #
def _read_video_links() -> list[str]:
    try:
        lines = SOURCES_FILE.read_text(encoding="utf-8").splitlines()
    except FileNotFoundError:
        return []
    return [line.strip() for line in lines if line.strip().startswith("http")]


VIDEO_LINKS = _read_video_links()

# Vidéo de présentation de la problématique (Boujmaa), servie par Streamlit depuis static/
PROBLEMATIQUE_VIDEO_FILE = BASE_DIR / "static" / "boujmaa_problematique.mp4"
PROBLEMATIQUE_VIDEO_URL = "/app/static/boujmaa_problematique.mp4"
PROBLEMATIQUE_POSTER_URL = "/app/static/boujmaa_poster.jpg?v=2"
