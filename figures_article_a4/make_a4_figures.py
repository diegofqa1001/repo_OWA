"""Figures 1-2 of the article on regime-induced orness (A4). Fig. 3 is produced in validacion-oe4.

Navy-and-grey palette, white background, sans-serif font, no internal titles, width <= 174 mm.
Profiles are also distinguished by line style and marker, so the figures read in greyscale.

Run from the repository root after scripts/run_iowa.py, scripts/analyze_iowa.py and
scripts/analyze_a4_compression.py:
    python figures_article_a4/make_a4_figures.py
Inputs: results/iowa/ventanas_US.csv, results/iowa/estres_US.csv, results/iowa/compresion_a4.json.
Outputs: figures_article_a4/Fig1, Fig2 as .png and .tif (600 dpi) and .eps.
"""
from pathlib import Path
import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

ROOT = Path(__file__).resolve().parent.parent
RES = ROOT / 'results' / 'iowa'
OUT = ROOT / 'figures_article_a4'
for f in fm.findSystemFonts():
    if 'LiberationSans' in f:
        fm.fontManager.addfont(f)
FONT = 'Liberation Sans' if any(x.name == 'Liberation Sans' for x in fm.fontManager.ttflist) else 'DejaVu Sans'
plt.rcParams.update({'font.family': FONT, 'font.size': 8, 'axes.edgecolor': '#9E9E9E',
                     'axes.labelcolor': '#222222', 'xtick.color': '#444444', 'ytick.color': '#444444',
                     'savefig.facecolor': 'white', 'figure.facecolor': 'white', 'hatch.linewidth': 0.6,
                     'ps.fonttype': 42, 'pdf.fonttype': 42})
MM = 1 / 25.4
NAVY, GREY_D, GREY_M, INK, GRID = '#1F3A5F', '#3F3F3F', '#8C8C8C', '#111111', '#D9D9D9'
PROFILES = ['Guardian', 'Sentinel', 'Pragmatist', 'Analyst', 'Strategist', 'Adventurer', 'Innovator', 'Visionary']
SHADES = ['#9E9E9E', '#7A7A7A', '#565656', '#2E2E2E', '#8FA2BA', '#5F7899', '#3A5577', '#1F3A5F']
STYLES = ['-', '--', '-.', ':', '-', '--', '-.', ':']


def save(fig, name):
    for ext, kw in (('png', {'dpi': 600}), ('tif', {'dpi': 600, 'pil_kwargs': {'compression': 'tiff_lzw'}}),
                    ('eps', {})):
        fig.savefig(OUT / f'{name}.{ext}', bbox_inches='tight', **kw)
    plt.close(fig)


def style(ax):
    ax.spines[['top', 'right']].set_visible(False)
    ax.grid(axis='y', color=GRID, lw=0.5)
    ax.set_axisbelow(True)


# Fig. 1: stress index and effective orness, United States
V = pd.read_csv(RES / 'ventanas_US.csv', parse_dates=['fecha'])
E = pd.read_csv(RES / 'estres_US.csv', index_col=0, parse_dates=True)
E = E[(E.index >= V.fecha.min()) & (E.index <= V.fecha.max())]
fig, (a1, a2) = plt.subplots(2, 1, figsize=(174 * MM, 110 * MM), sharex=True,
                             gridspec_kw={'height_ratios': [1, 2.1], 'hspace': 0.08})
a1.plot(E.index, E['s'], color=GREY_D, lw=0.6)
a1.axhline(0.55, color=NAVY, lw=0.9, ls='--')
a1.text(E.index[-1], 0.04, 'dashed line: activation threshold 0.55', color=NAVY, fontsize=6.5, ha='right', va='bottom')
a1.set_ylabel('Stress index s(t)')
a1.set_ylim(0, 1)
style(a1)
for p, c, ls in zip(PROFILES, SHADES, STYLES):
    g = V[V.perfil == p].sort_values('fecha')
    a2.step(g.fecha, g.orness_efectivo, where='post', color=c, lw=1.0, ls=ls, label=p)
    a2.axhline(g.orness.iloc[0], color=c, lw=0.4, ls=':')
a2.axhline(0.12, color=GREY_M, lw=0.8, ls=(0, (6, 3)))
a2.text(E.index[-1], 0.125, 'floor 0.12', color=GREY_D, fontsize=6.5, ha='right', va='bottom')
a2.set_ylabel('Effective orness')
a2.set_ylim(0, 1)
a2.legend(frameon=False, ncol=4, fontsize=6.5, loc='upper center', bbox_to_anchor=(0.5, -0.12))
style(a2)
save(fig, 'Fig1')

# Fig. 2: cross-section of the window of highest activation, United States
C = json.load(open(RES / 'compresion_a4.json'))['US']['ventana_max_activacion']
x = np.arange(len(PROFILES)); w = 0.38
fig, ax = plt.subplots(figsize=(129 * MM, 64 * MM))
st = [C['vol_estatica_pct'][p] for p in PROFILES]
ad = [C['vol_adaptativa_pct'][p] for p in PROFILES]
ax.bar(x - w / 2, st, w, color=GREY_M, edgecolor=INK, lw=0.5, hatch='///', label='Static')
ax.bar(x + w / 2, ad, w, color=NAVY, edgecolor=INK, lw=0.5, label='Regime-induced')
ax.set_xticks(x, [f"{p}\n{C['orness_efectivo'][p]:.4g}" for p in PROFILES], fontsize=6.5)
ax.set_xlabel('Profile and effective orness on 6 April 2020')
ax.set_ylabel('Annualised realised volatility (%)')
ax.set_ylim(0, 50)
ax.legend(frameon=False, loc='upper left', fontsize=7)
style(ax)
save(fig, 'Fig2')
print('Fig1-Fig2 written to', OUT)
