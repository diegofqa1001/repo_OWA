"""fig_8_1_flujo.py — Figura 8.1 de la tesis: flujo de datos de repo_OWA.
Okabe-Ito, fondo blanco, 300 dpi, rótulos en español. Uso: python scripts/fig_8_1_flujo.py"""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

OK = {"naranja": "#E69F00", "celeste": "#56B4E9", "verde": "#009E73", "amarillo": "#F0E442",
      "azul": "#0072B2", "bermellon": "#D55E00", "purpura": "#CC79A7", "gris": "#999999"}
fig, ax = plt.subplots(figsize=(12, 4.9), facecolor="white")
ax.set_xlim(0, 12); ax.set_ylim(0, 4.9); ax.axis("off")

def caja(x, y, w, h, texto, color, fs=9):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.03,rounding_size=0.08",
                                fc=color, ec="black", lw=1.4))
    ax.text(x + w / 2, y + h / 2, texto, ha="center", va="center", fontsize=fs)

def flecha(x0, y0, x1, y1):
    ax.annotate("", xy=(x1, y1), xytext=(x0, y0), arrowprops=dict(arrowstyle="-|>", lw=1.4, color="black"))

caja(0.1, 2.0, 1.9, 1.2, "Datos (data.py)\ninstantánea 2026-08-31\nprecios y volumen\nEE. UU. · Colombia", "white", 8.5)
caja(0.1, 0.3, 1.9, 1.1, "Régimen (regime.py)\nVIX y EPU (FRED)\n" + r"$\alpha_{\mathrm{ef}}(t)$", OK["amarillo"], 8.5)
caja(2.6, 2.0, 2.0, 1.2, "owa_core\nOWA · RIM · orness\nβ*(α, n) · anclas", OK["celeste"], 9)
caja(5.3, 3.6, 2.3, 1.1, "criteria_route\n(vía de criterios)", OK["naranja"])
caja(5.3, 0.5, 2.3, 1.1, "spectral_route\n(PR-WOWA)\nspectral_lp (verificación)", OK["verde"], 8.5)
caja(8.2, 2.0, 1.85, 1.2, "backtest\nventanas rodantes\ncostos 10 pb\n1/N · Markowitz", "white", 8)
caja(10.3, 2.0, 1.6, 1.2, "inference\nNewey-West\npermutación · DM", OK["purpura"], 8.5)
flecha(2.0, 2.6, 2.6, 2.6)
flecha(2.0, 0.85, 5.3, 0.85)
ax.text(3.65, 0.95, "orness efectivo (sección 8.4)", ha="center", fontsize=7.5)
flecha(4.6, 2.9, 5.3, 4.1); flecha(4.6, 2.3, 5.3, 1.3)
flecha(7.6, 4.1, 8.4, 3.2); flecha(7.6, 1.1, 8.4, 2.0)
flecha(10.05, 2.6, 10.3, 2.6)
out = os.path.join(os.path.dirname(__file__), "..", "figures", "fig_8_1_flujo.png")
fig.savefig(out, dpi=300, facecolor="white", bbox_inches="tight")
print(out)
