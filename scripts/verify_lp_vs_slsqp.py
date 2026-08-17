"""
verify_lp_vs_slsqp.py — Verificacion de la Proposicion 5 (tratabilidad por
programa lineal en el regimen coherente, beta>=1) contra el heuristico
SLSQP multi-start usado en el resto del repositorio.

La Proposicion 5 (Anexo B.6 de la tesis) afirma que para alpha<=1/2
(beta>=1) la cartera optima se obtiene resolviendo un unico programa
lineal (mezcla finita de CVaR). spectral_route.py resuelve siempre con
SLSQP multi-start -- correcto y necesario en el regimen no convexo
(alpha>1/2), pero sin necesidad teorica en el regimen coherente. Este
script cierra esa brecha entre el enunciado formal y el codigo: calcula,
para cada perfil con orness<=1/2, el optimo certificado por LP
(src/spectral_lp.py) y lo compara contra el optimo hallado por SLSQP
multi-start.

Se usan escenarios SIMULADOS (no datos de mercado) deliberadamente: el
proposito de este script es una verificacion determinista y reproducible
del ALGORITMO (¿el heuristico encuentra el optimo que el LP certifica?),
no una re-estimacion empirica de las carteras de la tesis -- para eso
estan run_spectral_multistart.py y run_criteria.py, que sí usan datos
reales via yfinance. El LP crece como S^2 en el numero de escenarios
(ver docstring de spectral_lp.py), por lo que S se mantiene moderado.

Uso:  python scripts/verify_lp_vs_slsqp.py
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import numpy as np
import pandas as pd
from src.owa_core import ORNESS_PERFIL, beta_para_orness
from src.spectral_route import optimiza_cartera, V_beta
from src.spectral_lp import optimiza_cartera_lp

CAP, S, N, SEED = 0.30, 60, 10, 20260704

os.makedirs("results", exist_ok=True)
rng = np.random.default_rng(SEED)
# escenarios simulados: retornos diarios ~ N(0.0006, 0.018), correlacion
# moderada entre activos (misma escala que las series bursatiles reales
# que consume backtest.py; ver justificacion en el docstring).
corr = 0.15 * np.ones((N, N)) + 0.85 * np.eye(N)
L = np.linalg.cholesky(corr)
Z = rng.normal(size=(S, N))
R = 0.0006 + 0.018 * (Z @ L.T)

print(f"Verificacion LP (Prop. 5) vs SLSQP multi-start — "
      f"{N} activos simulados, {S} escenarios, semilla={SEED}")
print(f"{'perfil':<12}{'orness':>8}{'beta':>8}{'V_LP':>12}{'V_SLSQP':>12}{'dif':>10}")
filas = []
for perfil, orness in ORNESS_PERFIL.items():
    if orness > 0.5:
        continue  # el LP solo es valido en el regimen coherente (Prop. 5)
    beta = beta_para_orness(orness, S)
    w_lp, V_lp = optimiza_cartera_lp(R, beta, cap=CAP)
    w_sq, V_sq, _ = optimiza_cartera(R, beta, cap=CAP, r_starts=40, seed=1)
    V_sq_directo = V_beta(w_sq, R, beta)
    dif = abs(V_lp - V_sq_directo)
    filas.append({"perfil": perfil, "orness": orness, "beta": round(beta, 3),
                   "V_LP": round(V_lp, 6), "V_SLSQP": round(V_sq_directo, 6),
                   "dif_abs": dif})
    print(f"{perfil:<12}{orness:>8.3f}{beta:>8.3f}{V_lp:>12.6f}"
          f"{V_sq_directo:>12.6f}{dif:>10.2e}")

pd.DataFrame(filas).to_csv("results/verificacion_lp_vs_slsqp.csv", index=False)
peor = max(f["dif_abs"] for f in filas)
print(f"\nDiferencia maxima LP vs SLSQP en el regimen coherente: {peor:.2e}")
print("Guardado: results/verificacion_lp_vs_slsqp.csv")
