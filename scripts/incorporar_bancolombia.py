"""
incorporar_bancolombia.py — Incorpora al universo colombiano del snapshot la acción
preferencial de Bancolombia, que el universo definido de antemano incluía.

Tras la reorganización societaria de Bancolombia como Grupo Cibest (2025), la fuente
(Yahoo Finance, endpoint chart) publica la historia completa de la acción preferencial
desde 2015 bajo el símbolo vigente PFCIBEST.CL; el símbolo anterior (PFBCOLOM.CL) ya
no devuelve serie. El valor es el mismo; cambia solo su símbolo.

El guion descarga la serie con el mismo endpoint, periodo y campos que el resto del
snapshot (cierre ajustado por dividendos y splits, volumen diario), guarda la
respuesta cruda y añade la columna PFCIBEST.CL a co_prices_snapshot.csv y
co_volume_snapshot.csv sobre el mismo índice de fechas, sin rellenar.

Uso: python scripts/incorporar_bancolombia.py
"""
import hashlib, os, time
import pandas as pd, requests

SNAP = os.path.join(os.path.dirname(__file__), "..", "data", "snapshot_2026-08-31")
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36"
TICKER, START, END = "PFCIBEST.CL", "2015-01-01", "2025-01-02"


def descargar():
    p1 = int(pd.Timestamp(START, tz="UTC").timestamp()); p2 = int(pd.Timestamp(END, tz="UTC").timestamp())
    for a in range(5):
        try:
            r = requests.get(f"https://query2.finance.yahoo.com/v8/finance/chart/{TICKER}",
                             params={"period1": p1, "period2": p2, "interval": "1d", "events": "div,splits"},
                             headers={"User-Agent": UA}, timeout=30)
            res = r.json()["chart"]["result"][0]
            idx = pd.to_datetime(res["timestamp"], unit="s", utc=True).tz_convert(
                res["meta"]["exchangeTimezoneName"]).tz_localize(None).normalize()
            q = res["indicators"]["quote"][0]
            df = pd.DataFrame({"close": q["close"], "adjclose": res["indicators"]["adjclose"][0]["adjclose"],
                               "volume": q["volume"]}, index=idx)
            return df[~df.index.duplicated(keep="last")]
        except Exception:
            time.sleep(3 * (a + 1))
    raise RuntimeError("sin serie para " + TICKER)


def sha16(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()[:16]


if __name__ == "__main__":
    raw = descargar()
    raw.to_csv(os.path.join(SNAP, "raw_PFCIBEST.CL.csv"), index_label="fecha")
    for nombre, campo in (("co_prices_snapshot.csv", "adjclose"), ("co_volume_snapshot.csv", "volume")):
        p = os.path.join(SNAP, nombre)
        df = pd.read_csv(p, index_col=0, parse_dates=True)
        if TICKER in df.columns:
            df = df.drop(columns=TICKER)
        s = raw[campo].reindex(df.index)
        if campo == "volume":
            s = s.fillna(0.0)
        df.insert(0, TICKER, s)
        df.to_csv(p)
        print(nombre, df.shape, "cobertura", round(float(s.notna().mean()), 4), "sha256[:16]", sha16(p))
    print("fecha de descarga (UTC):", pd.Timestamp.utcnow().strftime("%Y-%m-%dT%H:%MZ"))
