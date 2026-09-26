"""
backtest.py — Ventanas rodantes fuera de muestra, neto de costos, y comparadores.

Protocolo (tesis, §5.1): estimación con 252 días hábiles, rebalanceo cada 21
días, costo proporcional de 10 pb por unidad de rotación cargado el primer día
de cada periodo de tenencia. La rotación se mide contra los pesos de la cartera
anterior DESPUÉS de su deriva por los rendimientos del periodo.

Comparadores: 1/N y cartera de media-varianza de Markowitz en su versión de
máxima razón de Sharpe (tasa libre de riesgo nula), ambos con el mismo tope de
concentración que el operador.

Versión 1.1.0: todas las estrategias del Capítulo 5 pasan por esta función
(en la v1.0.0 los guiones reimplementaban el bucle sin costos).

Licencia: MIT.
"""
from __future__ import annotations
import numpy as np
from scipy.optimize import minimize

LOOKBACK, STEP, TC, CAP = 252, 21, 0.0010, 0.30


def max_drawdown(r):
    eq = np.cumprod(1 + np.asarray(r, float))
    return float((eq / np.maximum.accumulate(eq) - 1).min())


def rebalanceos(n, lookback=LOOKBACK, step=STEP):
    return list(range(lookback, n - step, step))


def backtest(close, pesos_fn, lookback=LOOKBACK, step=STEP, tc=TC):
    """pesos_fn(t, R_in) -> vector de pesos, con R_in = rendimientos (lookback x N).
    Devuelve dict: 'serie' (rendimientos diarios netos), 'fechas', 'por_ventana'
    (lista de dicts con t, fecha, ret, vol, dd, rotacion) y 'pesos'."""
    ret = close.pct_change().values
    fechas = close.index
    n = len(close)
    series, f_series, por_ventana, pesos = [], [], [], []
    w_deriva = None
    for t in rebalanceos(n, lookback, step):
        R_in = ret[t - lookback + 1:t + 1]           # rendimientos observados hasta t (inclusive)
        w = np.asarray(pesos_fn(t, R_in), float)
        rot = float(np.abs(w).sum()) if w_deriva is None else float(np.abs(w - w_deriva).sum())
        fut = ret[t + 1:t + 1 + step]                # periodo de tenencia estrictamente posterior
        rp = fut @ w
        rp = rp.copy(); rp[0] -= tc * rot
        crec = np.prod(1 + fut, axis=0) * w
        w_deriva = crec / crec.sum() if crec.sum() > 0 else w
        series.append(rp); f_series.append(fechas[t + 1:t + 1 + step])
        pesos.append(w)
        por_ventana.append({"t": t, "fecha": str(fechas[t].date()),
                            "ret": float(rp.mean() * 252),
                            "vol": float(rp.std(ddof=1) * np.sqrt(252)),
                            "dd": max_drawdown(rp), "rotacion": rot})
    return {"serie": np.concatenate(series), "fechas": np.concatenate(f_series),
            "por_ventana": por_ventana, "pesos": np.array(pesos)}


def resumen(serie):
    serie = np.asarray(serie, float)
    v = serie.std(ddof=1) * np.sqrt(252)
    mu = serie.mean() * 252
    return {"Ret%": mu * 100, "Vol%": v * 100, "Sharpe": mu / v if v > 0 else 0.0,
            "CaidaMax%": max_drawdown(serie) * 100}


def pesos_1N(t, R_in):
    N = R_in.shape[1]
    return np.full(N, 1.0 / N)


def pesos_markowitz(t, R_in, cap=CAP):
    """Máxima razón de Sharpe (rf = 0), largo solamente, tope cap."""
    mu = R_in.mean(axis=0) * 252
    Sig = np.cov(R_in, rowvar=False) * 252
    N = len(mu)

    def f(w):
        m = mu @ w; s = np.sqrt(w @ Sig @ w)
        return -m / s

    res = minimize(f, np.full(N, 1.0 / N), method="SLSQP", bounds=[(0.0, cap)] * N,
                   constraints=({"type": "eq", "fun": lambda w: w.sum() - 1.0},),
                   options={"maxiter": 500, "ftol": 1e-12})
    w = np.clip(res.x, 0, cap)
    return w / w.sum()
