"""
Exoplanet Detection Bias Visualization
---------------------------------------
Shows that our exoplanet catalog reflects instrument limits,
not the true distribution of planets in the galaxy.

The gaps are the story: methods have narrow sensitivity windows,
so the catalog over-represents large, close-in, short-period planets.

Usage:
    python visualize.py
Output:
    exoplanet_bias.png  (saved in the same directory)
"""

import sys
from pathlib import Path

import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import pandas as pd

# ── Paths ─────────────────────────────────────────────────────────────────────
HERE = Path(__file__).parent
DATA = HERE.parent / "Downloads" / "exoplanets.csv"
OUT  = HERE / "exoplanet_bias.png"


# ── Sensitivity zone definitions ──────────────────────────────────────────────
# These are simplified editorial approximations, not precise instrument limits.
# Transit:        favors short-period planets (needs multiple transits) of any size
# Radial Velocity: favors massive (large-radius proxy) planets at short-to-mid periods
# Direct Imaging:  favors large, self-luminous planets far from their star
ZONES = [
    {
        "label":    "Transit",
        "desc":     "Transit\nzone",
        "xmin": 0.2,  "xmax": 300,
        "ymin": 0.4,  "ymax": 30,
        "color":    "#3A86FF",
        "alpha":    0.13,
        "label_xy": (3.5, 22),
    },
    {
        "label":    "Radial Velocity",
        "desc":     "Radial Velocity\nzone",
        "xmin": 0.5,  "xmax": 4000,
        "ymin": 2.0,  "ymax": 30,
        "color":    "#20C997",
        "alpha":    0.15,
        "label_xy": (100, 22),
    },
    {
        "label":    "Direct Imaging",
        "desc":     "Imaging\nzone",
        "xmin": 1500, "xmax": 1.3e7,
        "ymin": 7,    "ymax": 30,
        "color":    "#FF9F1C",
        "alpha":    0.20,
        "label_xy": (2e5, 22),
    },
]

# Detection desert: the region all methods struggle to reach
DESERT = {"xmin": 300, "xmax": 1.3e7, "ymin": 0.3, "ymax": 2.0}


# ── Drawing helpers ───────────────────────────────────────────────────────────

def draw_zone(ax, z: dict) -> None:
    """Fill a rectangular sensitivity zone and draw its border."""
    ax.fill_between(
        [z["xmin"], z["xmax"]], z["ymin"], z["ymax"],
        color=z["color"], alpha=z["alpha"], zorder=1
    )
    ax.plot(
        [z["xmin"], z["xmax"], z["xmax"], z["xmin"], z["xmin"]],
        [z["ymin"], z["ymin"], z["ymax"], z["ymax"], z["ymin"]],
        color=z["color"], alpha=0.50, linewidth=0.9, zorder=2
    )


def draw_detection_desert(ax) -> None:
    """Draw the annotated 'detection desert' in the bottom-right quadrant."""
    d = DESERT
    ax.fill_between(
        [d["xmin"], d["xmax"]], d["ymin"], d["ymax"],
        color="#CC2936", alpha=0.07, zorder=1
    )
    ax.plot(
        [d["xmin"], d["xmax"], d["xmax"], d["xmin"], d["xmin"]],
        [d["ymin"], d["ymin"], d["ymax"], d["ymax"], d["ymin"]],
        color="#CC2936", alpha=0.55, linewidth=1.2, linestyle="--", zorder=2
    )
    ax.text(
        2e5, 0.68,
        "DETECTION DESERT\n"
        "Small planets + long orbits\n"
        "\u2022  Too faint for transit\n"
        "\u2022  Too light for radial velocity\n"
        "\u2022  Too close to star to image",
        color="#CC2936", fontsize=8.5, ha="center", va="center",
        fontstyle="italic",
        bbox=dict(
            boxstyle="round,pad=0.45", fc="white",
            ec="#CC2936", alpha=0.92, lw=0.9
        ),
        zorder=5
    )


def draw_earth_reference(ax) -> None:
    """Mark Earth's position to show it falls inside the detection desert."""
    ax.scatter([365.25], [1.0], marker="*", color="#28A745",
               s=150, zorder=6, label="_nolegend_")
    ax.annotate(
        "Earth",
        xy=(365.25, 1.0), xytext=(50, 0.45),
        fontsize=8, color="#28A745", ha="center",
        arrowprops=dict(arrowstyle="->", color="#28A745", lw=0.9),
        bbox=dict(boxstyle="round,pad=0.3", fc="white",
                  ec="#28A745", alpha=0.9, lw=0.7),
        zorder=6
    )


