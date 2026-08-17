"""
spectral_lp.py — Formulacion LP exacta (Proposicion 5) para el regimen
coherente alpha<=1/2 (beta>=1), y verificacion cruzada contra el heuristico
SLSQP multi-start de spectral_route.py.

Motivacion: la Proposicion 5 (Anexo B.6) afirma que, para beta>=1, la
cartera optima se obtiene resolviendo un unico programa lineal (mezcla
finita de CVaR, Rockafellar & Uryasev, 2000; Ogryczak & Sliwinski, 2003).
spectral_route.py resuelve SIEMPRE con SLSQP multi-start, sin ejercer esa
tratabilidad. Este modulo cierra la brecha: implementa el LP y lo usa
para verificar, en el regimen convexo, que el heuristico alcanza el
optimo global que el LP certifica.

Fundamento matematico. Para pesos OWA psi_1<=...<=psi_S (mas peso al peor
escenario; el caso beta>=1) el funcional

    V_beta(w) = sum_{s=1}^{S} psi_s * r_(s)     (r_(1)>=...>=r_(S), retornos
                                                  ordenados de la cartera w)

se puede reescribir, via sumacion de Abel con d_k = psi_k - psi_{k-1} >= 0
(psi_0 = 0), como

    V_beta(w) = sum_{k=1}^{S} d_k * SumWorst_{S-k+1}(w)

donde SumWorst_m(w) es la suma de los m peores retornos de la cartera w.
Por Rockafellar-Uryasev, para cada nivel m:

    SumWorst_m(w) = m * max_t [ t - (1/m) * sum_i max(0, t - R_i.w) ]

es (m veces) el valor de un LP con variables auxiliares u_{m,i} >=
t_m - R_i.w, u_{m,i} >= 0. Apilando los S niveles (cada uno con su propio
t_m y su fila de u, todos compartiendo el mismo w) se obtiene un unico
programa lineal cuyo optimo es exactamente V_beta*(w*) — la Proposicion 5
hecha computable.

Coste: N + S + S^2 variables (N activos, S escenarios). Crece como S^2,
por lo que esta formulacion se ofrece como VERIFICACION sobre ventanas de
tamano moderado (S de decenas), no como reemplazo del heuristico en el
backtesting de produccion (S=252 dias generaria ~63.500 variables
auxiliares). Ver el bloque __main__ para el uso recomendado.

Licencia: MIT.
"""
from __future__ import annotations
import numpy as np
from scipy.optimize import linprog


def _psi(beta: float, S: int) -> np.ndarray:
    s = np.arange(1, S + 1)
    return (s / S) ** beta - ((s - 1) / S) ** beta


def optimiza_cartera_lp(R: np.ndarray, beta: float, cap: float = 0.30):
    """Resuelve exactamente max_w V_beta(w) para beta>=1 (alpha<=1/2) como LP.

    R : matriz (S escenarios x N activos) de retornos.
    beta : exponente RIM (beta>=1 requerido; region coherente/convexa,
           Proposicion 3 y 5). Para beta<1 el problema no es convexo y
           debe resolverse con optimiza_cartera (SLSQP multi-start) de
           spectral_route.py.

    Devuelve (w_optimo, V_optimo), con V_optimo verificable de forma
    independiente evaluando V_beta(w_optimo, R, beta).
    """
    if beta < 1.0:
        raise ValueError(
            "optimiza_cartera_lp solo es valido para beta>=1 (alpha<=1/2, "
            "Prop. 5); para beta<1 el problema no es convexo."
        )
    S, N = R.shape
    psi = _psi(beta, S)
    d = np.clip(np.diff(np.concatenate([[0.0], psi])), 0.0, None)  # d_k, k=1..S

    n_w, n_t, n_u = N, S, S * S
    n_var = n_w + n_t + n_u

    def idx_u(m0: int, i: int) -> int:
        # m0 = m-1 (nivel m, 0-indexado); i = escenario, 0-indexado
        return n_w + n_t + m0 * S + i

    # Objetivo (minimizar -V): coef(t_m) = -d_k*m ; coef(u_{m,i}) = +d_k,
    # con k = S-m+1 (la biyeccion k<->m definida en la sumacion de Abel).
    c = np.zeros(n_var)
    for k in range(1, S + 1):
        dk = d[k - 1]
        if dk <= 0:
            continue
        m = S - k + 1
        c[n_w + (m - 1)] += -dk * m
        for i in range(S):
            c[idx_u(m - 1, i)] += dk

    # Restricciones u_{m,i} >= t_m - R_i.w  <=>  t_m - u_{m,i} - R_i.w <= 0
    A_ub_rows, b_ub = [], []
    for m in range(1, S + 1):
        for i in range(S):
            row = np.zeros(n_var)
            row[0:N] = -R[i, :]
            row[n_w + (m - 1)] = 1.0
            row[idx_u(m - 1, i)] = -1.0
            A_ub_rows.append(row)
            b_ub.append(0.0)

    A_eq = np.zeros((1, n_var)); A_eq[0, 0:N] = 1.0
    b_eq = np.array([1.0])
    bounds = [(0.0, cap)] * N + [(None, None)] * S + [(0.0, None)] * n_u

    res = linprog(np.array(c), A_ub=np.array(A_ub_rows), b_ub=np.array(b_ub),
                   A_eq=A_eq, b_eq=b_eq, bounds=bounds, method="highs")
    if not res.success:
        raise RuntimeError(f"LP no convergio: {res.message}")
    return res.x[0:N], float(-res.fun)


if __name__ == "__main__":
    import sys, os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
    from src.spectral_route import optimiza_cartera, V_beta
    from src.owa_core import beta_para_orness

    rng = np.random.default_rng(7)
    S, N = 40, 6
    R = rng.normal(0.0006, 0.018, size=(S, N))
    cap = 0.30

    print("Verificacion cruzada LP (Prop. 5) vs SLSQP multi-start "
          "(regimen coherente, beta>=1)")
    print(f"{'orness':>8} {'beta':>7} {'V_LP':>12} {'V_SLSQP':>12} "
          f"{'V_LP(w_SLSQP)':>14} {'dif_abs':>10}")
    peor_dif = 0.0
    for orness in (0.05, 0.10, 0.25, 0.40, 0.50):
        beta = beta_para_orness(orness, S)
        w_lp, V_lp = optimiza_cartera_lp(R, beta, cap=cap)
        w_sq, V_sq, _ = optimiza_cartera(R, beta, cap=cap, r_starts=40, seed=1)
        # doble verificacion: evaluar V_beta directamente sobre cada w
        V_lp_directo = V_beta(w_lp, R, beta)
        V_sq_directo = V_beta(w_sq, R, beta)
        dif = abs(V_lp_directo - V_sq_directo)
        peor_dif = max(peor_dif, dif)
        print(f"{orness:8.3f} {beta:7.3f} {V_lp_directo:12.6f} "
              f"{V_sq_directo:12.6f} {'':>14} {dif:10.2e}")
        assert abs(V_lp - V_lp_directo) < 1e-8, "el LP no reproduce su propio optimo"
        assert dif < 1e-4, (
            f"LP (cota superior certificada) y SLSQP deberian coincidir "
            f"en el regimen convexo; diferencia={dif:.2e} en orness={orness}"
        )
    print(f"\nOK: el heuristico SLSQP multi-start alcanza, dentro de "
          f"{peor_dif:.1e}, el optimo global que certifica el LP de la "
          f"Proposicion 5, en los {5} niveles de orness probados "
          f"(S={S} escenarios, N={N} activos, semilla=7).")
