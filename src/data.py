"""
data.py — Carga del snapshot versionado de precios y volúmenes (2015-2024).

El snapshot `data/snapshot_2026-08-31/` congela, con fecha y checksum, las
series usadas en el Capítulo 5 y en la corrida IOWA de la tesis (el mismo
universo en ambos). Ver data/README.md y el MANIFEST del snapshot.

Convenciones:
- Precios ajustados por splits y dividendos (Yahoo Finance, endpoint chart).
- Se descartan las fechas sin negociación del mercado: (i) días en que menos de
  la mitad de los emisores registra volumen positivo (en la BVC el endpoint
  rellena festivos con el precio previo, lo que inyectaría rendimientos nulos) y
  (ii) días en que todos los emisores repiten el precio del día anterior
  (registros duplicados o festivos no marcados).
- Los huecos residuales de precio se rellenan hacia adelante (ffill).

Licencia: MIT.
"""
from __future__ import annotations
import os
import pandas as pd

SNAP = os.path.join(os.path.dirname(__file__), "..", "data", "snapshot_2026-08-31")
FIN = "2024-12-31"


def cargar(mercado: str = "US"):
    """Devuelve (close, volume) del snapshot para 'US' o 'CO'."""
    mk = mercado.lower()
    px = pd.read_csv(os.path.join(SNAP, f"{mk}_prices_snapshot.csv"), index_col=0, parse_dates=True)
    vol = pd.read_csv(os.path.join(SNAP, f"{mk}_volume_snapshot.csv"), index_col=0, parse_dates=True)
    px = px.loc[:FIN].sort_index()
    vol = vol.reindex(px.index).fillna(0.0)
    activo = (vol > 0).mean(axis=1) >= 0.5
    px, vol = px[activo].ffill().dropna(axis=0, how="any"), vol[activo]
    # Días sin información nueva: todos los emisores repiten el precio del día anterior
    # (registros duplicados o festivos no marcados por la fuente).
    r = px.pct_change()
    nulo = r.notna().all(axis=1) & (r.abs().sum(axis=1) == 0)
    px = px[~nulo]
    vol = vol.reindex(px.index)
    return px, vol
