"""Figura 4.1 — Ilustración del Contraejemplo 1 (inversión conductual), rótulos en español y coma decimal.

Dos activos con criterios c = (rentabilidad, estabilidad): A = (0,90; 0,50), B = (0,40; 1,00).
Conservador: orness → 0 (criterio mínimo); agresivo: orness → 1 (criterio máximo). Okabe-Ito, 300 dpi.
"""
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

A, B = (0.90, 0.50), (0.40, 1.00)
cons = [min(A), min(B)]
agr = [max(A), max(B)]
c = lambda v, d=2: f'{v:.{d}f}'.replace('.', ',')
plt.rcParams.update({'font.family': 'DejaVu Sans', 'axes.spines.top': False, 'axes.spines.right': False})
fig, ax = plt.subplots(figsize=(8, 4.4), dpi=300)
x = [0, 1]; w = 0.35
b1 = ax.bar([i - w / 2 for i in x], cons, w, color='#0072B2', edgecolor='black',
            label='Conservador (orness→0, criterio mínimo)')
b2 = ax.bar([i + w / 2 for i in x], agr, w, color='#D55E00', edgecolor='black',
            label='Agresivo (orness→1, criterio máximo)')
for bars in (b1, b2):
    for r in bars:
        ax.text(r.get_x() + r.get_width() / 2, r.get_height() + 0.015, c(r.get_height()), ha='center', va='bottom', fontsize=10)
ax.annotate('El conservador prefiere A\n(el más volátil): inversión', xy=(-w / 2, cons[0] + 0.01), xytext=(0.2, 1.05),
            color='#0072B2', fontsize=10, arrowprops=dict(arrowstyle='->', color='#0072B2'))
ax.set_xticks(x)
ax.set_xticklabels([f'Activo A\n(crecimiento volátil)\nc = ({c(A[0])}; {c(A[1])})',
                    f'Activo B\n(defensivo)\nc = ({c(B[0])}; {c(B[1])})'])
ax.set_ylim(0, 1.15)
ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: c(v, 1)))
ax.set_ylabel('Puntaje multicriterio $s_i$')
ax.set_title('Contraejemplo 1: aplicar el orness a los criterios invierte al inversor', fontsize=11)
ax.legend(loc='center', frameon=True, fontsize=9)
os.makedirs('figures', exist_ok=True)
fig.tight_layout(); fig.savefig('figures/fig_4_1_contraejemplo.png', dpi=300, facecolor='white')
print('OK figures/fig_4_1_contraejemplo.png')
