# viz.py
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
from matplotlib.offsetbox import OffsetImage, AnnotationBbox

from ddragon import get_latest_version, get_champion_icon_path


BLUE = (0.20, 0.45, 1.00)
RED  = (1.00, 0.25, 0.25)

def plot_team_gold(minutes, blue_gold, red_gold, title="Team Gold Over Time"):
    plt.figure()
    plt.plot(minutes, blue_gold, label="Blue Team Gold")
    plt.plot(minutes, red_gold, label="Red Team Gold")
    plt.xlabel("Time (minutes)")
    plt.ylabel("Total Gold")
    plt.title(title)
    plt.legend()
    plt.tight_layout()
    plt.show()

def plot_gold_diff(minutes, blue_gold, red_gold, title="Gold Difference (Blue - Red)"):
    diff = [b - r for b, r in zip(blue_gold, red_gold)]
    plt.figure()
    plt.plot(minutes, diff, label="Gold Diff")
    plt.axhline(0)
    plt.xlabel("Time (minutes)")
    plt.ylabel("Gold Difference")
    plt.title(title)
    plt.legend()
    plt.tight_layout()
    plt.show()


def plot_event_tick_timeline(events, title="Game Timeline (Key Events)"):
    """
    Horizontal timeline with vertical ticks and 90° labels.
    Events should be a list of dicts with keys:
      - 't_min' (float)
      - 'label' (str)
      - optionally 'type' (str)

    Staggers tick heights to reduce overlap.
    """
    if not events:
        print("No events to plot.")
        return

    # Sort just in case
    events = sorted(events, key=lambda e: e["t_min"])

    xs = [e["t_min"] for e in events]
    labels = [e["label"] for e in events]

    # Stagger heights in a repeating pattern (helps prevent overlap)
    heights_pattern = [0.20, 0.35, 0.50, 0.65, 0.80]
    heights = [heights_pattern[i % len(heights_pattern)] for i in range(len(xs))]

    plt.figure(figsize=(26, 5))
    ax = plt.gca()

    # Baseline
    xmin, xmax = min(xs), max(xs)
    ax.hlines(0, xmin - 0.5, xmax + 0.5)

    # Vertical ticks
    for x, h, text in zip(xs, heights, labels):
        ax.vlines(x, 0, h)
        ax.text(
            x, h + 0.02, text,
            rotation=90,
            ha="left",
            va="bottom",
            fontsize=8
        )

    ax.set_ylim(-0.05, 1.0)
    ax.set_xlim(xmin - 0.5, xmax + 0.5)
    ax.set_xlabel("Time (minutes)")
    ax.set_yticks([])
    ax.set_title(title)
    plt.tight_layout()
    plt.show()

def _tint_image(img: Image.Image, rgb, strength=0.35):
    img = img.convert("RGBA")
    r, g, b = rgb
    overlay = Image.new("RGBA", img.size, (int(r*255), int(g*255), int(b*255), int(strength*255)))
    return Image.alpha_composite(img, overlay)

def plot_icon_timeline_ddragon(events, assets_dir="assets", title="Game Timeline (Icons)", champ_zoom=0.22, kill_zoom=0.22):
    """
    Champions come from Data Dragon (cached).
    Objectives + kill icon come from your local assets folder:
      assets/objectives/{dragon|baron|herald|tower|inhibitor}.png
      assets/misc/kill.png
    """
    if not events:
        print("No events to plot.")
        return

    version = get_latest_version()

    lanes = [0.20, 0.35, 0.50, 0.65, 0.80]
    xs = [e["t_min"] for e in events]
    xmin, xmax = min(xs), max(xs)

    plt.figure(figsize=(26, 5))
    ax = plt.gca()
    ax.hlines(0, xmin - 0.5, xmax + 0.5)

    def place_icon(img: Image.Image, x, y, z):
        oi = OffsetImage(np.asarray(img), zoom=z)  # <-- convert PIL -> array
        ab = AnnotationBbox(
            oi,
            (x, y),
            frameon=False,
            box_alignment=(0.5, 0.0),
            pad=0.0
        )
        ab.set_clip_on(False)     # <-- don't let axes clip it away
        ab.set_zorder(10)         # <-- draw on top
        ax.add_artist(ab)

    for i, e in enumerate(events):
        x = e["t_min"]
        y = lanes[i % len(lanes)]
        ax.vlines(x, 0, y)

        kind = e["event_kind"]

        if kind == "KILL":
            team = e.get("killer_team")
            tint = BLUE if team == 100 else RED if team == 200 else None

            killer = e.get("killer_champ", "Unknown")
            victim = e.get("victim_champ", "Unknown")

            try:
                k_path = get_champion_icon_path(killer, version=version)
                v_path = get_champion_icon_path(victim, version=version)
                k_img = Image.open(k_path).convert("RGBA")
                v_img = Image.open(v_path).convert("RGBA")

                kill_img = Image.open(f"{assets_dir}/misc/kill.png").convert("RGBA")

                kill_img = kill_img.resize((110, 110), Image.LANCZOS)

                if tint:
                    kill_img = _tint_image(kill_img, tint, strength=0.35)

                dx = 0.5
                place_icon(k_img,       x - dx, y + 0.02, champ_zoom)
                place_icon(kill_img,    x,      y + 0.02, kill_zoom)
                place_icon(v_img,       x + dx, y + 0.02, champ_zoom)
            except Exception:
                ax.text(x, y + 0.02, f"{killer} > {victim}", rotation=90, fontsize=7, ha="left", va="bottom")

        elif kind == "OBJECTIVE":
            team = e.get("killer_team")
            tint = BLUE if team == 100 else RED if team == 200 else None

            monster = e.get("monster", "")
            if monster == "DRAGON":
                icon = f"{assets_dir}/objectives/dragon.png"
            elif monster == "RIFTHERALD":
                icon = f"{assets_dir}/objectives/herald.png"
            elif monster == "BARON_NASHOR":
                icon = f"{assets_dir}/objectives/baron.png"
            else:
                icon = None

            if icon:
                try:
                    img = Image.open(icon).convert("RGBA")
                    if tint:
                        img = _tint_image(img, tint, strength=0.05)
                    place_icon(img, x, y + 0.02)
                except Exception:
                    ax.text(x, y + 0.02, monster, rotation=90, fontsize=7, ha="left", va="bottom")

        elif kind == "BUILDING":
            building_team = e.get("building_team")
            tint = BLUE if building_team == 100 else RED if building_team == 200 else None

            btype = e.get("building_type", "")
            icon = f"{assets_dir}/objectives/inhibitor.png" if btype == "INHIBITOR_BUILDING" else f"{assets_dir}/objectives/tower.png"

            try:
                img = Image.open(icon).convert("RGBA")
                if tint:
                    img = _tint_image(img, tint, strength=0.30)
                place_icon(img, x, y + 0.02)
            except Exception:
                ax.text(x, y + 0.02, btype, rotation=90, fontsize=7, ha="left", va="bottom")

        elif kind == "GAME_END":
            ax.text(x, y + 0.02, "END", rotation=90, fontsize=8, ha="left", va="bottom")

    ax.set_ylim(-0.05, 1.0)
    ax.set_xlim(xmin - 0.5, xmax + 0.5)
    ax.set_xlabel("Time (minutes)")
    ax.set_yticks([])
    ax.set_title(title)
    plt.tight_layout()
    plt.show()