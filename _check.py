"""Verification script against PLAN.md criteria (Phases 1–4)."""
import importlib.util, sys, os
from pathlib import Path

PASS = "\u2713"
FAIL = "\u2717"
results = []

def check(label, cond, detail=""):
    sym = PASS if cond else FAIL
    msg = f"  [{sym}] {label}"
    if detail:
        msg += f"  ({detail})"
    print(msg)
    results.append(cond)

# ── load visualize module ─────────────────────────────────────────────────────
HERE = Path(__file__).parent
spec = importlib.util.spec_from_file_location("visualize", HERE / "visualize.py")
viz  = importlib.util.module_from_spec(spec)
spec.loader.exec_module(viz)

import matplotlib
matplotlib.use("Agg")   # headless
import matplotlib.pyplot as plt

# ══════════════════════════════════════════════════════════════════════════════
print("\n── Phase 1: load_data() ─────────────────────────────────────────────")

# FileNotFoundError on bad path
raised = False
try:
    viz.load_data("/nonexistent/path.csv")
except FileNotFoundError:
    raised = True
check("Raises FileNotFoundError for missing file", raised)

# Load the real CSV (suppress print)
import io, contextlib
buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    df = viz.load_data(str(viz.DATA_PATH))
output_line = buf.getvalue().strip()

check("Row count > 1,000 after dropna", len(df) > 1000, f"got {len(df):,}")
check("Exactly two columns: pl_orbper, pl_rade",
      list(df.columns) == ["pl_orbper", "pl_rade"])
check("All values finite and positive", (df > 0).all().all())
check("Console prints row count", "planets" in output_line.lower(), repr(output_line))

# ══════════════════════════════════════════════════════════════════════════════
print("\n── Phase 2: figure scaffolding ──────────────────────────────────────")

fig = viz.build_figure(df)
ax  = fig.axes[0]

check("X-axis is log scale",  ax.get_xscale() == "log")
check("Y-axis is log scale",  ax.get_yscale() == "log")

xlim = ax.get_xlim()
check("X limits ≈ (0.5, 100,000)",
      0.25 <= xlim[0] <= 1.0 and 50_000 <= xlim[1] <= 200_000,
      f"got {xlim}")

ylim = ax.get_ylim()
check("Y limits ≈ (0.3, 30)",
      0.15 <= ylim[0] <= 0.6 and 15 <= ylim[1] <= 60,
      f"got {ylim}")

xtick_labels = [t.get_text() for t in ax.get_xticklabels() if t.get_text()]
check("6 custom X-tick labels present",
      len(xtick_labels) >= 6, str(xtick_labels))
check("X-ticks use plain language (contains 'day' or 'yr')",
      any("day" in l or "yr" in l for l in xtick_labels))

ytick_labels = [t.get_text() for t in ax.get_yticklabels() if t.get_text()]
check("5 custom Y-tick labels present",
      len(ytick_labels) >= 5, str(ytick_labels))
check("Y-ticks use size-class names (contains 'Earth')",
      any("Earth" in l for l in ytick_labels))

# ══════════════════════════════════════════════════════════════════════════════
print("\n── Phase 3: visual layers ───────────────────────────────────────────")

from matplotlib.collections import PathCollection
from matplotlib.patches import FancyBboxPatch, Polygon, Rectangle
import matplotlib as mpl

# Count fill_between zones — exclude PathCollection (scatter) and Line2D
fills = [c for c in ax.collections
         if not isinstance(c, PathCollection)]
check("Exactly 3 sensitivity zone fills", len(fills) == 3, f"got {len(fills)}")

scatter_cols = [c for c in ax.collections if isinstance(c, PathCollection)]
pt_counts = [len(c.get_offsets()) for c in scatter_cols]
check("Scatter has > 1,000 points",
      any(n > 1000 for n in pt_counts), f"counts: {pt_counts}")

# Earth marker at (365.25, 1.0)
earth_found = False
for c in scatter_cols:
    offs = c.get_offsets()
    if any(abs(xy[0] - 365.25) < 1 and abs(xy[1] - 1.0) < 0.1 for xy in offs):
        earth_found = True
check("Earth marker at (365.25, 1.0)", earth_found)

# Dashed border on desert patch or rectangle
dashed_patch = any(
    p.get_linestyle() in ("--", "dashed")
    for p in ax.patches
)
check("Detection desert has dashed border", dashed_patch)

# Text annotations
all_texts = [t.get_text() for t in ax.texts]
check("'Transit' annotation present",        any("Transit" in t for t in all_texts))
check("'Radial Velocity' annotation present", any("Radial Velocity" in t for t in all_texts))
check("'Direct Imaging' annotation present",  any("Direct Imaging" in t for t in all_texts))
check("Detection Desert annotation present",  any("Desert" in t for t in all_texts))

# ══════════════════════════════════════════════════════════════════════════════
print("\n── Phase 4: labels, legend, export ─────────────────────────────────")

viz.finish_figure(fig, df)

check("X-axis label is 'Orbital Period'",
      ax.get_xlabel() == "Orbital Period")
check("Y-axis label is 'Planet Radius'",
      ax.get_ylabel() == "Planet Radius")

title = ax.get_title()
check("Title contains 'Cannot'", "Cannot" in title, repr(title))

# Footer disclaimer
fig_texts = [t.get_text() for t in fig.texts]
check("Footer disclaimer present",
      any("simplified editorial estimates" in t for t in fig_texts))
check("Footer says 'official instrument specifications'",
      any("official instrument specifications" in t for t in fig_texts))

out = HERE / "exoplanet_bias.png"
check("exoplanet_bias.png exists", out.exists())
if out.exists():
    size_kb = out.stat().st_size / 1024
    check("PNG > 100 KB", size_kb > 100, f"{size_kb:.0f} KB")

# No plt.show() in source
src = (HERE / "visualize.py").read_text()
check("No plt.show() in source", "plt.show()" not in src)

plt.close("all")

# ══════════════════════════════════════════════════════════════════════════════
passed = sum(results)
total  = len(results)
print(f"\n{'─'*54}")
print(f"  {passed}/{total} checks passed")
if passed < total:
    print("  Some checks FAILED — see [✗] lines above.")
