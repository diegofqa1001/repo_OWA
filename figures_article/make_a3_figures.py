"""Figures of the article derived from Chapters 4-5 (risk-order inversion): Fig1 to Fig3.

Navy-and-grey palette, white background, sans-serif font, no internal titles, width
<= 174 mm. Categories are also encoded by marker shape and line style, so the figures
read in greyscale.

Run from the repository root after scripts/run_cap5.py and scripts/analyze_cap5.py:
    python figures_article/make_a3_figures.py

Inputs: results/cap5/tabla_5_1_coherencia.csv, results/cap5/tabla_5_2_desempeno.csv.
Outputs: figures_article/Fig1..Fig3 as .png (600 dpi), .tif (600 dpi) and .eps.
"""
from pathlib import Path
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from matplotlib.lines import Line2D

ROOT = Path(__file__).resolve().parent.parent
RES = ROOT / 'results' / 'cap5'
OUT = ROOT / 'figures_article'
OUT.mkdir(exist_ok=True)

for f in fm.findSystemFonts():
    if 'LiberationSans' in f:
        fm.fontManager.addfont(f)
FONT = 'Liberation Sans' if any(x.name == 'Liberation Sans' for x in fm.fontManager.ttflist) else 'DejaVu Sans'
plt.rcParams.update({'font.family': FONT, 'font.size': 8, 'axes.edgecolor': '#9E9E9E',
                     'axes.labelcolor': '#222222', 'xtick.color': '#444444', 'ytick.color': '#444444',
                     'savefig.facecolor': 'white', 'figure.facecolor': 'white', 'hatch.linewidth': 0.6,
                     'ps.fonttype': 42, 'pdf.fonttype': 42})
MM = 1 / 25.4
NAVY, NAVY2, GREY_D, GREY_M = '#1F3A5F', '#4F6D8F', '#3F3F3F', '#8C8C8C'
INK, GRID = '#111111', '#D9D9D9'
PROFILES = ['Guardian', 'Sentinel', 'Pragmatist', 'Analyst', 'Strategist', 'Adventurer', 'Innovator', 'Visionary']


def save(fig, name):
    for ext, kw in (('png', {'dpi': 600}), ('tif', {'dpi': 600, 'pil_kwargs': {'compression': 'tiff_lzw'}}),
                    ('eps', {})):
        fig.savefig(OUT / f'{name}.{ext}', bbox_inches='tight', **kw)
    plt.close(fig)


def style(ax):
    ax.spines[['top', 'right']].set_visible(False)
    ax.grid(axis='y', color=GRID, lw=0.5)
    ax.set_axisbelow(True)


coh = pd.read_csv(RES / 'tabla_5_1_coherencia.csv')
perf = pd.read_csv(RES / 'tabla_5_2_desempeno.csv')
oct_ = coh[coh.anclas == 'octiles']

# Fig. 1: share of coherent windows by route and market
fig, ax = plt.subplots(figsize=(84 * MM, 62 * MM))
mk = {'US': 'United States', 'CO': 'Colombia'}
x = [0, 1]
w = 0.36
for i, (via, col, hatch, lab) in enumerate([('criterios', GREY_M, '///', 'Criteria route'),
                                             ('espectral', NAVY, None, 'Spectral route')]):
    vals = [oct_[(oct_.mercado == m) & (oct_.via == via)].pct_ventanas_rho_pos.item() for m in ['US', 'CO']]
    bars = ax.bar([xi + (i - 0.5) * w for xi in x], vals, w, color=col, edgecolor=INK, lw=0.5,
                  hatch=hatch, label=lab)
    for b, v in zip(bars, vals):
        ax.text(b.get_x() + b.get_width() / 2, v + 1.5, f'{v:.0f}%', ha='center', va='bottom', fontsize=7)
ax.axhline(50, color=GREY_D, lw=0.8, ls='--')
ax.set_xticks(x, [mk['US'], mk['CO']])
ax.set_ylim(0, 120)
ax.set_yticks(range(0, 101, 20))
ax.set_ylabel('Windows with volatility increasing in orness (%)')
ax.legend(frameon=False, loc='upper center', ncol=2, fontsize=7, bbox_to_anchor=(0.5, 1.02))
style(ax)
save(fig, 'Fig1')

# Fig. 3: spectral-route volatility by profile in both markets
sp = perf[(perf.anclas == 'octiles') & (perf.estrategia == 'espectral')]
fig, ax = plt.subplots(figsize=(129 * MM, 66 * MM))
for m, col, mrk, ls in [('US', NAVY, 'o', '-'), ('CO', GREY_D, 's', '--')]:
    d = sp[sp.mercado == m].set_index('perfil').loc[PROFILES]
    ax.plot(d.orness, d['Vol%'], color=col, marker=mrk, ls=ls, lw=1.2, ms=4.5, label=mk[m])
ax.axvline(0.5, color=GREY_M, lw=0.8, ls=':')
ax.text(0.51, 16.0, 'orness = 1/2', fontsize=7, color=GREY_D, va='bottom')
d = sp[sp.mercado == 'US'].set_index('perfil').loc[PROFILES]
ax.set_xticks(d.orness, [f'{p}\n{o:.4g}' for p, o in zip(PROFILES, d.orness)], fontsize=6.5)
ax.set_xlabel('Profile and orness anchor')
ax.set_ylabel('Annualised volatility (%)')
ax.legend(frameon=False, loc='upper left', fontsize=7)
style(ax)
save(fig, 'Fig3')

# Fig. 2: both routes in the United States with benchmarks
us = perf[(perf.anclas == 'octiles') & (perf.mercado == 'US')]
fig, ax = plt.subplots(figsize=(129 * MM, 66 * MM))
for via, col, mrk, ls, lab in [('criterios', GREY_M, 's', '--', 'Criteria route'),
                               ('espectral', NAVY, 'o', '-', 'Spectral route')]:
    d = us[us.estrategia == via].set_index('perfil').loc[PROFILES]
    ax.plot(d.orness, d['Vol%'], color=col, marker=mrk, ls=ls, lw=1.2, ms=4.5, label=lab)
for name, ls in [('1/N', (0, (1, 1.5))), ('Markowitz', (0, (5, 2)))]:
    v = us[us.perfil == name]['Vol%'].item()
    ax.axhline(v, color=GREY_D, lw=0.7, ls=ls)
    ax.text(0.95, v + 0.4, name, fontsize=6.5, color=GREY_D, ha='right', va='bottom')
d = us[us.estrategia == 'espectral'].set_index('perfil').loc[PROFILES]
ax.set_xticks(d.orness, [f'{p}\n{o:.4g}' for p, o in zip(PROFILES, d.orness)], fontsize=6.5)
ax.set_xlim(0, 1)
ax.set_xlabel('Profile and orness anchor')
ax.set_ylabel('Annualised volatility (%)')
ax.legend(frameon=False, loc='upper left', fontsize=7)
style(ax)
save(fig, 'Fig2')
print('Fig1-Fig3 written to', OUT)
