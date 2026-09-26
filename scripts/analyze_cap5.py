"""
analyze_cap5.py — Tablas, pruebas y figuras del Capítulo 5 a partir de results/cap5.

Escribe en results/cap5/:
  tabla_5_1_coherencia.csv   prueba A (monotonía por ventana) y prueba B (permutación exacta)
  tabla_5_2_desempeno.csv    rentabilidad, volatilidad, Sharpe y caída máxima por estrategia
  tabla_5_3_dm.csv           Diebold-Mariano (HLN) de los contrastes declarados
  dispersion_resumen.csv     estabilidad del multi-start en el régimen no cóncavo
y en figures/: fig_5_1_coherencia.png, fig_5_2_volatilidad_perfil.png,
fig_5_3_vias_US.png (Okabe-Ito, fondo blanco, 300 dpi, rótulos en español).

Uso: python scripts/analyze_cap5.py
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from src.owa_core import ANCLAS, PERFILES
from src.backtest import resumen
from src.inference import monotonia_por_ventana, permutacion_exacta, diebold_mariano

RES = os.path.join(os.path.dirname(__file__), "..", "results", "cap5")
FIG = os.path.join(os.path.dirname(__file__), "..", "figures"); os.makedirs(FIG, exist_ok=True)
ES = {"Guardian": "Guardián", "Sentinel": "Centinela", "Pragmatist": "Pragmático", "Analyst": "Analista",
      "Strategist": "Estratega", "Adventurer": "Aventurero", "Innovator": "Innovador", "Visionary": "Visionario"}
OK = ["#E69F00", "#56B4E9", "#009E73", "#F0E442", "#0072B2", "#D55E00", "#CC79A7", "#000000"]
coma = FuncFormatter(lambda x, _: f"{x:g}".replace(".", ","))
plt.rcParams.update({"font.family": "DejaVu Sans", "axes.facecolor": "white", "figure.facecolor": "white"})

coh, des, dms, disp_rows = [], [], [], []
for mk in ("US", "CO"):
    for an in ("octiles", "v1"):
        V = pd.read_csv(f"{RES}/ventanas_{mk}_{an}.csv")
        S = pd.read_csv(f"{RES}/series_{mk}_{an}.csv", index_col=0)
        orn = np.array([ANCLAS[an][p] for p in PERFILES])
        for via in ("criterios", "espectral"):
            sub = V[V.via == via]
            M = sub.pivot(index="t", columns="perfil", values="vol")[PERFILES].values
            mw = monotonia_por_ventana(orn, M)
            pe = permutacion_exacta(orn, np.nanmean(M, axis=0))
            gv = sub.pivot(index="t", columns="perfil", values="vol")
            coh.append({"mercado": mk, "anclas": an, "via": via, "n_ventanas": mw["n_ventanas"],
                        "rho_medio": mw["rho_medio"], "t_NW": mw["t_NW"], "p_NW": mw["p_NW"], "lag_NW": mw["lag"],
                        "pct_ventanas_rho_pos": mw["pct_ventanas_pos"], "p_binomial": mw["p_binomial"],
                        "pct_guardian_mas_volatil_que_visionario": 100 * float((gv["Guardian"] > gv["Visionary"]).mean()),
                        "rho_perm": pe["rho_obs"], "p_perm_exacta": pe["p_perm"], "n_perm": pe["n_perm"]})
            for p in PERFILES:
                r = resumen(S[f"{via}:{p}"].values)
                des.append({"mercado": mk, "anclas": an, "estrategia": f"{via}", "perfil": p,
                            "orness": ANCLAS[an][p], **r,
                            "rotacion_media": float(sub[sub.perfil == p]["rotacion"].iloc[1:].mean())})
        for c in ("1/N", "Markowitz"):
            r = resumen(S[c].values)
            des.append({"mercado": mk, "anclas": an, "estrategia": "comparador", "perfil": c, "orness": np.nan, **r,
                        "rotacion_media": float(V[V.perfil == c]["rotacion"].iloc[1:].mean())})
        pares = [("espectral:Guardian", "1/N"), ("espectral:Guardian", "criterios:Guardian"),
                 ("espectral:Visionary", "Markowitz"), ("espectral:Guardian", "Markowitz"),
                 ("criterios:Guardian", "criterios:Visionary"), ("espectral:Guardian", "espectral:Visionary")]
        for a, b in pares:
            for nombre, la, lb in (("rentabilidad", -S[a].values, -S[b].values),
                                   ("cuadrado", S[a].values ** 2, S[b].values ** 2)):
                d = diebold_mariano(la, lb)
                dms.append({"mercado": mk, "anclas": an, "A": a, "B": b, "perdida": nombre, **d})
        D = pd.read_csv(f"{RES}/dispersion_{mk}_{an}.csv")
        for p, g in D.groupby("perfil"):
            disp_rows.append({"mercado": mk, "anclas": an, "perfil": p, "orness": g["orness"].iloc[0],
                              "V_rango_rel_medio": g["V_rango_rel"].mean(),
                              "pct_arranques_optimo_medio": g["pct_arranques_optimo"].mean(),
                              "pct_arranques_optimo_min": g["pct_arranques_optimo"].min()})

coh = pd.DataFrame(coh); des = pd.DataFrame(des); dms = pd.DataFrame(dms); disp = pd.DataFrame(disp_rows)
coh.to_csv(f"{RES}/tabla_5_1_coherencia.csv", index=False)
des.to_csv(f"{RES}/tabla_5_2_desempeno.csv", index=False)
dms.to_csv(f"{RES}/tabla_5_3_dm.csv", index=False)
disp.to_csv(f"{RES}/dispersion_resumen.csv", index=False)
pd.set_option("display.width", 250); pd.set_option("display.max_columns", 30)
print(coh.round(3).to_string(index=False))
print(des[des.anclas == "octiles"].round(3).to_string(index=False))
print(dms[dms.anclas == "octiles"].round(4).to_string(index=False))
print(disp[(disp.anclas == "octiles") & (disp.orness > 0.5)].round(3).to_string(index=False))

# Figura 5.1: % de ventanas con rho > 0 por vía y mercado (anclas canónicas)
c = coh[coh.anclas == "octiles"]
fig, ax = plt.subplots(figsize=(7, 4.2), dpi=300)
x = np.arange(2); ancho = 0.36
for i, (via, col) in enumerate((("criterios", OK[5]), ("espectral", OK[4]))):
    vals = [c[(c.mercado == m) & (c.via == via)]["pct_ventanas_rho_pos"].iloc[0] for m in ("US", "CO")]
    b = ax.bar(x + (i - 0.5) * ancho, vals, ancho, color=col, label=f"Vía {via}")
    for xi, v in zip(x + (i - 0.5) * ancho, vals):
        ax.text(xi, v + 1.5, f"{v:.0f} %", ha="center", fontsize=8)
ax.axhline(50, ls="--", color="#999999", lw=1, label="Referencia aleatoria (50 %)")
ax.set_xticks(x, ["Estados Unidos", "Colombia"]); ax.set_ylim(0, 110)
ax.set_ylabel("Ventanas con riesgo creciente en el orness (%)")
ax.legend(frameon=False, fontsize=8, loc="upper left"); ax.spines[["top", "right"]].set_visible(False)
plt.tight_layout(); plt.savefig(f"{FIG}/fig_5_1_coherencia.png", dpi=300, facecolor="white"); plt.close()

# Figura 5.2: volatilidad fuera de muestra por perfil, vía espectral, ambos mercados
fig, ax = plt.subplots(figsize=(7.2, 4.4), dpi=300)
# Rótulos sin solapamiento: para cada perfil, el mercado con mayor volatilidad se rotula
# encima de su marcador y el de menor volatilidad debajo.
_esp = des[(des.anclas == "octiles") & (des.estrategia == "espectral") & (des.mercado.isin(["US", "CO"]))]
_vmax = _esp.groupby("perfil")["Vol%"].max()
for mk, col, mkr in (("US", OK[4], "o"), ("CO", OK[0], "s")):
    d = des[(des.anclas == "octiles") & (des.mercado == mk) & (des.estrategia == "espectral")]
    ax.plot(d["orness"], d["Vol%"], marker=mkr, color=col, lw=1.8, label="Estados Unidos" if mk == "US" else "Colombia")
    for _, r in d.iterrows():
        arriba = r["Vol%"] >= _vmax[r["perfil"]]
        ax.annotate(ES[r["perfil"]], (r["orness"], r["Vol%"]), fontsize=6.5, color=col,
                    xytext=(0, 6 if arriba else -7), textcoords="offset points", ha="center",
                    va="bottom" if arriba else "top",
                    bbox=dict(fc="white", ec="none", pad=0.4, alpha=0.8))
ax.axvline(0.5, ls="--", color=OK[5], lw=1, label="Cruce de régimen (orness = 1/2)")
ax.margins(y=0.09)
ax.set_xlabel("Orness del perfil (anclas por octiles)"); ax.set_ylabel("Volatilidad anualizada fuera de muestra (%)")
ax.xaxis.set_major_formatter(coma); ax.yaxis.set_major_formatter(coma)
ax.legend(frameon=False, fontsize=8); ax.spines[["top", "right"]].set_visible(False)
plt.tight_layout(); plt.savefig(f"{FIG}/fig_5_2_volatilidad_perfil.png", dpi=300, facecolor="white"); plt.close()

# Figura 5.3: comparativa de las dos vías en volatilidad (EE. UU.)
fig, ax = plt.subplots(figsize=(7.2, 4.4), dpi=300)
for via, col, mkr in (("criterios", OK[5], "s"), ("espectral", OK[4], "o")):
    d = des[(des.anclas == "octiles") & (des.mercado == "US") & (des.estrategia == via)]
    ax.plot(d["orness"], d["Vol%"], marker=mkr, color=col, lw=1.8, label=f"Vía {via}")
for cmp, ls in (("1/N", ":"), ("Markowitz", "-.")):
    v = des[(des.anclas == "octiles") & (des.mercado == "US") & (des.perfil == cmp)]["Vol%"].iloc[0]
    ax.axhline(v, ls=ls, color="#999999", lw=1, label=cmp)
ax.set_xlabel("Orness del perfil (anclas por octiles)"); ax.set_ylabel("Volatilidad anualizada fuera de muestra (%)")
ax.xaxis.set_major_formatter(coma); ax.yaxis.set_major_formatter(coma)
ax.legend(frameon=False, fontsize=8); ax.spines[["top", "right"]].set_visible(False)
plt.tight_layout(); plt.savefig(f"{FIG}/fig_5_3_vias_US.png", dpi=300, facecolor="white"); plt.close()
print("figuras guardadas en", FIG)
