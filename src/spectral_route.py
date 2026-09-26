"""
spectral_route.py — Operador espectral PR-WOWA (tesis: §4.3.1 y Proposiciones 3-5).

Aplica el orness sobre los RESULTADOS ORDENADOS de la cartera: R es una matriz
(S escenarios x N activos) de RENDIMIENTOS simples diarios de la ventana de
estimación, y V_beta(w) = sum_s psi_s r_(s), con r_(1) >= ... >= r_(S) los
rendimientos ordenados de la cartera y psi_s = Q(s/S) - Q((s-1)/S), Q(r)=r^beta.

Para beta >= 1 (orness <= 1/2) el espectro asigna más peso a los peores
escenarios, V_beta es cóncavo en w y -V_beta es una medida de riesgo espectral
coherente (Acerbi, 2002). Para beta < 1 el problema deja de ser cóncavo.
En ambos regímenes se maximiza con SLSQP y gradiente analítico desde varios
arranques (multi-start); en el régimen cóncavo el LP exacto de spectral_lp.py
certifica el óptimo global (scripts/verify_lp_vs_slsqp.py).

Versión 1.1.0: corrige el uso de niveles de precio en lugar de rendimientos
(los guiones de la v1.0.0 pasaban precios a optimiza_cartera) y añade el
gradiente analítico.

Licencia: MIT.
"""
from __future__ import annotations
import numpy as np
from scipy.optimize import minimize
from .owa_core import beta_para_orness


def espectro(beta: float, S: int) -> np.ndarray:
    """psi_s = (s/S)^beta - ((s-1)/S)^beta, s = 1..S (índice 1 = mejor escenario)."""
    s = np.arange(1, S + 1)
    return (s / S) ** beta - ((s - 1) / S) ** beta


def V_beta(w, R, beta, psi=None):
    """Funcional PR-WOWA con pesos de escenario uniformes."""
    rp = np.sort(R @ w)[::-1]
    psi = espectro(beta, len(rp)) if psi is None else psi
    return float(psi @ rp)


def _V_y_grad(w, R, psi):
    rp = R @ w
    orden = np.argsort(-rp)                 # índices de mejor a peor
    val = float(psi @ rp[orden])
    grad = R[orden].T @ psi                 # supergradiente (exacto sin empates)
    return val, grad


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
    """Maximiza V_beta(w) sobre {w >= 0, sum w = 1, w <= cap}.
    R: rendimientos (S x N). Devuelve (w_mejor, V_mejor, dispersión entre arranques)."""
    R = np.asarray(R, float)
    rng = np.random.default_rng(seed)
    S, N = R.shape
    psi = espectro(beta, S)
    cons = ({"type": "eq", "fun": lambda w: w.sum() - 1.0, "jac": lambda w: np.ones_like(w)},)
    bnds = [(0.0, cap)] * N

    def f(w):
        v, g = _V_y_grad(w, R, psi)
        return -v, -g

    sols = []
    for x0 in _arranques(N, cap, r_starts, rng):
        res = minimize(f, x0, jac=True, method="SLSQP", bounds=bnds, constraints=cons,
                       options={"maxiter": 300, "ftol": 1e-10})
        w = _proj_simplex_cap(res.x, cap)
        sols.append((w, V_beta(w, R, beta, psi)))
    vals = np.array([v for _, v in sols])
    i_best = int(np.argmax(vals))
    escala = max(abs(vals.max()), 1e-12)
    disp = {
        "V_mejor": float(vals.max()),
        "V_rango": float(vals.max() - vals.min()),
        "V_rango_rel": float((vals.max() - vals.min()) / escala),
        "pct_arranques_optimo": float(np.mean(vals >= vals.max() - 1e-3 * escala) * 100),
    }
    return sols[i_best][0], float(vals.max()), disp


def pesos_espectral(R_in, orness, cap=0.30, r_starts=40, seed=42, r_starts_concavo=8):
    """Cartera espectral para un orness dado; beta se calibra con n = S escenarios.
    R_in debe contener RENDIMIENTOS, no precios. Devuelve (w, dispersión).
    En el régimen cóncavo (orness <= 1/2) todo óptimo local es global, por lo que
    bastan r_starts_concavo arranques; en el régimen no cóncavo se usan r_starts."""
    beta = beta_para_orness(orness, R_in.shape[0])
    if orness <= 0.5:
        r_starts = r_starts_concavo
    w, v, disp = optimiza_cartera(R_in, beta, cap=cap, r_starts=r_starts, seed=seed)
    return w, disp
