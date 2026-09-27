"""diag_tope_criterios.py — Peso máximo de las carteras de la vía de criterios.

La vía de criterios (src/criteria_route.py) selecciona los k = 8 activos de
mayor puntaje OWA y mezcla pesos proporcionales al puntaje (con peso igual al
orness) e inverso-volatilidad (con peso 1 − orness). No aplica el tope de
concentración explícitamente; este guion comprueba, con el mismo protocolo de
run_cap5.py (anclas por octiles, instantánea data/snapshot_2026-08-31), el
peso máximo alcanzado en todos los rebalanceos y perfiles.

Uso:  python scripts/diag_tope_criterios.py
Salida: results/cap5/diag_tope_criterios.csv
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import numpy as np, pandas as pd
from src.owa_core import ANCLAS, PERFILES
from src.data import cargar
from src.backtest import rebalanceos, LOOKBACK, CAP
from src.criteria_route import pesos_criterios

OUT = os.path.join(os.path.dirname(__file__), "..", "results", "cap5", "diag_tope_criterios.csv")
filas = []
for mk in ("US", "CO"):
    close, volume = cargar(mk)
    for p in PERFILES:
        o = ANCLAS["octiles"][p]
        mx = []
        for t in rebalanceos(len(close)):
            w = pesos_criterios(close.iloc[t - LOOKBACK + 1:t + 1],
                                volume.iloc[t - LOOKBACK + 1:t + 1], o, k=8)
            mx.append(float(w.max()))
        mx = np.array(mx)
        filas.append({"mercado": mk, "perfil": p, "orness": o, "k": 8,
                      "rebalanceos": len(mx), "peso_max": mx.max(),
                      "peso_max_medio": mx.mean(),
                      "rebalanceos_sobre_tope": int((mx > CAP + 1e-12).sum()),
                      "tope": CAP})
df = pd.DataFrame(filas)
df.to_csv(OUT, index=False)
print(df.round(4).to_string())
