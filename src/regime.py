"""
regime.py — Índice de estrés de régimen y orness efectivo inducido por régimen
(tesis: Definiciones 5 y 6, §4.5; corrida del §8.4).

Índice de estrés (Definición 5). Para cada fecha t:
    z_VIX(t) y z_EPU(t): estandarización causal con media y desviación móviles
    de 252 días hábiles que terminan en t;
    s(t) = 0,6 * Λ(z_VIX(t)) + 0,4 * Λ(z_EPU(t)),   Λ(z) = 1 / (1 + e^{-z}).
El EPU mensual de Baker, Bloom y Davis (2016) se incorpora con rezago de
publicación: el valor del mes m se conoce a partir del primer día del mes m+1
(FRED fecha cada observación el día 1 del mes que promedia).

Activación (Definición 6). La modulación actúa solo por encima del umbral de
estrés s0 = 0,55 (frontera entre los regímenes «normal» y «estrés»):
    a(t) = clip((s(t) - s0) / (1 - s0), 0, 1)
    alpha_eff(t) = alpha - lambda * a(t) * max(0, alpha - alpha_min)
con lambda = 0,85 y alpha_min = 0,12 (valores fijados en el diseño previo a la
corrida). Así alpha_eff(t) <= alpha para todo t, alpha_eff = alpha en calma y
normalidad, y el orden entre perfiles se conserva (alpha_eff es creciente en alpha).

Licencia: MIT.
"""
from __future__ import annotations
import os
import numpy as np
import pandas as pd

SNAP = os.path.join(os.path.dirname(__file__), "..", "data", "snapshot_2026-08-31")
W_VIX, VENTANA, S0, LAMBDA, ALPHA_MIN = 0.6, 252, 0.55, 0.85, 0.12
UMBRALES = (0.35, 0.55, 0.75)
ETIQUETAS = ("calma", "normal", "estres", "crisis")


def _z_causal(x: pd.Series, ventana=VENTANA) -> pd.Series:
    mu = x.rolling(ventana, min_periods=20).mean()
    sd = x.rolling(ventana, min_periods=20).std(ddof=0).replace(0, np.nan)
    return ((x - mu) / sd).fillna(0.0)


def senales(fechas: pd.DatetimeIndex) -> pd.DataFrame:
    """VIX diario y EPU con rezago de publicación, alineados a `fechas`."""
    vix = pd.read_csv(os.path.join(SNAP, "vix_raw.csv"))
    vix.columns = ["fecha", "VIX"]; vix["fecha"] = pd.to_datetime(vix["fecha"])
    vix = pd.to_numeric(vix.set_index("fecha")["VIX"], errors="coerce").dropna()
    epu = pd.read_csv(os.path.join(SNAP, "epu_raw.csv"))
    epu.columns = ["fecha", "EPU"]; epu["fecha"] = pd.to_datetime(epu["fecha"])
    epu = epu.set_index("fecha")["EPU"].astype(float)
    epu.index = epu.index + pd.offsets.MonthBegin(1)        # disponible desde el mes siguiente
    todas = fechas.union(vix.index).union(epu.index)
    df = pd.DataFrame({"VIX": vix.reindex(todas).ffill(), "EPU": epu.reindex(todas).ffill()})
    return df.reindex(fechas).ffill().bfill()


def indice_estres(fechas: pd.DatetimeIndex) -> pd.DataFrame:
    df = senales(fechas)
    lam = lambda z: 1.0 / (1.0 + np.exp(-z))
    df["s"] = W_VIX * lam(_z_causal(df["VIX"])) + (1 - W_VIX) * lam(_z_causal(df["EPU"]))
    df["activacion"] = ((df["s"] - S0) / (1 - S0)).clip(0, 1)
    cortes = [-np.inf, *UMBRALES, np.inf]
    df["regimen"] = pd.cut(df["s"], cortes, labels=ETIQUETAS, right=False).astype(str)
    return df


def orness_efectivo(alpha: float, activacion: float, lam=LAMBDA, alpha_min=ALPHA_MIN) -> float:
    return float(alpha - lam * activacion * max(0.0, alpha - alpha_min))
