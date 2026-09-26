"""fetch_volume.py — Descarga el volumen diario (endpoint chart de Yahoo Finance)
para los mismos emisores del snapshot de precios y lo congela junto a él.

Uso: python scripts/fetch_volume.py
Escribe data/snapshot_2026-08-31/{us,co}_volume_snapshot.csv
"""
import time, sys, requests
import pandas as pd

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36"
SNAP = "data/snapshot_2026-08-31"
START, END = "2015-01-01", "2025-01-02"


def fetch_volume(ticker, retries=5):
    p1 = int(pd.Timestamp(START, tz="UTC").timestamp()); p2 = int(pd.Timestamp(END, tz="UTC").timestamp())
    url = f"https://query2.finance.yahoo.com/v8/finance/chart/{ticker}"
    for a in range(retries):
        try:
            r = requests.get(url, params={"period1": p1, "period2": p2, "interval": "1d"}, headers={"User-Agent": UA}, timeout=30)
            res = r.json()["chart"]["result"][0]
            idx = pd.to_datetime(res["timestamp"], unit="s", utc=True).tz_convert(
                res["meta"].get("exchangeTimezoneName", "America/New_York")).tz_localize(None).normalize()
            s = pd.Series(res["indicators"]["quote"][0]["volume"], index=idx, name=ticker, dtype=float)
            return s[~s.index.duplicated(keep="last")]
        except Exception as e:
            time.sleep(3 * (a + 1))
    raise RuntimeError(f"sin volumen para {ticker}")


if __name__ == "__main__":
    for mk in ("us", "co"):
        px = pd.read_csv(f"{SNAP}/{mk}_prices_snapshot.csv", index_col=0, parse_dates=True)
        cols = {}
        for t in px.columns:
            cols[t] = fetch_volume(t); print(mk, t, len(cols[t])); time.sleep(0.8)
        vol = pd.DataFrame(cols).reindex(px.index).fillna(0.0)
        vol.to_csv(f"{SNAP}/{mk}_volume_snapshot.csv")
        print("guardado", mk, vol.shape, "cobertura>0:", (vol > 0).mean().round(2).min())
