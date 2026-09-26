"""
verify_lp_vs_slsqp_ventanas.py — Certificación del óptimo global de la vía
espectral en el régimen cóncavo (orness <= 1/2; tesis: Proposición 5, §4.3.5,
Anexo B.6) sobre ventanas de prueba con datos reales del snapshot.

Para cada mercado (US, CO) se toman ventanas de prueba equiespaciadas del
protocolo del Capítulo 5 (estimación de 252 días hábiles, rebalanceo cada 21) y,
para cada perfil con orness <= 1/2 en las dos parametrizaciones (octiles y v1),
se compara:
  * V_LP   : óptimo del programa lineal exacto de la Proposición 5 (misma
             formulación que src/spectral_lp.py, ensamblada en forma dispersa
             para admitir S = 252 escenarios, ~63.500 variables auxiliares);
  * V_PROD : valor alcanzado por el heurístico de producción
             (src/spectral_route.pesos_espectral: SLSQP multiarranque con
             gradiente analítico; 8 arranques en el régimen cóncavo).
Se reporta la brecha V_LP - V_PROD (>= 0 salvo tolerancia numérica) y su
valor relativo. Salida: results/verificacion_lp_ventanas.csv.

Uso: python scripts/verify_lp_vs_slsqp_ventanas.py [n_ventanas]
Licencia: MIT.
"""
import os, sys, time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import numpy as np
import pandas as pd
import scipy.sparse as sp
from scipy.optimize import linprog
from src.owa_core import ANCLAS, beta_para_orness
from src.data import cargar
from src.backtest import rebalanceos, LOOKBACK, CAP
from src.spectral_route import pesos_espectral, V_beta, espectro
from src.spectral_lp import optimiza_cartera_lp


def lp_disperso(R, beta, cap=CAP):
    """Mismo LP que spectral_lp.optimiza_cartera_lp, con matrices dispersas."""
    S, N = R.shape
    psi = espectro(beta, S)
    d = np.clip(np.diff(np.concatenate([[0.0], psi])), 0.0, None)
    n_w, n_t = N, S
    n_var = n_w + n_t + S * S
    c = np.zeros(n_var)
    for k in range(1, S + 1):
        m = S - k + 1
        c[n_w + m - 1] -= d[k - 1] * m
        c[n_w + n_t + (m - 1) * S: n_w + n_t + m * S] += d[k - 1]
    # filas (m, i): t_m - u_{m,i} - R_i.w <= 0
    filas = np.arange(S * S)
    m_idx = np.repeat(np.arange(S), S)
    i_idx = np.tile(np.arange(S), S)
    A_w = sp.csr_matrix(-R[i_idx, :])
    A_t = sp.csr_matrix((np.ones(S * S), (filas, m_idx)), shape=(S * S, n_t))
    A_u = sp.csr_matrix((-np.ones(S * S), (filas, filas)), shape=(S * S, S * S))
    A_ub = sp.hstack([A_w, A_t, A_u], format="csr")
    A_eq = sp.csr_matrix((np.ones(N), (np.zeros(N, int), np.arange(N))), shape=(1, n_var))
    bounds = [(0.0, cap)] * N + [(None, None)] * S + [(0.0, None)] * (S * S)
    res = linprog(c, A_ub=A_ub, b_ub=np.zeros(S * S), A_eq=A_eq, b_eq=[1.0],
                  bounds=bounds, method="highs")
    if not res.success:
        raise RuntimeError(res.message)
    return res.x[:N], float(-res.fun)


def main(n_vent=6):
    # control de equivalencia con la implementación densa de spectral_lp.py
    rng = np.random.default_rng(7)
    Rs = rng.normal(0.0006, 0.018, size=(40, 6))
    b = beta_para_orness(0.25, 40)
    assert abs(lp_disperso(Rs, b)[1] - optimiza_cartera_lp(Rs, b)[1]) < 1e-9

    filas = []
    for mk in ("US", "CO"):
        close, _ = cargar(mk)
        ret = close.pct_change().values
        ts = rebalanceos(len(close))
        sel = [ts[int(round(j))] for j in np.linspace(0, len(ts) - 1, n_vent)]
        for t in sel:
            R = ret[t - LOOKBACK + 1:t + 1]
            for par, anclas in ANCLAS.items():
                for perfil, a in anclas.items():
                    if a > 0.5:
                        continue
                    beta = beta_para_orness(a, R.shape[0])
                    t0 = time.time()
                    _, v_lp = lp_disperso(R, beta)
                    t_lp = time.time() - t0
                    w, _ = pesos_espectral(R, a, cap=CAP)
                    v_pr = V_beta(w, R, beta)
                    filas.append({"mercado": mk, "fecha": str(close.index[t].date()),
                                  "parametrizacion": par, "perfil": perfil, "orness": a,
                                  "beta": beta, "S": R.shape[0], "N": R.shape[1],
                                  "V_LP": v_lp, "V_PROD": v_pr, "brecha": v_lp - v_pr,
                                  "brecha_rel": (v_lp - v_pr) / max(abs(v_lp), 1e-12),
                                  "seg_LP": t_lp})
                    print(mk, filas[-1]["fecha"], par, perfil, f"{v_lp:.3e} {v_pr:.3e} "
                          f"brecha={v_lp - v_pr:.2e} LP {t_lp:.0f}s", flush=True)
    df = pd.DataFrame(filas)
    os.makedirs("results", exist_ok=True)
    df.to_csv("results/verificacion_lp_ventanas.csv", index=False)
    print("\nCasos:", len(df), "| brecha máx.:", f"{df.brecha.max():.2e}",
          "| brecha rel. máx.:", f"{df.brecha_rel.max():.2e}")


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 6)
