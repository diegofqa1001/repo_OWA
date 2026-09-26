"""
fig_iowa.py — Figuras 4.2 y 8.2-8.4 de la tesis y descriptivos que las acompañan.

Lee los resultados versionados (results/iowa y results/cap5, anclas por octiles) y
escribe en figures/ (Okabe-Ito, fondo blanco, 300 dpi, rótulos en español, coma
decimal):
  fig_4_2_espectros_octiles.png   espectros psi de los ocho perfiles (n = 7)
  fig_8_2_orness_efectivo_US.png  índice de estrés y orness efectivo por perfil en
                                  cada rebalanceo (EE. UU.)
  fig_8_3_orness_vol_US.png       orness frente a volatilidad realizada por ventana,
                                  versión estática y adaptativa (EE. UU.)
  fig_8_4_orness_vol_CO.png       ídem (Colombia)
y en results/iowa/descriptivos_figuras.json los estadísticos que la tesis cita al
comentar las figuras.

Uso: python scripts/fig_iowa.py
Licencia: MIT.
"""
import os, sys, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from src.owa_core import ORNESS_OCTILES, PERFILES, beta_para_orness
from src.spectral_route import espectro
from src.regime import S0

BASE = os.path.join(os.path.dirname(__file__), "..")
RES, CAP5, FIG = f"{BASE}/results/iowa", f"{BASE}/results/cap5", f"{BASE}/figures"
os.makedirs(FIG, exist_ok=True)
ES = {"Guardian": "Guardián", "Sentinel": "Centinela", "Pragmatist": "Pragmático", "Analyst": "Analista",
      "Strategist": "Estratega", "Adventurer": "Aventurero", "Innovator": "Innovador", "Visionary": "Visionario"}
OK = {"naranja": "#E69F00", "celeste": "#56B4E9", "verde": "#009E73", "amarillo": "#F0E442",
      "azul": "#0072B2", "bermellon": "#D55E00", "purpura": "#CC79A7", "negro": "#000000"}
COL_PERFIL = dict(zip(PERFILES, [OK["azul"], OK["celeste"], OK["verde"], OK["amarillo"],
                                 OK["naranja"], OK["bermellon"], OK["purpura"], OK["negro"]]))
COL_REG = {"calma": OK["verde"], "normal": OK["celeste"], "estres": OK["naranja"], "crisis": OK["bermellon"]}
ET_REG = {"calma": "Calma", "normal": "Normal", "estres": "Estrés", "crisis": "Crisis"}
coma = FuncFormatter(lambda x, _: f"{x:g}".replace(".", ","))
plt.rcParams.update({"font.family": "DejaVu Sans", "axes.facecolor": "white", "figure.facecolor": "white",
                     "savefig.facecolor": "white", "axes.spines.top": False, "axes.spines.right": False})


def guardar(fig, nombre):
    fig.savefig(f"{FIG}/{nombre}", dpi=300, facecolor="white", bbox_inches="tight")
    plt.close(fig)


# ---------------------------------------------------------------- Figura 4.2
# Espectro psi_j = (j/n)^beta - ((j-1)/n)^beta del cuantificador RIM para n = 7
# posiciones ordenadas (j = 1 mejor, j = 7 peor), con beta = beta*(alpha, 7).
n = 7
fig, ax = plt.subplots(figsize=(7.4, 4.4))
j = np.arange(1, n + 1)
for p in PERFILES:
    b = beta_para_orness(ORNESS_OCTILES[p], n)
    ax.plot(j, espectro(b, n), color=COL_PERFIL[p], lw=1.6, marker="o", ms=3.5,
            label=f"{ES[p]} ({ORNESS_OCTILES[p]:.4f}".rstrip("0").replace(".", ",") + ")")
ax.axhline(1.0 / n, color="#999999", ls="--", lw=0.9)
ax.text(7.05, 1.0 / n, "1/n", fontsize=7, color="#555555", va="center")
ax.set_xticks(j, ["1\n(mejor)", "2", "3", "4", "5", "6", "7\n(peor)"])
ax.set_xlabel(r"Posición $j$ del resultado ordenado")
ax.set_ylabel(r"Peso $\psi_j$")
ax.yaxis.set_major_formatter(coma)
ax.legend(title="Perfil (orness)", frameon=False, fontsize=7, title_fontsize=8, ncol=2, loc="upper center")
guardar(fig, "fig_4_2_espectros_octiles.png")

