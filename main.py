import argparse

from riot_api import get_puuid, get_match_ids, get_match, get_timeline
from features import team_gold_over_time, extract_key_events, extract_key_events_rich
from viz import plot_event_tick_timeline, plot_team_gold, plot_gold_diff, plot_icon_timeline_ddragon
import viz

print("VIZ IMPORTED FROM:", viz.__file__)

def match_overview_table(match: dict):
    """
    Prints a compact 10-player overview.
    Uses Riot ID (gameName#tagLine) because summonerName may be blank.
    """
    info = match["info"]
    rows = []

    for p in info["participants"]:
        summoner = p.get("summonerName") or f'{p.get("riotIdGameName","")}#{p.get("riotIdTagline","")}'
        cs = p["totalMinionsKilled"] + p.get("neutralMinionsKilled", 0)

        rows.append({
            "team": "Blue" if p["teamId"] == 100 else "Red",
            "summoner": summoner,
            "champion": p["championName"],
            "role": f'{p.get("teamPosition","")}/{p.get("individualPosition","")}',
            "K/D/A": f'{p["kills"]}/{p["deaths"]}/{p["assists"]}',
            "gold": p["goldEarned"],
            "cs": cs,
            "dmg_to_champs": p["totalDamageDealtToChampions"],
            "vision": p["visionScore"],
        })

    # Sort by team then role-ish (simple)
    rows.sort(key=lambda r: (r["team"], r["role"], r["summoner"]))

    headers = ["team", "summoner", "champion", "role", "K/D/A", "gold", "cs", "dmg_to_champs", "vision"]
    colw = {h: max(len(h), max(len(str(r[h])) for r in rows)) for h in headers}

    line = " | ".join(h.ljust(colw[h]) for h in headers)
    print(line)
    print("-" * len(line))
    for r in rows:
        print(" | ".join(str(r[h]).ljust(colw[h]) for h in headers))


def main():
    parser = argparse.ArgumentParser(description="LoL Match Analyzer (Riot API)")
    parser.add_argument("--riot_id", default="nytebyte11#8558", help="Riot ID like name#tag")
    parser.add_argument("--match_index", type=int, default=0, help="0 = most recent match")
    parser.add_argument("--count", type=int, default=5, help="How many recent matches to fetch IDs for")
    parser.add_argument("--plots", action="store_true", help="Show gold/time/event plots using timeline data")
    args = parser.parse_args()

    # Parse Riot ID
    if "#" not in args.riot_id:
        raise ValueError("riot_id must look like gameName#tagLine (e.g., nytebyte11#8558)")
    game_name, tag_line = args.riot_id.split("#", 1)

    # 1) Riot ID -> PUUID -> match ids
    puuid = get_puuid(game_name, tag_line)
    match_ids = get_match_ids(puuid, count=args.count)

    if not match_ids:
        raise RuntimeError("No matches found for this player.")
    if args.match_index < 0 or args.match_index >= len(match_ids):
        raise ValueError(f"match_index out of range (0..{len(match_ids)-1})")

    match_id = match_ids[args.match_index]
    print(f"Using match: {match_id}\n")

    match = get_match(match_id)
    match_overview_table(match)

    if args.plots:
        timeline = get_timeline(match_id)

        minutes, blue_gold, red_gold = team_gold_over_time(timeline, match)
        plot_team_gold(minutes, blue_gold, red_gold, title=f"Team Gold Over Time ({match_id})")
        plot_gold_diff(minutes, blue_gold, red_gold, title=f"Gold Difference (Blue - Red) ({match_id})")

        events = extract_key_events_rich(timeline, match)

        events = [e for e in events if e["event_kind"] == "KILL"]

        plot_icon_timeline_ddragon(
            events, 
            assets_dir="assets", 
            title=f"Icon Timeline ({match_id})"
        )


if __name__ == "__main__":
    main()
