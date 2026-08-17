"""
verify_nesting.py — Verificacion numerica del Hallazgo 4 (Proposicion 4,
Anexo B.7 de la tesis): anidamiento de CVaR y del maximin de Wald como
casos limite del operador espectral V_beta.

La Proposicion 4 afirma dos casos limite del cuantificador RIM Q(P)=P^beta
sobre los resultados ordenados de la cartera (Definicion 6):

  (a) beta -> infinito: V_beta converge al maximin de Wald, es decir, al
      peor escenario individual de la cartera (min(R@w)). Q(P)=P^beta
      colapsa a un salto en P=1 cuando beta crece sin cota, concentrando
      todo el peso espectral en el escenario mas desfavorable.

  (b) El cuantificador "escalon" (peso uniforme 1/m sobre los m peores
      escenarios de S, cero en el resto) reproduce exactamente el CVaR de
      los m peores escenarios (Average Value-at-Risk), calculado de forma
      INDEPENDIENTE con la formula directa: la media aritmetica de los m
      retornos mas bajos de la cartera.

Ambas afirmaciones se presentaban en el Anexo B solo como argumento
analitico/textual, sin verificacion computacional en el repositorio; este
script las convierte en pruebas numericas reproducibles, en linea con el
resto del programa (ver tambien spectral_lp.py, Proposicion 5, que usa la
misma formula de Rockafellar-Uryasev para el LP del regimen coherente).

Uso:  python scripts/verify_nesting.py
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import numpy as np
import pandas as pd
from src.spectral_route import V_beta

SEED = 20260817


def V_espectral(rp_desc, psi):
    """Funcional espectral generico: suma psi_s * r_(s), con r ya
    ordenado de mejor a peor (descendente). psi debe sumar 1 y ser >= 0
    (es una medida de probabilidad sobre el ranking de escenarios)."""
    assert abs(psi.sum() - 1.0) < 1e-9, "psi debe sumar 1"
    assert (psi >= -1e-12).all(), "psi debe ser no negativo"
    return float(np.dot(psi, rp_desc))


def psi_escalon_peor_m(S, m):
    """Cuantificador escalon: peso uniforme 1/m sobre los m PEORES
    escenarios (las ultimas m posiciones del orden descendente), cero en
    el resto. Equivale a Q_m(P) = clip((P - (S-m)/S) * S/m, 0, 1)."""
    psi = np.zeros(S)
    psi[S - m:] = 1.0 / m
    return psi


def parte_a_wald(seed=SEED, S=200, N=8,
                 betas=(10, 100, 1_000, 10_000, 100_000)):
    """(a) V_beta(w) -> min(R@w) cuando beta -> infinito (Wald maximin)."""
    rng = np.random.default_rng(seed)
    R = rng.normal(0.0006, 0.018, size=(S, N))
    w = rng.dirichlet(np.ones(N))
    peor_real = float(np.min(R @ w))
    filas = []
    for beta in betas:
        v = V_beta(w, R, beta)
        filas.append({"beta": beta, "V_beta": v, "min(Rw)_Wald": peor_real,
                      "dif_abs": abs(v - peor_real)})
    return pd.DataFrame(filas), peor_real


def parte_b_cvar(seed=SEED, S=200, N=8, ms=(1, 5, 10, 20, 50, 100)):
    """(b) el cuantificador escalon (peso 1/m en los m peores) coincide
    con el CVaR_m calculado directamente (media de los m peores retornos,
    formula de Rockafellar-Uryasev)."""
    rng = np.random.default_rng(seed + 1)
    R = rng.normal(0.0006, 0.018, size=(S, N))
    w = rng.dirichlet(np.ones(N))
    rp_asc = np.sort(R @ w)            # ascendente: el peor primero
    rp_desc = rp_asc[::-1]             # descendente: convencion de V_beta
    filas = []
    for m in ms:
        cvar_directo = float(np.mean(rp_asc[:m]))
        v_escalon = V_espectral(rp_desc, psi_escalon_peor_m(S, m))
        filas.append({"m": m, "CVaR_directo": cvar_directo,
                      "V_escalon": v_escalon,
                      "dif_abs": abs(cvar_directo - v_escalon)})
    return pd.DataFrame(filas)


if __name__ == "__main__":
    os.makedirs("results", exist_ok=True)

    print("=== Parte (a): anidamiento del maximin de Wald (beta -> infinito) ===")
    df_a, peor_real = parte_a_wald()
    print(df_a.to_string(index=False))
    dif_final_a = float(df_a["dif_abs"].iloc[-1])
    assert dif_final_a < 1e-6, (
        f"V_beta no converge al minimo de la cartera cuando beta crece: "
        f"diferencia final = {dif_final_a:.2e}")
    print(f"OK: con beta={int(df_a['beta'].iloc[-1])}, V_beta coincide con "
          f"min(R@w)={peor_real:.6f} hasta {dif_final_a:.2e}.\n")

    print("=== Parte (b): anidamiento del CVaR (cuantificador escalon) ===")
    df_b = parte_b_cvar()
    print(df_b.to_string(index=False))
    peor_dif_b = float(df_b["dif_abs"].max())
    assert peor_dif_b < 1e-9, (
        f"el cuantificador escalon no reproduce el CVaR directo: "
        f"diferencia maxima = {peor_dif_b:.2e}")
    print(f"OK: el funcional espectral con cuantificador escalon coincide "
          f"con la formula directa de CVaR (Rockafellar-Uryasev) hasta "
          f"{peor_dif_b:.2e}, para m en {list(df_b['m'])} de S=200 "
          f"escenarios.\n")

    df_a.to_csv("results/verificacion_nesting_wald.csv", index=False)
    df_b.to_csv("results/verificacion_nesting_cvar.csv", index=False)
    print("Guardado: results/verificacion_nesting_wald.csv, "
          "results/verificacion_nesting_cvar.csv")
