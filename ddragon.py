# ddragon.py
import os
import requests
from pathlib import Path

DD_BASE = "https://ddragon.leagueoflegends.com"

def get_latest_version() -> str:
    """Returns latest Data Dragon version string (e.g., '14.16.1')."""
    url = f"{DD_BASE}/api/versions.json"
    r = requests.get(url, timeout=30)
    r.raise_for_status()
    return r.json()[0]

def champion_icon_url(champion_id: str, version: str) -> str:
    """
    champion_id should match Riot's championName field from match-v5
    (e.g., 'Jax', 'KaiSa', 'MonkeyKing').
    """
    return f"{DD_BASE}/cdn/{version}/img/champion/{champion_id}.png"

def ensure_cached(url: str, cache_path: Path) -> Path:
    """
    Downloads url to cache_path if missing. Returns local path.
    """
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    if cache_path.exists():
        return cache_path

    r = requests.get(url, timeout=30)
    r.raise_for_status()
    cache_path.write_bytes(r.content)
    return cache_path

def get_champion_icon_path(champion_id: str, version: str | None = None, cache_dir: str = ".cache/ddragon") -> str:
    """
    Returns a local filepath to a cached champion icon PNG.
    Downloads it on first request.
    """
    if version is None:
        version = get_latest_version()

    url = champion_icon_url(champion_id, version)
    local = Path(cache_dir) / version / "img" / "champion" / f"{champion_id}.png"
    return str(ensure_cached(url, local))
