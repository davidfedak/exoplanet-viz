# Exoplanet Detection Bias Visualization

## Ground Rules

1. **State the audience and what they care about before exploring data.**
   Design decisions depend on who's reading. Don't touch columns until
   you know what story matters to the viewer.

2. **Present 2-3 alternatives with trade-offs before committing to any
   design direction.** First ideas aren't best ideas. Compare before
   you converge.

---

## Goal
Show that our exoplanet catalog is shaped by instrument limitations,
not by what actually exists. The gaps in the data are the story.

## Audience
Students in an AI class. Comfortable with data concepts.
Takeaway: selection bias in training data determines what models can learn.

## Hypothesis
Detection methods have narrow sensitivity windows. The resulting catalog
over-represents large, close-in, short-period planets — not because
they're more common, but because they're easier to find.

## Visualization Choice
Scatter plot with annotation overlays.

- All 1,174 planets plotted as neutral (gray) dots
- Shaded regions overlaid showing each detection method's sensitivity zone
- Labeled annotations in empty regions explaining WHY they're empty
- Log-log axes to handle scale range

Rejected alternatives:
- Per-point color by method: cluttered, mixes data and explanation
- Habitability angle: weaker AI-class relevance
- Discovery timeline: interesting but doesn't show bias spatially

## Key Columns
| Column         | Role                        | Notes                          |
|----------------|-----------------------------|--------------------------------|
| pl_rade        | Y-axis (planet radius)      | Earth radii. Log scale.        |
| pl_orbper      | X-axis (orbital period)     | Days. Log scale.               |
| discoverymethod| Shaded region grouping      | May need to group rare methods |

## Columns Excluded
| Column         | Why                                                    |
|----------------|--------------------------------------------------------|
| pl_bmasse      | Correlated with radius, adds clutter not clarity       |
| pl_eqt         | Habitability story, not bias story                     |
| ra, dec        | Spatial position, different story                      |
| st_teff/rad/mass/met | Star properties, secondary to detection bias     |
| sy_dist        | Distance matters but complicates the viz               |
| disc_year      | Timeline story, not spatial bias story                 |

## Text Diagram

    pl_rade (log, Earth radii)
    |
    |  +-----------------------+
    |  | Transit zone          |  <-- shaded region
    |  | (short period, any    |
    |  |  size if large enough)|
    |  +-----------+-----------+
    |              |
    |   +----------+----------+
    |   | Radial velocity zone |  <-- shaded region
    |   | (massive planets,    |
    |   |  short-to-mid period)|
    |   +----------+----------+
    |              |
    |  . . . . . . . . . . . . . . .
    |  .                           .
    |  .   DETECTION DESERT        .  <-- annotation
    |  .   Small planets,          .
    |  .   long orbital periods    .
    |  .   Too faint, too slow     .
    |  .                           .
    |  . . . . . . . . . . . . . . .
    |
    +-------------------------------------> pl_orbper (log, days)

    [ ] = gray dots (all 1,174 planets)
    Shaded regions = method sensitivity zones
    Dotted region = annotated empty space

## Risks
- **Method grouping**: If rare methods (imaging, microlensing) have
  few points, their "zones" may be misleading. May need "Other" bucket.
- **Overlap**: Transit and RV zones overlap for large short-period
  planets. Shaded regions need transparency or distinct boundaries.
- **Log scale readability**: Audience is AI students not astronomers.
  Axis labels need plain-language anchors ("1 day", "1 year", "Earth-sized").
- **Sensitivity zones are approximate**: The shaded regions are
  editorial — simplified representations of complex detection limits.
  Need a note acknowledging this.

## What's Next
This design feeds into Plan + Implement phase:
1. Explore actual data distributions to validate assumptions
2. Determine method groupings from data
3. Define shaded region boundaries from the point clusters
4. Build the visualization
