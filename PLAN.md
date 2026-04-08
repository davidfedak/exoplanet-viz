# PLAN.md — Exoplanet Detection Bias Visualization

## 1. Overview

This script reads a NASA Exoplanet Archive CSV, filters it to two columns (orbital period and planet radius), and produces a single annotated scatter plot saved as `exoplanet_bias.png`. The visualization overlays approximate detection-sensitivity zones on a log-log scatter of all known exoplanets to make the argument that the shape of the catalog reflects instrument limitations, not the true distribution of planets. The intended audience is AI students learning about selection bias in training data.

---

## 2. Phases

### Phase 1: Data Loading and Validation

**Goal:** Read the CSV, isolate the two required columns, and produce a clean DataFrame ready for plotting. Fail loudly if the file or columns are missing.

### Phase 2: Figure Scaffolding

**Goal:** Initialize the matplotlib figure and axes with log-log scaling, fixed axis limits that encompass both the data and all annotation regions, and human-readable tick labels on both axes.

### Phase 3: Visual Layers

**Goal:** Draw all data-ink elements in the correct stacking order: sensitivity zone fills first, then the scatter of planet points, then the detection desert rectangle, then the Earth reference marker, then annotation text.

### Phase 4: Labels, Legend, and Export

**Goal:** Apply all textual finishing — axis labels, plot title, subtitle, legend, and footer disclaimer — then save the figure to disk at publication resolution.

---

## 3. Deliverables

### Phase 1 Deliverables

- Function `load_data(path: str) -> pd.DataFrame` that:
  - Reads the CSV (handle possible comment rows with `comment="#"` or `skiprows` as needed)
  - Selects only `pl_orbper` and `pl_rade`
  - Drops any row where either column is NaN
  - Returns the cleaned DataFrame
- Console print of row count after cleaning (e.g., `"Loaded 1,147 planets after dropping missing values."`)

### Phase 2 Deliverables

- A `matplotlib.figure.Figure` object and a single `Axes` object (`fig, ax`)
- Both axes set to log scale (`ax.set_xscale("log")`, `ax.set_yscale("log")`)
- X-axis limits: `(0.5, 100_000)` days
- Y-axis limits: `(0.3, 30)` Earth radii
- X-axis major ticks at `[1, 10, 100, 365.25, 3652.5, 36525]` with labels `["1 day", "10 days", "100 days", "1 yr", "10 yr", "100 yr"]`
- Y-axis major ticks at `[1, 2, 4, 11.2, 22.4]` with labels `["1× Earth", "2× Earth", "4× super-Earth", "11× Neptune-size", "22× Jupiter-size"]`
- Minor ticks suppressed on both axes for readability

### Phase 3 Deliverables

- Three filled sensitivity zones drawn with `ax.fill_between` or `ax.axhspan`/`ax.fill` (see Zone Definitions table in Section 6); each zone uses a distinct color at alpha ≈ 0.15–0.20
- Scatter plot of all cleaned planet rows as gray circles (`color="#888888"`, `s=8`, `alpha=0.6`, `zorder=3`)
- Detection desert: a dashed-border rectangle in the bottom-right quadrant (approximately x: 500–50,000 days, y: 0.3–2.5 Earth radii), filled with a very light gray or transparent interior, border `linestyle="--"`, `edgecolor` distinct from zone fills
- Earth reference marker: a single point plotted at `(365.25, 1.0)` with a star marker (`marker="*"`, `color="blue"`, `s=120`, `zorder=5`) plus a text annotation offset slightly up-right reading `"Earth"`
- Short annotation strings inside each zone naming the method (e.g., `"Transit"`, `"Radial Velocity"`, `"Direct Imaging"`)
- A multi-line annotation inside the detection desert box explaining why it is empty (e.g., `"Detection Desert\nSmall planets, long periods\nToo faint / too slow to detect"`)

### Phase 4 Deliverables

- X-axis label: `"Orbital Period"` (plain language, no units in the label itself — units conveyed by tick labels)
- Y-axis label: `"Planet Radius"` (same rationale)
- Title: `"What Our Exoplanet Catalog Can — and Cannot — See"`
- Subtitle (via `ax.text` near top of axes or `fig.suptitle`): `"Gray dots = known exoplanets. Shaded regions = approximate instrument sensitivity windows."`
- Legend entries for each named zone and the scatter series, placed inside the axes at a non-overlapping position
- Footer text via `fig.text(0.5, 0.01, "...", ha="center", fontsize=7)` containing the disclaimer: `"Sensitivity zones are simplified editorial estimates and do not represent official instrument specifications."`
- Output file `exoplanet_bias.png` saved with `fig.savefig("exoplanet_bias.png", dpi=150, bbox_inches="tight")`
- No call to `plt.show()`

---

## 4. Verification Criteria

### Phase 1 Verification

