import io
import json
import time
from pathlib import Path

import pandas as pd
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

BASE_DIR = Path(__file__).resolve().parents[1]
CACHE_DIR = BASE_DIR / "data" / "external" / "cache_wb"
CACHE_DIR.mkdir(parents=True, exist_ok=True)

# Session avec tentatives automatiques (5 essais, pauses croissantes)
session = requests.Session()
session.headers.update({"User-Agent": "Mozilla/5.0"})
session.mount("https://", HTTPAdapter(max_retries=Retry(
    total=5, backoff_factor=3,
    status_forcelist=[429, 500, 502, 503, 504],
)))


def worldbank(code: str) -> pd.Series:
    cache = CACHE_DIR / f"{code}.json"
    if cache.exists():
        data = json.loads(cache.read_text(encoding="utf-8"))
    else:
        url = f"https://api.worldbank.org/v2/country/MAR/indicator/{code}"
        r = session.get(url, params={"format": "json", "date": "2016:2026",
                                     "per_page": 100}, timeout=(15, 120))
        r.raise_for_status()
        data = r.json()
        if len(data) >= 2 and data[1]:
            cache.write_text(json.dumps(data), encoding="utf-8")
        time.sleep(2)  # pause entre deux appels
    if len(data) < 2 or not data[1]:
        return pd.Series(dtype=float)
    return pd.Series({int(d["date"]): d["value"] for d in data[1]}, dtype=float)