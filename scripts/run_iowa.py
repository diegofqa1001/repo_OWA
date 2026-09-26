"""
run_iowa.py — Corrida del componente adaptativo inducido por régimen (tesis §8.4)
sobre el operador espectral PR-WOWA, anclas por octiles, mismo universo,
protocolo y costos que el Capítulo 5 (snapshot data/snapshot_2026-08-31).

En cada rebalanceo t el orness de cada perfil se sustituye por
alpha_eff(t) = alpha - lambda * a(t) * max(0, alpha - alpha_min)  (src/regime.py),
con a(t) la activación del índice de estrés en t (información disponible en t).
La versión estática es la vía espectral del Capítulo 5 (results/cap5).

Escribe results/iowa/ventanas_<mk>.csv, series_<mk>.csv y estres_<mk>.csv.
Uso: python scripts/run_iowa.py [US|CO]
"""
import os, sys, time, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import numpy as np, pandas as pd
from src.owa_core import ORNESS_OCTILES, PERFILES
from src.data import cargar
from src.backtest import backtest, CAP
from src.spectral_route import pesos_espectral
from src.regime import indice_estres, orness_efectivo, LAMBDA, ALPHA_MIN, S0

R_STARTS, SEED = 40, 42
OUT = os.path.join(os.path.dirname(__file__), "..", "results", "iowa")
os.makedirs(OUT, exist_ok=True)


def corre(mercado):
    close, _ = cargar(mercado)
    est = indice_estres(close.index)
    est.to_csv(f"{OUT}/estres_{mercado}.csv")
    ventanas, series = [], {}
    t0 = time.time()
    for p in PERFILES:
        o = ORNESS_OCTILES[p]

        def f_adapt(t, R_in, o=o):
            a_eff = orness_efectivo(o, float(est["activacion"].iloc[t]))
            w, _ = pesos_espectral(R_in, a_eff, cap=CAP, r_starts=R_STARTS, seed=SEED)
            return w

        bt = backtest(close, f_adapt)
        series[p] = bt["serie"]
        for v in bt["por_ventana"]:
            t = v["t"]
            ventanas.append({"perfil": p, "orness": o,
                             "orness_efectivo": orness_efectivo(o, float(est["activacion"].iloc[t])),
                             "s": float(est["s"].iloc[t]), "activacion": float(est["activacion"].iloc[t]),
                             "regimen": est["regimen"].iloc[t], **v})
        print(mercado, p, f"{time.time() - t0:.0f}s", flush=True)
    pd.DataFrame(ventanas).to_csv(f"{OUT}/ventanas_{mercado}.csv", index=False)
    pd.DataFrame(series, index=bt["fechas"]).to_csv(f"{OUT}/series_{mercado}.csv")
    json.dump({"mercado": mercado, "lambda": LAMBDA, "alpha_min": ALPHA_MIN, "umbral_s0": S0,
               "anclas": "octiles", "arranques": R_STARTS, "semilla": SEED},
              open(f"{OUT}/meta_{mercado}.json", "w"), indent=1)


if __name__ == "__main__":
    for m in ([sys.argv[1]] if len(sys.argv) > 1 else ["US", "CO"]):
        corre(m)