# ---------------------------------------------------------------- Figuras 8.2-8.4
desc = {}
for mk in ("US", "CO"):
    A = pd.read_csv(f"{RES}/ventanas_{mk}.csv")
    E = pd.read_csv(f"{RES}/estres_{mk}.csv", index_col=0, parse_dates=True)
    Sx = pd.read_csv(f"{CAP5}/ventanas_{mk}_octiles.csv"); Sx = Sx[Sx.via == "espectral"]
    M = A.merge(Sx[["perfil", "t", "vol"]], on=["perfil", "t"], suffixes=("_ad", "_es"))
    act = M[M.activacion > 0]
    disp = M.groupby("t").agg(activa=("activacion", lambda x: bool(x.iloc[0] > 0)),
                              sd_es=("vol_es", "std"), sd_ad=("vol_ad", "std"),
                              rango_orness_ef=("orness_efectivo", lambda x: float(x.max() - x.min())))
    no_guard = act[act.perfil != "Guardian"]
    desc[mk] = {
        "n_ventanas": int(M.t.nunique()), "n_activas": int(act.t.nunique()),
        "regimen_ventanas_activas": act.drop_duplicates("t")["regimen"].value_counts().to_dict(),
        "activacion_max": float(A.activacion.max()),
        "orness_efectivo_min_por_perfil": {p: float(A[A.perfil == p].orness_efectivo.min()) for p in PERFILES},
        "orness_efectivo_activas_min_max_sin_guardian": [float(no_guard.orness_efectivo.min()),
                                                           float(no_guard.orness_efectivo.max())],
        "rango_orness_efectivo_medio_activas": float(disp[disp.activa].rango_orness_ef.mean()),
        "rango_orness_nominal": float(max(ORNESS_OCTILES.values()) - min(ORNESS_OCTILES.values())),
        "sd_transversal_vol_activas_estatica": float(disp[disp.activa].sd_es.mean()),
        "sd_transversal_vol_activas_adaptativa": float(disp[disp.activa].sd_ad.mean()),
        "vol_media_activas_estatica_pct": 100 * float(act.vol_es.mean()),
        "vol_media_activas_adaptativa_pct": 100 * float(act.vol_ad.mean()),
    }

    # Figura 8.2 (solo EE. UU.): índice de estrés diario y orness efectivo en cada rebalanceo
    if mk == "US":
        fig, (a1, a2) = plt.subplots(2, 1, figsize=(7.6, 5.6), sharex=True,
                                     gridspec_kw={"height_ratios": [1, 2.1]})
        E2 = E.loc[pd.to_datetime(A.fecha.min()):pd.to_datetime(A.fecha.max()) + pd.Timedelta(days=31)]
        a1.fill_between(E2.index, 0, E2["s"], color=OK["celeste"], alpha=0.45, lw=0)
        a1.plot(E2.index, E2["s"], color=OK["azul"], lw=0.6)
        a1.axhline(S0, color=OK["bermellon"], ls="--", lw=1)
        a1.text(1.0, S0 + 0.02, "umbral s₀ = 0,55", fontsize=7, color=OK["bermellon"], transform=a1.get_yaxis_transform(), ha="right", va="bottom", bbox=dict(fc="white", ec="none", pad=1))
        a1.set_ylabel("Índice de estrés s(t)"); a1.set_ylim(0.2, 1.0); a1.yaxis.set_major_formatter(coma)
        for p in PERFILES:
            g = A[A.perfil == p].sort_values("t")
            f = pd.to_datetime(g["fecha"])
            a2.step(f, g["orness_efectivo"], where="post", color=COL_PERFIL[p], lw=1.3, label=ES[p])
            a2.hlines(ORNESS_OCTILES[p], f.min(), f.max(), colors=COL_PERFIL[p], linestyles=":", lw=0.7)
        a2.axhline(0.12, color="#999999", ls="--", lw=0.8)
        a2.text(f.min(), 0.085, r"piso $\alpha_{\mathrm{mín}}$ = 0,12", fontsize=7, color="#555555")
        a2.set_ylabel("Orness en el rebalanceo"); a2.set_ylim(0, 1); a2.yaxis.set_major_formatter(coma)
        a2.legend(frameon=False, fontsize=7, ncol=4, loc="upper center", bbox_to_anchor=(0.5, -0.1))
        guardar(fig, "fig_8_2_orness_efectivo_US.png")

    # Figuras 8.3 / 8.4: orness frente a volatilidad realizada por ventana
    fig, axs = plt.subplots(1, 2, figsize=(8.2, 4.2), sharey=True)
    rng = np.random.default_rng(42)
    for ax, (tit, xcol, ycol) in zip(axs, (("Versión estática", "orness", "vol_es"),
                                           ("Versión adaptativa", "orness_efectivo", "vol_ad"))):
        for reg in ("calma", "normal", "estres", "crisis"):
            g = M[M.regimen == reg]
            x = g[xcol].values + (rng.uniform(-0.012, 0.012, len(g)) if xcol == "orness" else 0)
            ax.scatter(x, 100 * g[ycol].values, s=7, alpha=0.55, color=COL_REG[reg], label=ET_REG[reg], lw=0)
        ax.set_title(tit, fontsize=10); ax.set_xlim(0, 1)
        ax.set_xlabel("Orness nominal" if xcol == "orness" else "Orness efectivo")
        ax.xaxis.set_major_formatter(coma); ax.yaxis.set_major_formatter(coma)
    axs[0].set_ylabel("Volatilidad realizada anualizada en la ventana (%)")
    axs[1].legend(title="Régimen en el rebalanceo", frameon=False, fontsize=7, title_fontsize=8, markerscale=2)
    guardar(fig, f"fig_8_{'3' if mk == 'US' else '4'}_orness_vol_{mk}.png")

json.dump(desc, open(f"{RES}/descriptivos_figuras.json", "w"), indent=1, ensure_ascii=False)
print(json.dumps(desc, indent=1, ensure_ascii=False))
print("figuras guardadas en", FIG)
