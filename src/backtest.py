"""
backtest.py — Ventanas rodantes out-of-sample, neto de costos, y universos.

Estimacion de 252 dias, rebalanceo mensual (21 dias), costo de transaccion
~10 pb por unidad de rotacion. Devuelve, para cada perfil, la serie de retornos
OOS y la metrica realizada por ventana (para la inferencia de coherencia).

Licencia: MIT.
"""
from __future__ import annotations
import numpy as np
import pandas as pd
import yfinance as yf

TICKERS_US = ["AAPL", "MSFT", "AMZN", "GOOGL", "META", "NVDA", "JPM", "JNJ", "PG", "KO",
              "XOM", "CVX", "WMT", "HD", "UNH", "V", "MA", "DIS", "PFE", "CSCO",
              "PEP", "MRK", "ABT", "T", "INTC"]

TICKERS_CO = ["ECOPETROL.CL", "GRUPOSURA.CL", "GRUPOARGOS.CL", "ISA.CL", "CEMARGOS.CL",
              "BOGOTA.CL", "CELSIA.CL", "NUTRESA.CL", "GRUPOAVAL.CL", "PFAVAL.CL",
              "PFDAVVNDA.CL", "PROMIGAS.CL", "MINEROS.CL", "CORFICOLCF.CL", "ENKA.CL",
              "BCOLOMBIA.CL", "GEB.CL", "TERPEL.CL"]


def cargar(mercado="US", inicio="2015-01-01", fin="2025-01-01"):
    tk = TICKERS_US if mercado == "US" else TICKERS_CO
    raw = yf.download(tk, start=inicio, end=fin, auto_adjust=True, progress=False)
    close = raw["Close"].dropna(axis=1, how="all")
    close = close[close.columns[close.notna().mean() > 0.8]].dropna()
    volume = raw["Volume"].reindex(index=close.index, columns=close.columns).fillna(0.0)
    return close, volume


def max_drawdown(r):
    eq = np.cumprod(1 + r)
    return float((eq / np.maximum.accumulate(eq) - 1).min())


def backtest(close, volume, pesos_fn, lookback=252, step=21, tc=0.0010):
    """pesos_fn(close_win, volume_win) -> vector de pesos. Devuelve dict con
    'serie' (retornos OOS netos concatenados) y 'por_ventana' (lista de
    {'ret','vol','dd'} realizados en cada ventana OOS)."""
    n = len(close)
    series, por_ventana = [], []
    w_prev = None
    for t in range(lookback, n - step, step):
        cw, vw = close.iloc[t - lookback:t], volume.iloc[t - lookback:t]
        w = pesos_fn(cw, vw)
        rot = 0.0 if w_prev is None else np.abs(w - w_prev).sum()
        w_prev = w
        fut = close.iloc[t:t + step].pct_change().dropna().values @ w
        if len(fut):
            fut = fut.copy(); fut[0] -= tc * rot      # costo aplicado al rebalanceo
            series.append(fut)
            por_ventana.append({
                "ret": float(fut.mean() * 252),
                "vol": float(fut.std(ddof=1) * np.sqrt(252)) if len(fut) > 1 else np.nan,
                "dd": max_drawdown(fut),
            })
    serie = np.concatenate(series) if series else np.array([])
    return {"serie": serie, "por_ventana": por_ventana}


def resumen(serie):
    v = serie.std(ddof=1) * np.sqrt(252)
    mu = serie.mean() * 252
    return {"Ret%": mu * 100, "Vol%": v * 100,
            "Sharpe": mu / v if v > 0 else 0.0, "Caida": max_drawdown(serie)}