- `load_data()` raises a clear `FileNotFoundError` (or equivalent) if the CSV path does not exist — do not silently return an empty DataFrame
- After `dropna`, the returned DataFrame has **more than 1,000 rows** (the raw catalog has ~1,174 planets; a count below 500 indicates a column-name mismatch or wrong file)
- The DataFrame contains exactly two columns: `pl_orbper` and `pl_rade`
- All values in both columns are finite and positive (no zeros, no negatives, no infinities) — assert `(df > 0).all().all()`
- Console output prints the exact row count

### Phase 2 Verification

- `ax.get_xscale()` returns `"log"` and `ax.get_yscale()` returns `"log"`
- `ax.get_xlim()` is approximately `(0.5, 100_000)` — within a factor of 2
- `ax.get_ylim()` is approximately `(0.3, 30)` — within a factor of 2
- The six custom X-tick labels are present and readable
- The five custom Y-tick labels are present
- The figure renders without any `UserWarning` about missing ticks or out-of-range values

### Phase 3 Verification

- Exactly three zone fills are present in the axes
- The scatter collection contains more than 1,000 points
- The Earth marker is visible at data coordinates `(365.25, 1.0)`
- The detection desert rectangle appears in the bottom-right region and uses a dashed border style
- All zone annotation strings (`"Transit"`, `"Radial Velocity"`, `"Direct Imaging"`) appear as text within the axes
- The detection desert annotation string contains the word `"Desert"`
- No `OverflowError` or blank axes when the script is run end-to-end

### Phase 4 Verification

- `fig.savefig(...)` completes without error
- `exoplanet_bias.png` exists in the script directory after execution
- The PNG file size is greater than 100 KB (a near-zero file indicates a blank figure)
- The saved image shows: gray scatter points, colored shaded zones, the Earth star marker, the dashed desert box, tick labels in plain language, and footer text at the bottom
- No `plt.show()` call exists anywhere in the script
- The title string `"What Our Exoplanet Catalog Can — and Cannot — See"` is present in the figure

---

## 5. Implementation Constraints

- Use only `pl_rade` and `pl_orbper` columns. Drop every row where either column is NaN before any plotting or validation step.
- Both axes must use log scale. Do not transform the data manually — use `ax.set_xscale("log")` and `ax.set_yscale("log")`.
- Sensitivity zones must be drawn using `fill_between`, `fill`, or a filled `Polygon`/`Rectangle` patch. Do not use background images or colormaps for zones.
- Exactly three named zones must be rendered: `Transit`, `Radial Velocity`, and `Direct Imaging`. Any rare methods (microlensing, astrometry, etc.) appear only as gray scatter points — no dedicated zone.
- The detection desert must be marked with a dashed-border rectangle. Use `linestyle="--"` on the rectangle edge. Interior may be transparent or very lightly shaded.
- The Earth reference marker must be plotted at exactly `(365.25, 1.0)` in data coordinates with a star marker and a text annotation reading `"Earth"`.
- X-axis tick labels must use plain language: `"1 day"`, `"10 days"`, `"100 days"`, `"1 yr"`, `"10 yr"`, `"100 yr"`. Do not show raw numeric values on the x-axis.
- Y-axis tick labels must use plain language approximating size classes: `"1× Earth"`, `"2× Earth"`, `"4× super-Earth"`, `"11× Neptune-size"`, `"22× Jupiter-size"`. Do not show raw numeric values on the y-axis.
- Footer disclaimer must read (exactly or nearly): `"Sensitivity zones are simplified editorial estimates and do not represent official instrument specifications."` — placed at the bottom of the figure outside the axes area.
- Output file must be saved as `exoplanet_bias.png` in the same directory as `visualize.py`. Derive the script directory with `pathlib.Path(__file__).parent`.
- Do not call `plt.show()`. The script must be safe to run in headless environments.
- Input CSV path: `../Downloads/exoplanets.csv` relative to the script. Define it as a named constant at the top of the file (e.g., `DATA_PATH`).
- Single file (`visualize.py`). Dependencies: `pandas`, `matplotlib`, Python standard library only.

---

## 6. Zone Definitions

All coordinates are in **data units**: orbital period in **days** (x-axis) and planet radius in **Earth radii** (y-axis). These are editorial approximations — not scientifically authoritative.

| Zone Name       | x min (days) | x max (days) | y min (Earth radii) | y max (Earth radii) | Fill Color (suggested) | Rationale |
|-----------------|--------------|--------------|---------------------|---------------------|------------------------|-----------|
| Transit         | 0.5          | 100          | 1.0                 | 25                  | Steelblue              | Requires multiple observed transits; favors short periods and large radii |
| Radial Velocity | 0.5          | 3000         | 4.0                 | 25                  | Darkorange             | RV signal scales with mass; most detections are massive planets within a few AU |
| Direct Imaging  | 1000         | 100000       | 7.0                 | 25                  | Mediumseagreen         | Requires angular separation; favors wide orbits and large bright planets |

**Detection Desert** (dashed rectangle, not a fill zone):
- x: 500–50,000 days
- y: 0.3–2.5 Earth radii
- Bottom-right quadrant: small long-period planets we cannot yet detect

**Overlap note:** Transit and RV zones overlap in the upper-left (large short-period planets). Intentional — use `alpha ≈ 0.15` so both remain visible.
