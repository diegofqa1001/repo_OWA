"""Graphical abstract of the article on risk-order inversion (Applied Soft Computing).

Left: the criteria route (orness applied to each asset's criteria). Right: the spectral route
(orness applied to the ordered outcomes of the portfolio). Bottom: realised volatility by profile
in the United States under both routes (octile anchors, net of costs).
Input: results/cap5/tabla_5_2_desempeno.csv. Output: figures_article/Graphical_abstract.{png,tif,pdf}
Run from the repository root: python figures_article/make_a3_graphical_abstract.py
"""
from pathlib import Path

import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
import matplotlib.font_manager as fm

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "figures_article"
for f in fm.findSystemFonts():
    if "LiberationSans" in f:
        fm.fontManager.addfont(f)
FONT = "Liberation Sans" if any(x.name == "Liberation Sans" for x in fm.fontManager.ttflist) else "DejaVu Sans"
plt.rcParams.update({"font.family": FONT, "font.size": 9, "savefig.facecolor": "white",
                     "pdf.fonttype": 42})
NAVY, GREY_D, GREY_M, GREY_L, FILL = "#1F3A5F", "#3F3F3F", "#8C8C8C", "#EFEFEF", "#E3E9F1"
PROFILES = ["Guardian", "Sentinel", "Pragmatist", "Analyst", "Strategist", "Adventurer", "Innovator", "Visionary"]

perf = pd.read_csv(ROOT / "results" / "cap5" / "tabla_5_2_desempeno.csv")
us = perf[(perf.mercado == "US") & (perf.anclas == "octiles")]

fig = plt.figure(figsize=(13.3 / 2.54 * 2, 6.6 / 2.54 * 2))
ax = fig.add_axes([0, 0.40, 1, 0.60]); ax.set_xlim(0, 100); ax.set_ylim(0, 40); ax.axis("off")


def box(x, w, title, lines, fc, ec, tc):
    ax.add_patch(FancyBboxPatch((x, 11), w, 25, boxstyle="round,pad=0.6,rounding_size=2", fc=fc, ec=ec, lw=1))
    ax.text(x + w / 2, 33.5, title, ha="center", va="top", weight="bold", color=tc, fontsize=10.5)
    ax.text(x + w / 2, 27, lines, ha="center", va="top", color="#222222", fontsize=9, linespacing=1.45)


box(2, 45, "Criteria route",
    "Orness aggregates the criteria of each asset\n= Choquet integral, symmetric capacity\n"
    "blind to the covariance of returns\n\nConservative profiles can select riskier assets\n"
    "Risk-order inversion: ρ = −0.93 (US), −0.86 (CO)", GREY_L, GREY_D, GREY_D)
box(53, 45, "Spectral route (PR-WOWA)",
    "Same orness on the ordered portfolio outcomes\n= spectral risk measure, coherent for\n"
    "cautious profiles, LP-solvable, nests CVaR\n\nRisk positively rank-correlated with orness\nin "
    "99% (US) and 92% (CO) of out-of-sample windows", FILL, NAVY, NAVY)
ax.annotate("", xy=(52.3, 22), xytext=(47.7, 22), arrowprops=dict(arrowstyle="-|>", color=NAVY, lw=1.4))
ax.text(50, 24.5, "same\norness", ha="center", va="bottom", fontsize=7.5, color=NAVY)

a2 = fig.add_axes([0.08, 0.08, 0.88, 0.36])
for route, color, ls, mk, lab in (("criterios", GREY_M, "--", "o", "Criteria route"),
                                  ("espectral", NAVY, "-", "s", "Spectral route")):
    d = us[us.estrategia == route].set_index("perfil").reindex(PROFILES)
    a2.plot(range(8), d["Vol%"], color=color, ls=ls, marker=mk, ms=4, lw=1.4, label=lab)
a2.set_xticks(range(8), PROFILES, fontsize=8)
a2.set_ylabel("Volatility (%)", fontsize=8.5)
a2.spines[["top", "right"]].set_visible(False)
a2.grid(axis="y", color="#D9D9D9", lw=0.5)
a2.legend(frameon=False, fontsize=8, loc="upper left")
a2.set_title("United States, 2016–2024, net of costs: same profiles, same prices, opposite risk order",
             fontsize=8.5, color=GREY_D, loc="left")
for ext, kw in (("png", {"dpi": 300}), ("tif", {"dpi": 300, "pil_kwargs": {"compression": "tiff_lzw"}}), ("pdf", {})):
    fig.savefig(OUT / f"Graphical_abstract.{ext}", bbox_inches="tight", **kw)
print("written")
