"""
analyze_iowa.py — Pruebas del componente adaptativo inducido por régimen (tesis §8.4).

Compara, ventana a ventana, la versión adaptativa (results/iowa) con la estática
(vía espectral del Capítulo 5, anclas por octiles, results/cap5). La unidad de
inferencia es la VENTANA: para cada una se promedia la diferencia entre perfiles,
de modo que las ocho carteras de una misma fecha no se tratan como observaciones
independientes.

Pruebas (ventanas con estrés activo, a(t) > 0, y todas las ventanas):
  A. Coherencia: rho de Spearman(orness base, volatilidad realizada) por ventana,
     adaptativa frente a estática; diferencia media con t de Newey-West.
  B. Riesgo de nivel: d_t = media entre perfiles de (vol_estática - vol_adaptativa),
     y lo mismo para la magnitud de la caída máxima; Diebold-Mariano-HLN unilateral
     (H1: la adaptativa reduce el riesgo).
Escribe results/iowa/resumen_<mk>.json, tabla_iowa.csv y figures/fig_8_x_*.png.
"""
import os, sys, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import numpy as np, pandas as pd
from scipy.stats import spearmanr
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from src.owa_core import ORNESS_OCTILES, PERFILES
from src.inference import nw_tstat, diebold_mariano

BASE = os.path.join(os.path.dirname(__file__), "..")
RES, CAP5, FIG = f"{BASE}/results/iowa", f"{BASE}/results/cap5", f"{BASE}/figures"
ES = {"Guardian": "Guardián", "Sentinel": "Centinela", "Pragmatist": "Pragmático", "Analyst": "Analista",
      "Strategist": "Estratega", "Adventurer": "Aventurero", "Innovator": "Innovador", "Visionary": "Visionario"}
OK = ["#E69F00", "#56B4E9", "#009E73", "#F0E442", "#0072B2", "#D55E00", "#CC79A7", "#000000"]
coma = FuncFormatter(lambda x, _: f"{x:g}".replace(".", ","))
orn = np.array([ORNESS_OCTILES[p] for p in PERFILES])
filas = []

for mk in ("US", "CO"):
    A = pd.read_csv(f"{RES}/ventanas_{mk}.csv")
    S = pd.read_csv(f"{CAP5}/ventanas_{mk}_octiles.csv"); S = S[S.via == "espectral"]
    m = A.merge(S[["perfil", "t", "vol", "dd", "ret"]], on=["perfil", "t"], suffixes=("_ad", "_es"))
    por_t = []
    for t, g in m.groupby("t"):
        g = g.set_index("perfil").loc[PERFILES]
        por_t.append({"t": t, "fecha": g["fecha"].iloc[0], "activacion": g["activacion"].iloc[0], "s": g["s"].iloc[0],
                      "regimen": g["regimen"].iloc[0],
                      "rho_ad": spearmanr(orn, g["vol_ad"])[0], "rho_es": spearmanr(orn, g["vol_es"])[0],
                      "dvol": float((g["vol_es"] - g["vol_ad"]).mean()),
                      "ddd": float((-g["dd_es"] + g["dd_ad"]).mean()),
                      "dret": float((g["ret_es"] - g["ret_ad"]).mean()),
                      "red_orness": float((g["orness"] - g["orness_efectivo"]).mean())})
    T = pd.DataFrame(por_t)
    T.to_csv(f"{RES}/por_ventana_{mk}.csv", index=False)
    res = {"mercado": mk, "n_ventanas": int(len(T)), "n_activas": int((T.activacion > 0).sum()),
           "frac_activas": float((T.activacion > 0).mean()),
           "regimen_en_rebalanceo": T["regimen"].value_counts(normalize=True).round(4).to_dict()}
    for nombre, mask in (("activas", T.activacion > 0), ("todas", T.activacion >= 0)):
        sub = T[mask]
        if len(sub) < 3:
            continue
        mu_ad, t_ad, _ = nw_tstat(sub["rho_ad"]); mu_es, t_es, _ = nw_tstat(sub["rho_es"])
        dif, t_dif, _ = nw_tstat(sub["rho_ad"] - sub["rho_es"])
        dv = diebold_mariano(np.zeros(len(sub)), -sub["dvol"].values)     # d = dvol; H1: dvol > 0
        dd = diebold_mariano(np.zeros(len(sub)), -sub["ddd"].values)
        dr = diebold_mariano(np.zeros(len(sub)), -sub["dret"].values)
        res[nombre] = {"n": int(len(sub)), "rho_adaptativa": mu_ad, "t_adaptativa": t_ad,
                       "rho_estatica": mu_es, "t_estatica": t_es, "dif_rho": dif, "t_dif_rho": t_dif,
                       "reduccion_vol_pp": 100 * float(sub["dvol"].mean()), "DM_vol": dv["DM_HLN"],
                       "p_vol_unilateral": dv["p_A_mayor"],
                       "reduccion_caida_pp": 100 * float(sub["ddd"].mean()), "DM_caida": dd["DM_HLN"],
                       "p_caida_unilateral": dd["p_A_mayor"],
                       "costo_rentabilidad_pp": 100 * float(sub["dret"].mean()), "p_ret_bilateral": dr["p_bilateral"],
                       "reduccion_media_orness": float(sub["red_orness"].mean())}
        filas.append({"mercado": mk, "ventanas": nombre, **res[nombre]})
    json.dump(res, open(f"{RES}/resumen_{mk}.json", "w"), indent=1, ensure_ascii=False, default=float)
    print(json.dumps(res, indent=1, ensure_ascii=False, default=float))

    # Figura: orness efectivo por perfil en el tiempo
    fig, ax = plt.subplots(figsize=(7.6, 4.2), dpi=300)
    for i, p in enumerate(PERFILES):
        g = A[A.perfil == p].sort_values("t")
        ax.plot(pd.to_datetime(g["fecha"]), g["orness_efectivo"], color=OK[i], lw=1.2, label=ES[p])
    ax.set_ylabel("Orness efectivo en el rebalanceo"); ax.yaxis.set_major_formatter(coma)
    ax.legend(frameon=False, fontsize=7, ncol=4, loc="upper center", bbox_to_anchor=(0.5, -0.12))
    ax.spines[["top", "right"]].set_visible(False)
    plt.tight_layout(); plt.savefig(f"{FIG}/fig_iowa_orness_{mk}.png", dpi=300, facecolor="white"); plt.close()

pd.DataFrame(filas).to_csv(f"{RES}/tabla_iowa.csv", index=False)
print(pd.DataFrame(filas).round(4).to_string(index=False))
