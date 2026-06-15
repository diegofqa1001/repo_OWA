"""
run_criteria.py — Vía de criterios: backtest (resultado de inversión).
Escribe results/criterios_desempeno_<mercado>.csv.

Uso:  python scripts/run_criteria.py [US|CO]
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import numpy as np, pandas as pd
from src.owa_core import ORNESS_PERFIL
from src.criteria_route import pesos_criterios
from src.backtest import cargar, resumen

mercado = sys.argv[1] if len(sys.argv) > 1 else "US"
os.makedirs("results", exist_ok=True)
close, volume = cargar(mercado)
n = len(close)
rows = []
for p, o in ORNESS_PERFIL.items():
    series = []
    for t in range(252, n - 21, 21):
        cw, vw = close.iloc[t - 252:t], volume.iloc[t - 252:t]
        w = pesos_criterios(cw, vw, o, k=8)
        series.append(close.iloc[t:t + 21].pct_change().dropna().values @ w)
    r = np.concatenate(series)
    rows.append({"Perfil": p, "orness": o, **{k: round(v, 3) for k, v in resumen(r).items()}})
tab = pd.DataFrame(rows)
tab.to_csv(f"results/criterios_desempeno_{mercado}.csv", index=False)
print(tab.to_string(index=False))
print(f"\nGuardado: results/criterios_desempeno_{mercado}.csv")
