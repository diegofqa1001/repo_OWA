"""
analyze_cap5_complementos.py — Estadísticos complementarios del Capítulo 5 que la
tesis cita en §5.4-5.6 y que no produce analyze_cap5.py.

1. Coherencia por ventana en los ejes de rentabilidad y de caída máxima (prueba A
   aplicada a ret y a |dd| en lugar de la volatilidad), para ambas vías, ambos
   mercados y ambas anclas -> results/cap5/coherencia_ejes.csv
2. Concentración de las carteras espectrales (anclas por octiles): número de
   activos en el tope de 0,30, número de posiciones con peso > 0,1 % e índice de
   Herfindahl, por perfil y ventana. Los pesos se recalculan con la misma función,
   semilla y arranques que run_cap5.py (pesos_espectral es determinista dada la
   ventana), y se verifica que reproducen la serie archivada (diferencia máxima
   absoluta de rendimiento diario < 1e-3, registrada en concentracion_verificacion_series.csv) en
   results/cap5/series_<mk>_octiles.csv -> results/cap5/concentracion_espectral.csv
   y concentracion_espectral_resumen.csv

Uso: python scripts/analyze_cap5_complementos.py
Licencia: MIT.
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import numpy as np, pandas as pd
from src.owa_core import ANCLAS, PERFILES
from src.data import cargar
from src.backtest import rebalanceos, LOOKBACK, STEP, TC, CAP
from src.spectral_route import pesos_espectral
from src.inference import monotonia_por_ventana

RES = os.path.join(os.path.dirname(__file__), "..", "results", "cap5")
R_STARTS, SEED = 40, 42

# 1. Coherencia en otros ejes
filas = []
for mk in ("US", "CO"):
    for an in ("octiles", "v1"):
        V = pd.read_csv(f"{RES}/ventanas_{mk}_{an}.csv")
        orn = np.array([ANCLAS[an][p] for p in PERFILES])
        for via in ("criterios", "espectral"):
            sub = V[V.via == via]
            for eje, col, signo in (("volatilidad", "vol", 1.0), ("rentabilidad", "ret", 1.0),
                                    ("caida_maxima", "dd", -1.0)):
                M = signo * sub.pivot(index="t", columns="perfil", values=col)[PERFILES].values
                mw = monotonia_por_ventana(orn, M)
                filas.append({"mercado": mk, "anclas": an, "via": via, "eje": eje,
                              "n_ventanas": mw["n_ventanas"], "rho_medio": mw["rho_medio"],
                              "t_NW": mw["t_NW"], "p_NW": mw["p_NW"],
                              "pct_ventanas_rho_pos": mw["pct_ventanas_pos"], "p_binomial": mw["p_binomial"]})
ejes = pd.DataFrame(filas)
ejes.to_csv(f"{RES}/coherencia_ejes.csv", index=False)
print(ejes.round(3).to_string(index=False))

# 2. Concentración de las carteras espectrales (octiles)
conc, difs = [], {}
for mk in ("US", "CO"):
    close, _ = cargar(mk)
    ret = close.pct_change().values
    S = pd.read_csv(f"{RES}/series_{mk}_octiles.csv", index_col=0)
    max_dif = 0.0
    for p in PERFILES:
        o = ANCLAS["octiles"][p]
        w_prev = None
        rp_all = []
        for t in rebalanceos(len(close), LOOKBACK, STEP):
            R_in = ret[t - LOOKBACK + 1:t + 1]
            w, _ = pesos_espectral(R_in, o, cap=CAP, r_starts=R_STARTS, seed=SEED)
            rot = float(np.abs(w).sum()) if w_prev is None else float(np.abs(w - w_prev).sum())
            fut = ret[t + 1:t + 1 + STEP]
            rp = fut @ w; rp = rp.copy(); rp[0] -= TC * rot
            crec = np.prod(1 + fut, axis=0) * w
            w_prev = crec / crec.sum() if crec.sum() > 0 else w
            rp_all.append(rp)
            conc.append({"mercado": mk, "perfil": p, "orness": o, "t": t,
                         "n_en_tope": int((w >= CAP - 1e-3).sum()),
                         "n_posiciones": int((w > 1e-3).sum()),
                         "hhi": float((w ** 2).sum())})
        serie = np.concatenate(rp_all)
        max_dif = max(max_dif, float(np.max(np.abs(serie - S[f"espectral:{p}"].values))))
        print(mk, p, "listo", flush=True)
    print(mk, "máxima diferencia frente a la serie archivada:", max_dif)
    difs[mk] = max_dif
    # tolerancia: diferencias de redondeo del optimizador (SLSQP) en ventanas con empates
    assert max_dif < 1e-3, "los pesos recalculados no reproducen la serie archivada"
C = pd.DataFrame(conc)
C.to_csv(f"{RES}/concentracion_espectral.csv", index=False)
res = (C.groupby(["mercado", "perfil", "orness"])
         .agg(n_en_tope_medio=("n_en_tope", "mean"), n_posiciones_medio=("n_posiciones", "mean"),
              hhi_medio=("hhi", "mean"),
              pct_ventanas_3_en_tope=("n_en_tope", lambda x: 100 * float((x >= 3).mean())))
         .reset_index().sort_values(["mercado", "orness"]))
res.to_csv(f"{RES}/concentracion_espectral_resumen.csv", index=False)
pd.Series(difs, name="max_dif_abs_rendimiento_diario").to_csv(f"{RES}/concentracion_verificacion_series.csv")
print(res.round(3).to_string(index=False))
