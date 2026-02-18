# riot_api.py
import os
import requests

API_KEY = os.environ["RIOT_API_KEY"]
HEADERS = {"X-Riot-Token": API_KEY}

def riot_get(url: str) -> tuple[dict, int]:
    r = requests.get(url, headers=HEADERS, timeout=30)
    r.raise_for_status()
    return r.json(), len(r.content)

def get_puuid(game_name: str, tag_line: str) -> str:
    url = f"https://americas.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{game_name}/{tag_line}"
    data, _ = riot_get(url)
    return data["puuid"]

def get_match_ids(puuid: str, start: int = 0, count: int = 10) -> list[str]:
    url = f"https://americas.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?start={start}&count={count}"
    data, _ = riot_get(url)
    return data

def get_match(match_id: str) -> dict:
    url = f"https://americas.api.riotgames.com/lol/match/v5/matches/{match_id}"
    data, _ = riot_get(url)
    return data

def get_timeline(match_id: str) -> dict:
    url = f"https://americas.api.riotgames.com/lol/match/v5/matches/{match_id}/timeline"
    data, _ = riot_get(url)
    return data
