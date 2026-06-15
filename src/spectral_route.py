"""
spectral_route.py — Operador espectral PR-WOWA (Definición 6, Prop. 3-7).

Aplica el orness sobre los resultados ORDENADOS de la cartera. Para alpha<=1/2
(beta>=1) es una medida de riesgo espectral coherente, resoluble como LP por
mezcla de CVaR (Prop. 6). Para alpha>1/2 (beta<1) es busca-riesgo y no convexo;
se resuelve por SLSQP con barrido de arranques (multi-start) reportando la
dispersión de los óptimos locales (residual R1 de la revisión Q1).

Licencia: MIT.
"""
from __future__ import annotations
import numpy as np
from scipy.optimize import minimize
from .owa_core import beta_para_orness


def V_beta(w, R, beta):
    """Funcional PR-WOWA (sub-caso de pesos de escenario uniformes)."""
    rp = np.sort(R @ w)[::-1]                  # r_(1) >= ... >= r_(S)
    S = len(rp)
    P = np.arange(1, S + 1) / S                # acumulada empirica
    Q = P ** beta
    psi = np.diff(np.concatenate([[0.0], Q]))  # psi_s = Q(P_s) - Q(P_{s-1})
    return float(np.sum(psi * rp))


def _proj_simplex_cap(w, cap):
    w = np.clip(w, 0, cap)
    s = w.sum()
    return w / s if s > 0 else np.full_like(w, 1.0 / len(w))


def _arranques(N, cap, r_starts, rng):
    starts = [np.full(N, 1.0 / N)]
    for _ in range(r_starts // 2):
        k = max(1, int(np.ceil(1.0 / cap)))
        idx = rng.choice(N, size=min(k, N), replace=False)
        w = np.zeros(N); w[idx] = cap
        starts.append(_proj_simplex_cap(w, cap))
    while len(starts) < r_starts:
        starts.append(_proj_simplex_cap(rng.dirichlet(np.ones(N)), cap))
    return starts


def optimiza_cartera(R, beta, cap=0.30, r_starts=40, seed=42):
    """Maximiza V_beta sobre el simplex con tope cap. Multi-start SLSQP.
    Devuelve (w_mejor, valor_mejor, dispersion)."""
    rng = np.random.default_rng(seed)
    N = R.shape[1]
    cons = ({"type": "eq", "fun": lambda w: w.sum() - 1.0},)
    bnds = [(0.0, cap)] * N
    sols = []
    for x0 in _arranques(N, cap, r_starts, rng):
        res = minimize(lambda w: -V_beta(w, R, beta), x0, method="SLSQP",
                       bounds=bnds, constraints=cons,
                       options={"maxiter": 300, "ftol": 1e-9})
        sols.append((res.x, -res.fun))
    vals = np.array([v for _, v in sols])
    i_best = int(np.argmax(vals))
    disp = {
        "V_mejor": float(vals.max()),
        "V_rango": float(vals.max() - vals.min()),
        "V_std": float(vals.std()),
        "pct_arranques_optimo": float(np.mean(vals >= vals.max() - 1e-3 * abs(vals.max())) * 100),
    }
    return sols[i_best][0], float(vals.max()), disp


def pesos_espectral(R_in, orness, cap=0.30, r_starts=40, seed=42):
    """Cartera espectral para un orness dado, calibrando beta con n=S escenarios."""
    beta = beta_para_orness(orness, R_in.shape[0])
    w, _, _ = optimiza_cartera(R_in, beta, cap=cap, r_starts=r_starts, seed=seed)
    return w
