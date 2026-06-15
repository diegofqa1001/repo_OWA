"""
inference.py — Inferencia de coherencia conductual (revisión Q1 corregida).

Unidad de analisis correcta: la VENTANA (no el bootstrap por bloques, que
remuestrea la dimension equivocada). Dos pruebas complementarias:
 (A) Monotonia POR VENTANA: rho de Spearman(orness, metrica) por ventana;
     significancia del rho medio por Newey-West (rezago automatico NW 1994) y
     prueba de signo binomial sobre el % de ventanas coherentes.
 (B) Permutacion de la asignacion perfil->orness (corte transversal de 8 perfiles).
Tambien Diebold-Mariano (Newey-West) entre estrategias.

Licencia: MIT.
"""
from __future__ import annotations
import numpy as np
from scipy.stats import spearmanr, binomtest, norm


def nw_lag(n):
    """Rezago automatico de Newey-West (1994): floor(4 (n/100)^(2/9))."""
    return int(np.floor(4 * (n / 100.0) ** (2.0 / 9.0)))


def nw_tstat(x, lag=None):
    """t de la media de x con varianza HAC de Newey-West."""
    x = np.asarray(x, float); x = x[~np.isnan(x)]
    n = len(x); mu = x.mean(); e = x - mu
    if lag is None:
        lag = nw_lag(n)
    g0 = np.dot(e, e) / n
    s = g0
    for L in range(1, lag + 1):
        w = 1.0 - L / (lag + 1.0)
        g = np.dot(e[L:], e[:-L]) / n
        s += 2 * w * g
    se = np.sqrt(s / n)
    return mu, (mu / se if se > 0 else np.nan), lag


def monotonia_por_ventana(orness_vec, metrica_por_ventana):
    """orness_vec: array (8,). metrica_por_ventana: array (n_ventanas, 8).
    Devuelve rho medio, t de NW, lag, % de ventanas con rho>0 y p binomial."""
    rhos = np.array([spearmanr(orness_vec, fila)[0] for fila in metrica_por_ventana])
    rhos = rhos[~np.isnan(rhos)]
    mu, t, lag = nw_tstat(rhos)
    pos = int(np.sum(rhos > 0)); n = len(rhos)
    pb = binomtest(pos, n, 0.5).pvalue
    return {"rho_medio": mu, "t_NW": t, "lag": lag,
            "pct_ventanas_pos": 100.0 * pos / n, "p_binomial": pb, "n_ventanas": n}


def permutacion(orness_vec, metrica_media, n_perm=20000, seed=42):
    """Test de permutacion: rho observado vs etiquetas de orness barajadas.
    metrica_media: array (8,) con la metrica promedio por perfil."""
    rng = np.random.default_rng(seed)
    rho_obs = spearmanr(orness_vec, metrica_media)[0]
    cnt = 0
    for _ in range(n_perm):
        if abs(spearmanr(rng.permutation(orness_vec), metrica_media)[0]) >= abs(rho_obs):
            cnt += 1
    return {"rho_obs": rho_obs, "p_perm": (cnt + 1) / (n_perm + 1)}


def diebold_mariano(loss_a, loss_b, lag=None):
    """DM con varianza NW sobre la diferencia de perdidas d = loss_a - loss_b.
    t<0 indica que la estrategia A pierde menos (mejor)."""
    d = np.asarray(loss_a, float) - np.asarray(loss_b, float)
    mu, t, lag = nw_tstat(d, lag)
    p = 2 * (1 - norm.cdf(abs(t)))
    return {"dbar": mu, "t": t, "p": p, "lag": lag}
