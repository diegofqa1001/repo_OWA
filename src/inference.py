"""
inference.py — Inferencia de coherencia conductual y comparación de estrategias.

(A) Monotonía por ventana: rho de Spearman(orness, volatilidad realizada) en cada
    ventana; media con error estándar HAC de Newey-West (rezago automático de
    Newey y West, 1994) y prueba de signos binomial sobre la proporción de
    ventanas con rho > 0.
(B) Permutación EXACTA del orden de perfiles: rho de Spearman entre el orness y
    la volatilidad media por perfil, contra las 8! = 40 320 reasignaciones
    (bilateral, sobre |rho|).
(C) Diebold-Mariano con varianza de Newey-West y corrección de muestra pequeña
    de Harvey, Leybourne y Newbold (1997), distribución t de Student con T-1 gl.

Licencia: MIT.
"""
from __future__ import annotations
from itertools import permutations
import numpy as np
from scipy.stats import spearmanr, binomtest, t as tdist, rankdata


def nw_lag(n):
    """Rezago automático de Newey-West (1994): floor(4 (n/100)^(2/9))."""
    return int(np.floor(4 * (n / 100.0) ** (2.0 / 9.0)))


def nw_var_media(x, lag):
    x = np.asarray(x, float); n = len(x); e = x - x.mean()
    s = np.dot(e, e) / n
    for L in range(1, lag + 1):
        s += 2 * (1.0 - L / (lag + 1.0)) * np.dot(e[L:], e[:-L]) / n
    return s / n


def nw_tstat(x, lag=None):
    x = np.asarray(x, float); x = x[~np.isnan(x)]
    lag = nw_lag(len(x)) if lag is None else lag
    se = np.sqrt(nw_var_media(x, lag))
    return float(x.mean()), float(x.mean() / se) if se > 0 else np.nan, lag


def monotonia_por_ventana(orness_vec, metrica_por_ventana):
    rhos = np.array([spearmanr(orness_vec, fila)[0] for fila in metrica_por_ventana])
    rhos = rhos[~np.isnan(rhos)]
    mu, t, lag = nw_tstat(rhos)
    pos = int(np.sum(rhos > 0)); n = len(rhos)
    return {"rho_medio": mu, "t_NW": t, "p_NW": float(2 * tdist.sf(abs(t), n - 1)), "lag": lag,
            "pct_ventanas_pos": 100.0 * pos / n, "p_binomial": binomtest(pos, n, 0.5).pvalue,
            "n_ventanas": n, "rhos": rhos}


def permutacion_exacta(orness_vec, metrica_media):
    """Permutación exacta sobre las k! asignaciones (k = 8 -> 40 320)."""
    r_o = rankdata(orness_vec); r_m = rankdata(metrica_media)
    k = len(r_o)
    def rho(a, b):
        a = a - a.mean(); b = b - b.mean()
        return float(a @ b / np.sqrt((a @ a) * (b @ b)))
    rho_obs = rho(r_o, r_m)
    cnt = tot = 0
    for p in permutations(range(k)):
        tot += 1
        if abs(rho(r_o[list(p)], r_m)) >= abs(rho_obs) - 1e-12:
            cnt += 1
    return {"rho_obs": rho_obs, "p_perm": cnt / tot, "n_perm": tot}


def diebold_mariano(loss_a, loss_b, h=1):
    """DM-HLN. d = loss_a - loss_b; dbar < 0 indica que A tiene menor pérdida.
    Devuelve estadístico, p bilateral y p unilaterales."""
    d = np.asarray(loss_a, float) - np.asarray(loss_b, float)
    d = d[~np.isnan(d)]; T = len(d)
    lag = max(h - 1, nw_lag(T))
    dm = d.mean() / np.sqrt(nw_var_media(d, lag))
    hln = np.sqrt((T + 1 - 2 * h + h * (h - 1) / T) / T)
    s = dm * hln
    return {"dbar": float(d.mean()), "DM_HLN": float(s), "p_bilateral": float(2 * tdist.sf(abs(s), T - 1)),
            "p_A_menor": float(tdist.cdf(s, T - 1)), "p_A_mayor": float(tdist.sf(s, T - 1)),
            "T": T, "lag": lag}
