"""Editorial "graph-paper" benchmark charts for the hub README.

Framed light panel, square grid, sage-green Linkup bar (with the white Linkup
mark inside it), muted grey competitors, monospace caption + date footer.
One composite image per GTM category (people, company) stacking each signal.
"""
import os
import math
import numpy as np
from PIL import Image
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.offsetbox import OffsetImage, AnnotationBbox

OUT = os.path.dirname(os.path.abspath(__file__))
LOGODIR = os.path.join(OUT, "logos")

# palette sampled from the reference chart
BG = "#F8F8F8"
GREEN = "#7EA995"
GREY_BAR = "#D2D2D2"
GRID = "#E4E4E4"
FRAME = "#C4C4C4"
INK = "#3F3F46"
MUTED = "#9AA0A6"
GREEN_INK = "#4F7D68"
DATE = "2026-07"

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Helvetica Neue", "Arial", "DejaVu Sans"],
    "font.monospace": ["Menlo", "DejaVu Sans Mono", "Courier New"],
    "figure.dpi": 200,
    "savefig.dpi": 200,
})


def white_logo(px=110):
    """White-on-transparent Linkup mark (glyph is white on a black tile)."""
    img = Image.open(os.path.join(LOGODIR, "linkup.png")).convert("RGBA")
    side = max(img.size)
    sq = Image.new("RGBA", (side, side), (0, 0, 0, 0))
    sq.paste(img, ((side - img.width) // 2, (side - img.height) // 2))
    sq = sq.resize((px, px), Image.LANCZOS)
    arr = np.asarray(sq).astype(float) / 255.0
    lum = arr[..., :3].max(axis=-1)          # white glyph -> ~1, black tile -> 0
    out = np.zeros_like(arr)
    out[..., :3] = 1.0                        # paint white
    out[..., 3] = np.clip((lum - 0.35) / 0.5, 0, 1)  # alpha from luminance
    return out


_WLOGO = None


def _nice_bounds(vals):
    lo, hi = min(vals), max(vals)
    if hi <= 10:
        return 0, 10, 2
    step = 10 if (hi - lo) > 35 else 5
    dmin = max(0, math.floor((lo - step * 0.6) / step) * step)
    dmax = math.ceil((hi + step * 0.4) / step) * step
    return dmin, dmax, step


def panel(ax, title, subtitle, data, suffix="", decimals=0, date=None):
    global _WLOGO
    labels = [d[0] for d in data]
    vals = [d[1] for d in data]
    dmin, dmax, step = _nice_bounds(vals)
    span = dmax - dmin
    multiline = any("\n" in l for l in labels)
    band = span * (0.44 if multiline else 0.30)   # footer strip below baseline
    top_pad = span * 0.22
    ax.set_ylim(dmin - band, dmax + top_pad)
    n = len(labels)
    ax.set_xlim(-0.7, n - 0.3)

    # square-ish grid, only within the data region
    for gy in range(int(dmin), int(dmax) + 1, step):
        ax.plot([-0.7, n - 0.3], [gy, gy], color=GRID, lw=0.9, zorder=1)
    ncols = 12
    for gx in np.linspace(-0.7, n - 0.3, ncols + 1):
        ax.plot([gx, gx], [dmin, dmax], color=GRID, lw=0.9, zorder=1)
    ax.plot([-0.7, n - 0.3], [dmin, dmin], color=FRAME, lw=1.1, zorder=2)

    for i, (lab, v) in enumerate(zip(labels, vals)):
        is_lk = "linkup" in lab.lower()
        ax.bar(i, v - dmin, bottom=dmin, width=0.62,
               color=GREEN if is_lk else GREY_BAR, zorder=3,
               edgecolor="none")
        # value above the bar
        ax.text(i, v + span * 0.03, f"{v:.{decimals}f}{suffix}",
                ha="center", va="bottom", zorder=5,
                family="monospace", fontsize=10.5,
                fontweight="bold" if is_lk else "normal",
                color=GREEN_INK if is_lk else INK)
        # engine name below the baseline
        ax.text(i, dmin - band * (0.16 if multiline else 0.30), lab,
                ha="center", va="top", zorder=5,
                fontsize=10.5, fontweight="bold" if is_lk else "normal",
                color=GREEN_INK if is_lk else MUTED)
        # white Linkup mark inside the green bar
        if is_lk:
            if _WLOGO is None:
                _WLOGO = white_logo()
            ab = AnnotationBbox(OffsetImage(_WLOGO, zoom=0.24),
                                (i, dmin + span * 0.16),
                                frameon=False, box_alignment=(0.5, 0.5),
                                zorder=6)
            ax.add_artist(ab)

    # y-axis value labels (monospace, muted)
    for gy in range(int(dmin), int(dmax) + 1, step):
        ax.text(-0.62, gy, str(gy), ha="left", va="center",
                family="monospace", fontsize=8.5, color=MUTED, zorder=4)

    # footer: caption left, date right (inside the frame, below baseline)
    cap_y = dmin - band * (0.90 if multiline else 0.82)
    ax.text(-0.66, cap_y, subtitle, ha="left", va="center",
            family="monospace", fontsize=8.5, color=MUTED, zorder=5)
    ax.text(n - 0.34, cap_y, date or DATE, ha="right", va="center",
            family="monospace", fontsize=8.5, color=MUTED, zorder=5)

    # frame
    for s in ax.spines.values():
        s.set_visible(True)
        s.set_color(FRAME)
        s.set_linewidth(1.1)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_title(title, loc="left", fontsize=12.5, fontweight="bold",
                 color=INK, pad=8)
    ax.set_facecolor(BG)


def hero(fname, header, panels, date=None):
    n = len(panels)
    fig, axes = plt.subplots(n, 1, figsize=(8.0, 3.25 * n + 0.7))
    fig.patch.set_facecolor("white")
    if n == 1:
        axes = [axes]
    fig.text(0.02, 0.995, header, fontsize=15, fontweight="bold",
             color=GREEN_INK, ha="left", va="top")
    for ax, p in zip(axes, panels):
        panel(ax, date=date, **p)
    fig.subplots_adjust(top=1 - 0.9 / (3.25 * n + 0.7),
                        left=0.055, right=0.975, bottom=0.02, hspace=0.42)
    path = os.path.join(OUT, fname)
    fig.savefig(path, facecolor="white", bbox_inches="tight")
    plt.close(fig)
    print("wrote", path)


hero(
    "people_hero.png",
    "People  ·  Linkup leads all 3 signals",
    [
        dict(title="Enrichment — returned the correct person",
             subtitle="LinkedIn profile URL / % correct / n=500",
             data=[("Linkup", 94), ("Perplexity", 64), ("Parallel", 63), ("Exa", 56)],
             suffix="%"),
        dict(title="Richness — pre-meeting brief quality",
             subtitle="Opus-4.8 judge / score out of 100 / n=100",
             data=[("Linkup", 64.8), ("Parallel", 59.8), ("Exa", 55.8), ("Perplexity", 53.1)],
             decimals=1),
        dict(title="Freshness — caught a just-happened job change",
             subtitle="People who changed jobs this month / % caught / n=~50",
             data=[("Linkup", 74), ("Exa", 14), ("Parallel", 11), ("Perplexity", 9)],
             suffix="%"),
    ],
)

hero(
    "company_hero.png",
    "Company  ·  Linkup leads both signals",
    [
        dict(title="Answer quality — on-target sources",
             subtitle="Company research, 100 companies \u00d7 5 sections / % / n=500",
             data=[("Linkup", 80.7), ("Exa", 76.8), ("Perplexity", 73.4), ("Parallel", 71.0)],
             suffix="%", decimals=1),
        dict(title="Funding accuracy — within \u00b125% of Crunchbase",
             subtitle="Total funding from name + HQ + year / % within band / n=93",
             data=[("Linkup", 83), ("Parallel", 74), ("Exa", 72), ("Perplexity", 56)],
             suffix="%"),
    ],
)

hero(
    "finance_hero.png",
    "Finance  \u00b7  Linkup leads both FinSearchComp tiers",
    [
        dict(title="T2 — simple historical lookup",
             subtitle="FinSearchComp T2, best config per provider / % correct / n=119",
             data=[("Linkup", 82.4), ("Parallel", 73.1), ("Perplexity", 72.3),
                   ("Exa", 42.0), ("Tavily", 40.3)],
             suffix="%", decimals=1),
        dict(title="T3 — complex multi-step investigation",
             subtitle="FinSearchComp T3, best config per provider / % correct / n=84",
             data=[("Linkup", 58.3), ("Perplexity", 56.0), ("Parallel", 46.4),
                   ("Tavily", 36.9), ("Exa", 26.2)],
             suffix="%", decimals=1),
    ],
)

hero(
    "places_hero.png",
    "General consumer & places  ·  Linkup leads both",
    [
        dict(title="Places",
             subtitle="Specific physical site / score 0\u201310 / n=112",
             data=[("Linkup", 8.3), ("Perplexity", 5.7), ("Exa", 5.0)],
             decimals=1),
        dict(title="General consumer",
             subtitle="Everything else / score 0\u201310 / n=88",
             data=[("Linkup", 8.5), ("Perplexity", 5.5), ("Exa", 5.4)],
             decimals=1),
    ],
    date="2026-10",
)

hero(
    "legal_hero.png",
    "Legal  \u00b7  Linkup search lifts GPT-5.5 to the top",
    [
        dict(title="Contract redlining — RedlineBench (Crosby)",
             subtitle="Turn-weighted score / same model, prompts & 3-judge grading / n=140",
             data=[("GPT-5.5\n+ Linkup", 58.6), ("GPT-5.5", 50.5),
                   ("Claude\nFable 5", 47.3), ("Gemini 3.5\nFlash", 45.1),
                   ("Claude\nOpus 4.8", 44.4)],
             suffix="%", decimals=1),
    ],
)
