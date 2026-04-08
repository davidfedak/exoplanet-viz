"""
Exoplanet Detection Bias Visualization
---------------------------------------
Shows that our exoplanet catalog reflects instrument limits,
not the true distribution of planets in the galaxy.

Usage:
    python visualize.py
Output:
    exoplanet_bias.png  (saved in the same directory as this script)
"""

import sys
from pathlib import Path

import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import pandas as pd

# ── Paths ─────────────────────────────────────────────────────────────────────
HERE      = Path(__file__).parent
DATA_PATH = HERE.parent / "Downloads" / "exoplanets.csv"
OUT       = HERE / "exoplanet_bias.png"

# ── Sensitivity zone definitions ──────────────────────────────────────────────
# Simplified editorial approximations per PLAN.md Section 6.
ZONES = [
    {
        "label":    "Transit",
        "xmin": 0.5,   "xmax": 100,
        "ymin": 1.0,   "ymax": 25,
        "color":    "steelblue",
        "alpha":    0.15,
        "label_xy": (5, 18),
    },
    {
        "label":    "Radial Velocity",
        "xmin": 0.5,   "xmax": 3000,
        "ymin": 4.0,   "ymax": 25,
        "color":    "darkorange",
        "alpha":    0.15,
        "label_xy": (200, 20),
    },
    {
        "label":    "Direct Imaging",
        "xmin": 1000,  "xmax": 100_000,
        "ymin": 7.0,   "ymax": 25,
        "color":    "mediumseagreen",
        "alpha":    0.20,
        "label_xy": (10_000, 20),
    },
]

# Detection desert: dashed rectangle, not a fill zone
DESERT = {"xmin": 500, "xmax": 50_000, "ymin": 0.3, "ymax": 2.5}


# ── Phase 1: Data loading ─────────────────────────────────────────────────────

def load_data(path: str) -> pd.DataFrame:
    """Read the exoplanet CSV, keep pl_orbper and pl_rade, drop NaNs."""
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Data file not found: {p}")

    df = pd.read_csv(p, comment="#")[["pl_orbper", "pl_rade"]].dropna()
    assert (df > 0).all().all(), "Non-positive values found after cleaning"
    print(f"Loaded {len(df):,} planets after dropping missing values.")
    return df


# ── Phase 2 & 3: Figure construction ─────────────────────────────────────────

