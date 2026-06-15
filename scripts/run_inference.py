"""
run_inference.py — Reproduce la Tabla 1 (coherencia conductual en volatilidad):
monotonia por ventana (NW + binomial) y permutacion, para las vias de criterios
y espectral, en US y CO. Escribe results/tabla1_coherencia.csv.

Uso:  python scripts/run_inference.py   [puede tardar por el multi-start]
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import numpy as np, pandas as pd
from src.owa_core import ORNESS_PERFIL, PERFILES, beta_para_orness
from src.spectral_route import optimiza_cartera
from src.criteria_route import pesos_criterios
from src.backtest import cargar
from src.inference import monotonia_por_ventana, permutacion

CAP, R_STARTS, LOOKBACK, STEP = 0.30, 20, 252, 21
os.makedirs("results", exist_ok=True)
orn = np.array([ORNESS_PERFIL[p] for p in PERFILES])
filas = []

for mercado in ("US", "CO"):
    close, volume = cargar(mercado)
    arr = close.values; n = len(close)
    betas = {p: beta_para_orness(o, LOOKBACK) for p, o in ORNESS_PERFIL.items()}
    vol_crit, vol_spec = [], []
    for t in range(LOOKBACK, n - STEP, STEP):
        Rin = arr[t - LOOKBACK:t]
        fut = pd.DataFrame(arr[t:t + STEP]).pct_change().dropna().values
        fila_c, fila_s = [], []
        cw, vw = close.iloc[t - LOOKBACK:t], volume.iloc[t - LOOKBACK:t]
        for p in PERFILES:
            wc = pesos_criterios(cw, vw, ORNESS_PERFIL[p], k=8)
            ws, _, _ = optimiza_cartera(Rin, betas[p], cap=CAP, r_starts=R_STARTS)
            fila_c.append((fut @ wc).std(ddof=1))
            fila_s.append((fut @ ws).std(ddof=1))
        vol_crit.append(fila_c); vol_spec.append(fila_s)
    vol_crit = np.array(vol_crit); vol_spec = np.array(vol_spec)
    for via, M in (("Criterios", vol_crit), ("Espectral", vol_spec)):
        mw = monotonia_por_ventana(orn, M)
        pm = permutacion(orn, np.nanmean(M, axis=0), n_perm=20000)
        filas.append({"mercado": mercado, "via": via,
                      "rho_medio_ventana": round(mw["rho_medio"], 3),
                      "t_NW": round(mw["t_NW"], 1), "lag": mw["lag"],
                      "pct_ventanas": round(mw["pct_ventanas_pos"], 0),
                      "rho_perm": round(pm["rho_obs"], 2), "p_perm": round(pm["p_perm"], 4)})
        print(mercado, via, filas[-1])

pd.DataFrame(filas).to_csv("results/tabla1_coherencia.csv", index=False)
print("\nGuardado: results/tabla1_coherencia.csv")
