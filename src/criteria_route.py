"""
criteria_route.py — Vía de criterios (base de la industria; resultado de inversión).

Aplica el orness sobre los m=4 criterios financieros normalizados de cada activo
(Def. 5). Es la integral de Choquet respecto a una capacidad simétrica: mide
exigencia multicriterio (AND/OR), no aversión al riesgo (Prop. 2). La selección
top-k y la asignación se gobiernan por el orness.

Licencia: MIT.
"""
from __future__ import annotations
import numpy as np
import pandas as pd
from .owa_core import pesos_rim, beta_para_orness


def criterios(close, volume):
    """Matriz N x 4 de criterios normalizados [0,1] (mayor = mejor):
    rentabilidad, baja volatilidad, baja caida, liquidez."""
    r = close.pct_change().dropna()
    eq = (1 + r).cumprod()
    df = pd.DataFrame({
        "ret": r.mean() * 252,
        "vol": r.std(ddof=1) * np.sqrt(252),
        "dd": (eq / eq.cummax() - 1).min(),
        "liq": (close * volume).reindex(r.index).mean(),
    })

    def mm(x):
        x = x.astype(float); rng = x.max() - x.min()
        return pd.Series(0.5, index=x.index) if rng == 0 else (x - x.min()) / rng

    return np.column_stack([mm(df["ret"]), 1 - mm(df["vol"]), mm(df["dd"]), mm(df["liq"])])


def puntajes(C, beta):
    """Puntaje OWA por activo: s_i = sum_j w_j(beta) c_i,(j)."""
    n = C.shape[1]
    w = pesos_rim(beta, n)
    return np.array([np.dot(w, np.sort(row)[::-1]) for row in C])


def _inv_vol(sel, close):
    r = close.iloc[:, sel].pct_change().dropna()
    v = r.std(ddof=1).values
    iv = np.where(v > 0, 1.0 / np.where(v > 0, v, 1), 0.0)
    return iv / iv.sum() if iv.sum() > 0 else np.full(len(sel), 1.0 / len(sel))


def asignar(scores, close, orness, k):
    """Selección top-k y asignación gobernada por el orness (agresivo concentra
    por puntaje; conservador pondera inverso-volatilidad)."""
    sel = np.argsort(scores)[::-1][:k]
    sc = np.clip(scores[sel], 0, None)
    wsc = sc / sc.sum() if sc.sum() > 0 else np.full(k, 1.0 / k)
    blend = orness * wsc + (1 - orness) * _inv_vol(sel, close)
    w = np.zeros(len(scores)); w[sel] = blend / blend.sum()
    return w


def pesos_criterios(close, volume, orness, k=8):
    """Cartera de la vía de criterios para un orness dado (beta con n=4)."""
    beta = beta_para_orness(orness, 4)
    return asignar(puntajes(criterios(close, volume), beta), close, orness, k)
