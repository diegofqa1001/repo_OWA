"""
owa_core.py — Núcleo OWA / RIM y anclas conductuales.

Definiciones 1-4 y Proposición 1 del Artículo 3: operador OWA (Yager, 1988),
orness, pesos RIM Q(r)=r^beta (Yager, 1996), orness exacto por suma de Abel y
calibración beta*(alpha, n). Las anclas de orness por perfil provienen del
Artículo 2 (taxonomía difusa validada de 8 perfiles).

Licencia: MIT.
"""
from __future__ import annotations
import numpy as np
from scipy.optimize import brentq

# Anclas de orness por perfil (Artículo 2, Tabla 5)
ORNESS_PERFIL = {
    "Guardian": 0.158, "Sentinel": 0.257, "Pragmatist": 0.503, "Analyst": 0.600,
    "Strategist": 0.647, "Adventurer": 0.693, "Innovator": 0.738, "Visionary": 0.865,
}
PERFILES = list(ORNESS_PERFIL)


def pesos_rim(beta, n):
    """Vector de pesos RIM (Def. 3): w_j = (j/n)^beta - ((j-1)/n)^beta."""
    j = np.arange(1, n + 1)
    w = (j / n) ** beta - ((j - 1) / n) ** beta
    return w / w.sum()


def owa(a, w):
    """Operador OWA (Def. 1): F_w(a) = sum_j w_j a_(j), orden decreciente."""
    return float(np.dot(w, np.sort(a)[::-1]))


def orness_de_pesos(w):
    """orness(w) = (n-1)^-1 sum_j (n-j) w_j  (Def. 2)."""
    n = len(w)
    j = np.arange(1, n + 1)
    return float(np.dot(n - j, w) / (n - 1))


def orness_n(beta, n):
    """orness exacto del vector RIM (Prop. 1, Abel): (n-1)^-1 sum_{j=1}^{n-1} (j/n)^beta."""
    j = np.arange(1, n)
    return float((1.0 / (n - 1)) * np.sum((j / n) ** beta))


def beta_para_orness(alpha, n):
    """beta*(alpha, n): unico beta con orness_n(beta) = alpha (Prop. 1, brentq)."""
    if not 0.0 < alpha < 1.0:
        raise ValueError("alpha debe estar en (0,1)")
    return brentq(lambda b: orness_n(b, n) - alpha, 1e-6, 1e6, xtol=1e-9)


def orness_inducido(mu):
    """orness del inversor por pertenencia difusa mu (Def. 4): sum mu_k a_k / sum mu_k."""
    num = sum(mu[p] * ORNESS_PERFIL[p] for p in mu)
    den = sum(mu.values())
    return num / den


if __name__ == "__main__":
    for n in (4, 10, 252):
        assert abs(orness_n(1.0, n) - 0.5) < 1e-9, n
    print("orness_n(beta=1) = 0.5 para n en {4,10,252}  OK")
    print("beta por perfil (n=4):",
          {p: round(beta_para_orness(o, 4), 3) for p, o in ORNESS_PERFIL.items()})
