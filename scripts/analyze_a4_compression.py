"""analyze_a4_compression.py — Compression limit of the regime-induced orness (article A4).

Reads results/iowa/por_ventana_<mk>.csv and ventanas_<mk>.csv (scripts/run_iowa.py and
scripts/analyze_iowa.py) and results/cap5/ventanas_<mk>_octiles.csv (static spectral route).
Reports, for each market: the number of active windows with a negative Spearman correlation
between orness and realised volatility in the adaptive and the static versions, and the
cross-section of the window of highest activation. Writes results/iowa/compresion_a4.json.
"""
import os, json
import pandas as pd

BASE = os.path.join(os.path.dirname(__file__), "..")
RES, CAP5 = f"{BASE}/results/iowa", f"{BASE}/results/cap5"
out = {}
for mk in ("US", "CO"):
    P = pd.read_csv(f"{RES}/por_ventana_{mk}.csv")
    act = P[P.activacion > 0]
    top = act.loc[act.activacion.idxmax()]
    A = pd.read_csv(f"{RES}/ventanas_{mk}.csv")
    S = pd.read_csv(f"{CAP5}/ventanas_{mk}_octiles.csv"); S = S[S.via == "espectral"]
    a = A[A.t == top.t].set_index("perfil"); s = S[S.t == top.t].set_index("perfil")
    out[mk] = {
        "n_activas": int(len(act)),
        "n_rho_negativa_adaptativa": int((act.rho_ad < 0).sum()),
        "n_rho_negativa_estatica": int((act.rho_es < 0).sum()),
        "ventana_max_activacion": {
            "fecha": str(top.fecha), "activacion": float(top.activacion),
            "rho_adaptativa": float(top.rho_ad), "rho_estatica": float(top.rho_es),
            "orness_efectivo": a["orness_efectivo"].round(4).to_dict(),
            "vol_adaptativa_pct": (100 * a["vol"]).round(2).to_dict(),
            "vol_estatica_pct": (100 * s["vol"]).round(2).to_dict()}}
json.dump(out, open(f"{RES}/compresion_a4.json", "w"), indent=1, ensure_ascii=False)
print(json.dumps(out, indent=1, ensure_ascii=False))