def build_figure(df: pd.DataFrame) -> plt.Figure:
    fig, ax = plt.subplots(figsize=(13, 8))

    # Phase 2: log-log axes with fixed limits and plain-language tick labels
    ax.set_xscale("log")
    ax.set_yscale("log")

    ax.set_xlim(0.5, 100_000)
    ax.set_ylim(0.3, 30)

    ax.set_xticks([1, 10, 100, 365.25, 3652.5, 36525])
    ax.set_xticklabels(["1 day", "10 days", "100 days", "1 yr", "10 yr", "100 yr"],
                       fontsize=9)

    ax.set_yticks([1, 2, 4, 11.2, 22.4])
    ax.set_yticklabels(
        ["1\u00d7 Earth", "2\u00d7 Earth", "4\u00d7 super-Earth",
         "11\u00d7 Neptune-size", "22\u00d7 Jupiter-size"],
        fontsize=9,
    )

    ax.minorticks_off()

    # Phase 3 — layer 1: sensitivity zone fills
    for z in ZONES:
        ax.fill_between(
            [z["xmin"], z["xmax"]], z["ymin"], z["ymax"],
            color=z["color"], alpha=z["alpha"], zorder=1,
            label=z["label"],
        )

    # Phase 3 — layer 2: scatter of known planets
    ax.scatter(
        df["pl_orbper"], df["pl_rade"],
        color="#888888", s=8, alpha=0.6, zorder=3,
        rasterized=True, label="Known exoplanets",
    )

    # Phase 3 — layer 3: detection desert (dashed rectangle)
    d = DESERT
    rect = mpatches.FancyBboxPatch(
        (d["xmin"], d["ymin"]),
        d["xmax"] - d["xmin"],
        d["ymax"] - d["ymin"],
        boxstyle="square,pad=0",
        linewidth=1.4, linestyle="--",
        edgecolor="#CC2936", facecolor="none",
        zorder=4,
    )
    ax.add_patch(rect)
    ax.text(
        5_000, 0.8,
        "Detection Desert\nSmall planets, long periods\nToo faint / too slow to detect",
        color="#CC2936", fontsize=8, ha="center", va="center",
        fontstyle="italic", zorder=5,
        bbox=dict(boxstyle="round,pad=0.4", fc="white",
                  ec="#CC2936", alpha=0.90, lw=0.8),
    )

    # Phase 3 — layer 4: Earth reference marker
    ax.scatter([365.25], [1.0], marker="*", color="blue", s=120, zorder=5)
    ax.annotate(
        "Earth",
        xy=(365.25, 1.0), xytext=(600, 1.7),
        fontsize=8.5, color="blue",
        arrowprops=dict(arrowstyle="->", color="blue", lw=0.9),
        bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="blue",
                  alpha=0.9, lw=0.7),
        zorder=5,
    )

    # Phase 3 — zone annotation text
    for z in ZONES:
        ax.text(
            *z["label_xy"], z["label"],
            color=z["color"], fontsize=8.5,
            ha="center", va="center", fontweight="bold",
            bbox=dict(fc="white", alpha=0.75, pad=2, ec="none"),
            zorder=4,
        )

    ax.grid(True, which="major", alpha=0.18, color="gray", zorder=0)

    return fig


# ── Phase 4: Labels, legend, and export ──────────────────────────────────────

def finish_figure(fig: plt.Figure, df: pd.DataFrame) -> None:
    ax = fig.axes[0]
    n  = len(df)

    ax.set_xlabel("Orbital Period", fontsize=11, labelpad=8)
    ax.set_ylabel("Planet Radius", fontsize=11, labelpad=8)
    ax.set_title(
        "What Our Exoplanet Catalog Can \u2014 and Cannot \u2014 See",
        fontsize=13, fontweight="bold", pad=14,
    )

    # Subtitle
    ax.text(
        0.5, 1.025,
        "Gray dots = known exoplanets.  "
        "Shaded regions = approximate instrument sensitivity windows.",
        transform=ax.transAxes, ha="center", va="bottom",
        fontsize=9, color="#555555",
    )

    # Legend
    legend_handles = [
        mpatches.Patch(fc="#888888", alpha=0.6,
                       label=f"Known exoplanets (n\u2009=\u2009{n:,})"),
        mpatches.Patch(fc="steelblue",      alpha=0.45, label="Transit"),
        mpatches.Patch(fc="darkorange",     alpha=0.45, label="Radial Velocity"),
        mpatches.Patch(fc="mediumseagreen", alpha=0.45, label="Direct Imaging"),
    ]
    ax.legend(handles=legend_handles, loc="upper left",
              fontsize=8.5, framealpha=0.92, edgecolor="#cccccc", borderpad=0.8)

    # Footer disclaimer
    fig.text(
        0.5, 0.01,
        "Sensitivity zones are simplified editorial estimates and do not represent "
        "official instrument specifications.",
        ha="center", fontsize=7, color="#999999", style="italic",
    )

    plt.tight_layout(rect=[0, 0.03, 1, 1])
    fig.savefig(OUT, dpi=150, bbox_inches="tight")
    print(f"Saved -> {OUT}")


# ── Entry point ───────────────────────────────────────────────────────────────

def main() -> None:
    try:
        df = load_data(DATA_PATH)
    except FileNotFoundError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)

    fig = build_figure(df)
    finish_figure(fig, df)


if __name__ == "__main__":
    main()
