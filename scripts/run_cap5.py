"""
run_cap5.py — Reproduce íntegramente el Capítulo 5 de la tesis sobre el snapshot
versionado data/snapshot_2026-08-31 (2015-2024, EE. UU. y Colombia).

Para cada mercado y cada parametrización de anclas (octiles canónicos; v1 como
sensibilidad) ejecuta, con el mismo protocolo y neto de costos:
  - la vía de criterios (8 perfiles),
  - la vía espectral PR-WOWA (8 perfiles, SLSQP multi-start con gradiente),
  - los comparadores 1/N y Markowitz (máxima razón de Sharpe),
y escribe en results/cap5/:
  ventanas_<mk>_<anclas>.csv    métricas realizadas por ventana, perfil y vía
  series_<mk>_<anclas>.csv      rendimientos diarios netos por estrategia
  dispersion_<mk>_<anclas>.csv  dispersión del multi-start por ventana y perfil
Luego scripts/analyze_cap5.py calcula tablas, pruebas y figuras.

Uso:  python scripts/run_cap5.py [US|CO] [octiles|v1]    (sin argumentos: todo)
"""
import os, sys, json, time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import numpy as np, pandas as pd
from src.owa_core import ANCLAS, PERFILES
from src.data import cargar
from src.backtest import backtest, pesos_1N, pesos_markowitz, LOOKBACK, STEP, TC, CAP
from src.criteria_route import pesos_criterios
from src.spectral_route import pesos_espectral

R_STARTS, SEED = 40, 42
OUT = os.path.join(os.path.dirname(__file__), "..", "results", "cap5")
os.makedirs(OUT, exist_ok=True)


def corre(mercado, anclas):
    close, volume = cargar(mercado)
    orn = ANCLAS[anclas]
    ventanas, series, disp = [], {}, []
    t0 = time.time()
    for p in PERFILES:
        o = orn[p]

        def f_crit(t, R_in, o=o):
            cw = close.iloc[t - LOOKBACK + 1:t + 1]; vw = volume.iloc[t - LOOKBACK + 1:t + 1]
            return pesos_criterios(cw, vw, o, k=8)

        def f_spec(t, R_in, o=o, p=p):
            w, d = pesos_espectral(R_in, o, cap=CAP, r_starts=R_STARTS, seed=SEED)
            disp.append({"perfil": p, "orness": o, "t": t, **d})
            return w

        for via, fn in (("criterios", f_crit), ("espectral", f_spec)):
            bt = backtest(close, fn)
            series[f"{via}:{p}"] = bt["serie"]
            for v in bt["por_ventana"]:
                ventanas.append({"perfil": p, "orness": o, "via": via, **v})
        print(mercado, anclas, p, f"{time.time() - t0:.0f}s", flush=True)
    for nombre, fn in (("1/N", pesos_1N), ("Markowitz", pesos_markowitz)):
        bt = backtest(close, fn)
        series[nombre] = bt["serie"]
        for v in bt["por_ventana"]:
            ventanas.append({"perfil": nombre, "orness": np.nan, "via": "comparador", **v})
    idx = bt["fechas"]
    pd.DataFrame(ventanas).to_csv(f"{OUT}/ventanas_{mercado}_{anclas}.csv", index=False)
    pd.DataFrame(series, index=idx).to_csv(f"{OUT}/series_{mercado}_{anclas}.csv")
    pd.DataFrame(disp).to_csv(f"{OUT}/dispersion_{mercado}_{anclas}.csv", index=False)
    meta = {"mercado": mercado, "anclas": anclas, "activos": list(close.columns),
            "n_dias": len(close), "inicio": str(close.index[0].date()), "fin": str(close.index[-1].date()),
            "n_ventanas": len(set(v["t"] for v in ventanas)), "lookback": LOOKBACK, "step": STEP,
            "costo_pb": TC * 1e4, "tope": CAP, "arranques": R_STARTS, "semilla": SEED}
    json.dump(meta, open(f"{OUT}/meta_{mercado}_{anclas}.json", "w"), indent=1, ensure_ascii=False)
    print("listo", meta, flush=True)


if __name__ == "__main__":
    mks = [sys.argv[1]] if len(sys.argv) > 1 else ["US", "CO"]
    ans = [sys.argv[2]] if len(sys.argv) > 2 else ["octiles", "v1"]
    for m in mks:
        for a in ans:
            corre(m, a)
