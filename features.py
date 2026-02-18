# features.py
from typing import List, Dict, Any, Tuple

def team_gold_over_time(timeline: Dict[str, Any], match: Dict[str, Any]) -> Tuple[List[float], List[int], List[int]]:
    """
    Returns (minutes, blue_gold, red_gold)
    - minutes: list of timestamps in minutes
    - blue_gold/red_gold: summed totalGold for team in each frame
    """
    # Map participantId -> teamId from match details
    pid_to_team = {}
    for p in match["info"]["participants"]:
        pid_to_team[p["participantId"]] = p["teamId"]

    minutes, blue_gold, red_gold = [], [], []
    frames = timeline["info"]["frames"]

    for frame in frames:
        t_min = frame["timestamp"] / 60000.0
        b_sum, r_sum = 0, 0

        pframes = frame["participantFrames"]
        for pid_str, pf in pframes.items():
            pid = int(pid_str)
            team = pid_to_team.get(pid)
            tg = pf.get("totalGold")
            if tg is None:
                # Some modes/patches might omit; skip safely
                continue
            if team == 100:
                b_sum += tg
            elif team == 200:
                r_sum += tg

        minutes.append(t_min)
        blue_gold.append(b_sum)
        red_gold.append(r_sum)

    return minutes, blue_gold, red_gold


# features.py (add below)
def extract_key_events(timeline: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Pulls a compact list of key events with timestamps.
    """
    key_types = {
        "CHAMPION_KILL",
        "BUILDING_KILL",
        "ELITE_MONSTER_KILL",
        "GAME_END",
    }

    out = []
    for frame in timeline["info"]["frames"]:
        for ev in frame.get("events", []):
            et = ev.get("type")
            if et not in key_types:
                continue

            t_min = ev["timestamp"] / 60000.0

            # Build a readable label
            if et == "CHAMPION_KILL":
                label = f"Kill: {ev.get('killerId')} → {ev.get('victimId')}"
            elif et == "BUILDING_KILL":
                label = f"Tower/Inhib: {ev.get('buildingType')} ({ev.get('laneType')})"
            elif et == "ELITE_MONSTER_KILL":
                label = f"Objective: {ev.get('monsterType')} ({ev.get('monsterSubType','')})"
            else:
                label = "Game End"

            out.append({
                "t_min": t_min,
                "type": et,
                "label": label
            })

    # sort by time
    out.sort(key=lambda x: x["t_min"])
    return out

def _participant_maps(match: dict):
    pid_to_team = {}
    pid_to_champ = {}
    for p in match["info"]["participants"]:
        pid = p["participantId"]
        pid_to_team[pid] = p["teamId"]
        pid_to_champ[pid] = p["championName"]
    return pid_to_team, pid_to_champ

def extract_key_events_rich(timeline: dict, match: dict):
    """
    Returns events with enough info to draw icons + team colors.
    """
    pid_to_team, pid_to_champ = _participant_maps(match)
    out = []

    for frame in timeline["info"]["frames"]:
        for ev in frame.get("events", []):
            et = ev.get("type")
            t_min = ev.get("timestamp", 0) / 60000.0

            if et == "CHAMPION_KILL":
                killer_id = ev.get("killerId", 0)
                victim_id = ev.get("victimId", 0)

                killer_team = pid_to_team.get(killer_id)  # can be None if killerId=0
                out.append({
                    "t_min": t_min,
                    "event_kind": "KILL",
                    "killer_team": killer_team,
                    "killer_champ": pid_to_champ.get(killer_id, "Unknown"),
                    "victim_champ": pid_to_champ.get(victim_id, "Unknown"),
                })

            elif et == "ELITE_MONSTER_KILL":
                out.append({
                    "t_min": t_min,
                    "event_kind": "OBJECTIVE",
                    "killer_team": ev.get("killerTeamId"),
                    "monster": ev.get("monsterType"),      # DRAGON, BARON_NASHOR, RIFTHERALD
                    "monster_sub": ev.get("monsterSubType") # e.g. AIR_DRAGON
                })

            elif et == "BUILDING_KILL":
                out.append({
                    "t_min": t_min,
                    "event_kind": "BUILDING",
                    "building_team": ev.get("teamId"),      # team whose building died
                    "building_type": ev.get("buildingType") # TOWER_BUILDING / INHIBITOR_BUILDING
                })

            elif et == "GAME_END":
                out.append({"t_min": t_min, "event_kind": "GAME_END"})

    out.sort(key=lambda x: x["t_min"])
    return out
