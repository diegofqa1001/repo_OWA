"""
run_spectral_multistart.py — Reproduce la Tabla 2 (vía espectral, US), la
dispersión de óptimos del barrido alpha>1/2 (residual R1) y la figura del
cruce de régimen (R1b). Escribe results/ y figures/.

Uso:  python scripts/run_spectral_multistart.py
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import numpy as np, pandas as pd, matplotlib.pyplot as plt
from src.owa_core import ORNESS_PERFIL, PERFILES, beta_para_orness
from src.spectral_route import optimiza_cartera
from src.backtest import cargar, resumen

CAP, R_STARTS, LOOKBACK, STEP = 0.30, 40, 252, 21
os.makedirs("results", exist_ok=True); os.makedirs("figures", exist_ok=True)

close, volume = cargar("US")
arr = close.values; n = len(close)
print("Universo retenido:", close.shape[1], "activos |", n, "dias")

betas = {p: beta_para_orness(o, LOOKBACK) for p, o in ORNESS_PERFIL.items()}
oos = {p: [] for p in PERFILES}
disp_rows = []
for t in range(LOOKBACK, n - STEP, STEP):
    Rin, Rout = arr[t - LOOKBACK:t], arr[t:t + STEP]
    for p, o in ORNESS_PERFIL.items():
        w, _, disp = optimiza_cartera(Rin, betas[p], cap=CAP, r_starts=R_STARTS)
        ret_oos = pd.DataFrame(Rout).pct_change().dropna().values @ w
        oos[p].append(ret_oos)
        if o > 0.5:
            disp_rows.append({"perfil": p, "orness": o, **disp})

rows = []
for p, o in ORNESS_PERFIL.items():
    r = np.concatenate(oos[p]); m = resumen(r)
    rows.append({"Perfil": p, "orness": o, "beta": round(betas[p], 3),
                 "regimen": "convexo/LP" if o <= 0.5 else "no convexo",
                 **{k: round(v, 3) for k, v in m.items()}})
tab = pd.DataFrame(rows)
tab.to_csv("results/tabla2_desempeno_US.csv", index=False)
print("\n=== Tabla 2 (multi-start) - via espectral US ===")
print(tab.to_string(index=False))

disp = pd.DataFrame(disp_rows).groupby(["perfil", "orness"]).agg(
    V_rango_medio=("V_rango", "mean"), V_std_medio=("V_std", "mean"),
    pct_arranques_optimo=("pct_arranques_optimo", "mean")).reset_index().sort_values("orness")
disp.to_csv("results/dispersion_arranques.csv", index=False)
print("\n=== Dispersion de optimos (alpha>1/2) ===")
print(disp.to_string(index=False))

OKABE = ["#000000", "#E69F00", "#56B4E9", "#009E73", "#F0E442", "#0072B2", "#D55E00", "#CC79A7"]
fig, ax = plt.subplots(figsize=(7, 4.2), dpi=300)
ax.set_facecolor("white"); fig.patch.set_facecolor("white")
ax.plot(tab["orness"], tab["Vol%"], "-o", color=OKABE[5], lw=2, label="Volatilidad OOS (%)")
ax.axvline(0.5, ls="--", color=OKABE[6], lw=1.2, label="Cruce de regimen (orness=1/2)")
for _, row in tab.iterrows():
    ax.annotate(row["Perfil"], (row["orness"], row["Vol%"]), fontsize=7,
                xytext=(0, 5), textcoords="offset points")
ax.set_xlabel("orness del perfil"); ax.set_ylabel("Volatilidad OOS (%)")
ax.set_title("Volatilidad por perfil y cruce de regimen (espectral, US)")
ax.legend(frameon=False, fontsize=8); ax.spines[["top", "right"]].set_visible(False)
plt.tight_layout(); plt.savefig("figures/fig_cruce_regimen.png", dpi=300, bbox_inches="tight")
print("\nGuardado: results/ y figures/fig_cruce_regimen.png")