# ── Main figure builder ───────────────────────────────────────────────────────

def build_figure(df: pd.DataFrame) -> plt.Figure:
    fig, ax = plt.subplots(figsize=(13, 8))
    ax.set_xscale("log")
    ax.set_yscale("log")

    # Layers: zones → planets → labels/annotations
    for z in ZONES:
        draw_zone(ax, z)
    draw_detection_desert(ax)

    ax.scatter(
        df["pl_orbper"], df["pl_rade"],
        color="#555555", alpha=0.40, s=9,
        zorder=3, rasterized=True
    )

    draw_earth_reference(ax)

    # Zone labels (on top of fill, behind dots)
    for z in ZONES:
        ax.text(
            *z["label_xy"], z["desc"],
            color=z["color"], fontsize=8.5,
            ha="center", va="center", fontweight="bold",
            bbox=dict(fc="white", alpha=0.75, pad=2.5, ec="none"),
            zorder=4
        )

    # ── Axis limits and ticks ─────────────────────────────────────────────────
    ax.set_xlim(0.2, 1.3e7)
    ax.set_ylim(0.28, 35)

    ax.set_xticks([0.3, 1, 10, 100, 365.25, 3652, 36525, 365250, 3.65e6])
    ax.set_xticklabels(
        ["0.3 d", "1 day", "10 d", "100 d",
         "1 yr", "10 yr", "100 yr", "1,000 yr", "10,000 yr"],
        fontsize=8.5
    )

    ax.set_yticks([0.3, 0.5, 1, 2, 4, 8, 16, 32])
    ax.set_yticklabels(
        ["0.3\u00d7", "0.5\u00d7", "1\u00d7  Earth",
         "2\u00d7", "4\u00d7  super-Earth",
         "8\u00d7", "16\u00d7  Jupiter-size", "32\u00d7"],
        fontsize=8.5
    )

    ax.set_xlabel("Orbital Period", fontsize=11, labelpad=8)
    ax.set_ylabel("Planet Radius  (Earth radii)", fontsize=11, labelpad=8)
    ax.set_title(
        "Exoplanet Detection Bias: We Find What Our Instruments Can See",
        fontsize=13, fontweight="bold", pad=12
    )

    ax.grid(True, which="major", alpha=0.18, color="gray", zorder=0)
    ax.grid(True, which="minor", alpha=0.07, color="gray", zorder=0)

    # ── Legend ────────────────────────────────────────────────────────────────
    n = len(df)
    legend_handles = [
        mpatches.Patch(fc="#888888", alpha=0.6,
                       label=f"Confirmed exoplanets  (n\u2009=\u2009{n:,})"),
        mpatches.Patch(fc="#3A86FF", alpha=0.45,
                       label="Transit \u2014 short-period, any size"),
        mpatches.Patch(fc="#20C997", alpha=0.45,
                       label="Radial velocity \u2014 massive, close-in"),
        mpatches.Patch(fc="#FF9F1C", alpha=0.45,
                       label="Direct imaging \u2014 large, distant, young"),
        mpatches.Patch(fc="#CC2936", alpha=0.30,
                       label="Detection desert"),
    ]
    ax.legend(
        handles=legend_handles, loc="upper left",
        fontsize=8.5, framealpha=0.92, edgecolor="#cccccc", borderpad=0.8
    )

    fig.text(
        0.5, 0.005,
        "Sensitivity zones are simplified editorial estimates \u2014 "
        "real detection limits vary by instrument, star brightness, and observation duration.  "
        "Source: NASA Exoplanet Archive.",
        ha="center", fontsize=7.5, color="#999999", style="italic"
    )

    plt.tight_layout(rect=[0, 0.028, 1, 1])
    return fig


# ── Entry point ───────────────────────────────────────────────────────────────

def main() -> None:
    if not DATA.exists():
        print(f"ERROR: data file not found:\n  {DATA}", file=sys.stderr)
        sys.exit(1)

    df = pd.read_csv(DATA).dropna(subset=["pl_rade", "pl_orbper"])
    print(f"Loaded {len(df):,} planets with radius + period data")

    fig = build_figure(df)
    fig.savefig(OUT, dpi=150, bbox_inches="tight")
    print(f"Saved -> {OUT}")
    plt.show()


if __name__ == "__main__":
    main()
