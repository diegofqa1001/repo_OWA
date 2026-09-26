"""
verify_propiedades_cap4.py — Verificaciones numéricas de las afirmaciones
matemáticas de los Capítulos 3–4 y del Anexo B de la tesis (revisión de la
notación, la integral de Choquet, la representación de Lorenz, los
anidamientos, el Lema 1, el Contraejemplo 1 generalizado, las anclas por
octiles y el orness efectivo inducido por régimen).

Cada bloque imprime su resultado y lo guarda en
results/verificacion_propiedades_cap4.json.
Uso: python scripts/verify_propiedades_cap4.py
Licencia: MIT.
"""
import os, sys, json, itertools
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import numpy as np
from scipy import stats
from src.owa_core import pesos_rim, orness_n, beta_para_orness, ORNESS_OCTILES, ORNESS_V1
from src.spectral_route import espectro, V_beta
from src.spectral_lp import optimiza_cartera_lp
from src.regime import orness_efectivo, LAMBDA, ALPHA_MIN, S0

out = {}


def cvar_perdida(r, theta):
    """CVaR_theta como pérdida: media de las (theta*S) peores pérdidas (theta*S entero)."""
    r = np.sort(np.asarray(r))            # del peor al mejor
    m = int(round(theta * len(r)))
    return float(-r[:m].mean())


# 1. Integral de Choquet: capacidad simétrica nu(A) = Q(|A|/n) = sum_{j<=|A|} w_j
def supermodular(w):
    n = len(w); cum = np.concatenate([[0.0], np.cumsum(w)])
    nu = lambda A: cum[len(A)]
    U = range(n)
    subs = [frozenset(c) for k in range(n + 1) for c in itertools.combinations(U, k)]
    sup = all(nu(A | B) + nu(A & B) >= nu(A) + nu(B) - 1e-12 for A in subs for B in subs)
    sub = all(nu(A | B) + nu(A & B) <= nu(A) + nu(B) + 1e-12 for A in subs for B in subs)
    return sup, sub

res = {}
for b in (4.0, 1.0, 0.25):
    w = pesos_rim(b, 4)
    sup, sub = supermodular(w)
    res[f"beta={b}"] = {"orness": orness_n(b, 4), "supermodular": sup, "submodular": sub}
out["choquet_capacidad_n4"] = res
print("1. Choquet:", res)

# 2. Representación de Lorenz: phi_s = psi_{S-s+1} (peor primero), lambda_k = k(phi_k - phi_{k+1})
rng = np.random.default_rng(20260925)
S, beta = 50, 2.3
r = rng.normal(0.0005, 0.015, S)
psi = espectro(beta, S)                    # índice 1 = mejor escenario
phi = psi[::-1]                            # índice 1 = peor escenario
lam = np.array([(k + 1) * (phi[k] - (phi[k + 1] if k + 1 < S else 0.0)) for k in range(S)])
V = float(psi @ np.sort(r)[::-1])
mezcla = float(sum(lam[k] * cvar_perdida(r, (k + 1) / S) for k in range(S)))
out["lorenz"] = {"psi_creciente_mejor_primero": bool(np.all(np.diff(psi) >= 0)),
                 "phi_no_creciente_peor_primero": bool(np.all(np.diff(phi) <= 0)),
                 "lambda_no_negativos": bool(np.all(lam >= -1e-15)), "suma_lambda": float(lam.sum()),
                 "V_beta": V, "suma_lambda_CVaR": mezcla, "V_mas_mezcla": V + mezcla}
print("2. Lorenz:", out["lorenz"])

# 3. Anidamientos (familia general de cuantificadores)
S = 40; theta = 0.25
r = rng.normal(0.0005, 0.015, S); rs = np.sort(r)[::-1]
P = np.arange(0, S + 1) / S
Q_rampa = np.maximum(0.0, (P - 1 + theta) / theta)
psi_rampa = np.diff(Q_rampa)
Q_wald = (P >= 1.0).astype(float)
psi_wald = np.diff(Q_wald)
h = 0.3
psi_hurw = np.zeros(S); psi_hurw[0] = h; psi_hurw[-1] = 1 - h
orn = lambda w: float(np.dot(len(w) - np.arange(1, len(w) + 1), w) / (len(w) - 1))
psi_rim_min = [float(np.min(espectro(b, S))) for b in (0.2, 1.0, 5.0, 50.0)]
out["anidamientos"] = {
    "rampa_V_mas_CVaR": float(psi_rampa @ rs + cvar_perdida(r, theta)),
    "wald_V_menos_min": float(psi_wald @ rs - r.min()),
    "limite_beta_grande_V_menos_min": float(V_beta(np.array([1.0]), r[:, None], 5000.0) - r.min()),
    "hurwicz_orness": orn(psi_hurw), "hurwicz_h": h,
    "hurwicz_V_menos_formula": float(psi_hurw @ rs - (h * r.max() + (1 - h) * r.min())),
    "min_psi_RIM_para_beta_0.2_1_5_50": psi_rim_min}
print("3. Anidamientos:", out["anidamientos"])

# 4. Proposición 6: SSD (icv) mueve media y CVaR en sentidos opuestos; dispersión -> varianza
x = rng.normal(0.0, 0.01, 200000)
X, Y = 0.0 + 0.5 * x, 0.0002 + 1.0 * x      # Y más dispersa (orden de dispersión) y media mayor
out["prop6"] = {"var_X": float(X.var()), "var_Y": float(Y.var()),
                "media_X": float(X.mean()), "media_Y": float(Y.mean()),
                "CVaR05_X": cvar_perdida(X, 0.05), "CVaR05_Y": cvar_perdida(Y, 0.05)}
print("4. Prop. 6 (ilustración):", out["prop6"])

# 5. No unicidad / constancia por tramos del óptimo del LP (semilla 7, S=40, N=6)
rng7 = np.random.default_rng(7)
R = rng7.normal(0.0006, 0.018, size=(40, 6))
carteras = {}
for a in (0.05, 0.20, 0.30, 0.40, 0.45, 0.50):
    w, _ = optimiza_cartera_lp(R, beta_para_orness(a, 40))
    carteras[str(a)] = [round(float(v), 4) for v in w]
out["lp_constante_por_tramos"] = carteras
print("5. LP por tramos:", carteras)

# 6. Anclas por octiles: invariancia a la distribución de la latente
p = (2 * np.arange(1, 9) - 1) / 16
anclas = {}
for nombre, d in {"normal": stats.norm, "logistica": stats.logistic, "t3": stats.t(3),
                  "uniforme": stats.uniform}.items():
    z = d.ppf(p); anclas[nombre] = [float(v) for v in d.cdf(z)]
out["octiles_invariancia"] = anclas
print("6. Octiles:", anclas["normal"], "iguales en todas:",
      all(np.allclose(v, p) for v in anclas.values()))

# 7. Semiespectro cauteloso: beta*(alpha, n) por perfil y parametrización
tab = {}
for par, anc in (("v1", ORNESS_V1), ("octiles", ORNESS_OCTILES)):
    tab[par] = {k: {n: round(beta_para_orness(a, n), 3) for n in (2, 4, 7, 252)} for k, a in anc.items()}
out["beta_por_perfil"] = tab
print("7. beta*:", tab["v1"]["Pragmatist"], tab["octiles"]["Analyst"])

# 8. Lema 1: masa sobre la fracción p de peores escenarios, 1 - (1-p)^beta, creciente en beta
ps = np.linspace(0.01, 0.99, 99); bs = np.linspace(0.1, 10, 200)
M = np.array([[1 - (1 - q) ** b for b in bs] for q in ps])
out["lema1_monotonia"] = bool(np.all(np.diff(M, axis=1) >= 0))
print("8. Lema 1:", out["lema1_monotonia"])

# 9. Contraejemplo 1 con orness h arbitrario (n = 2: el orness de (w1, w2) es w1)
A, B = np.array([0.90, 0.50]), np.array([0.40, 1.00])
filas = []
for par, anc in (("v1", ORNESS_V1), ("octiles", ORNESS_OCTILES)):
    for k, a in anc.items():
        w = pesos_rim(beta_para_orness(a, 2), 2)
        sA, sB = float(w @ np.sort(A)[::-1]), float(w @ np.sort(B)[::-1])
        filas.append({"par": par, "perfil": k, "h": round(float(w[0]), 6), "sA_menos_sB": round(sA - sB, 6),
                      "formula": round(0.1 - 0.2 * float(w[0]), 6), "elige": "A" if sA > sB else "B"})
out["contraejemplo_h"] = filas
print("9. Contraejemplo:", [(f["par"], f["perfil"], f["elige"]) for f in filas])

# 10. Tabla 3.2: pertenencias y centros de gravedad
trap = {"VL": (0, 0, 0.10, 0.25), "L": (0.10, 0.25, 0.25, 0.40), "M": (0.30, 0.45, 0.55, 0.70),
        "H": (0.60, 0.75, 0.75, 0.90), "VH": (0.75, 0.90, 1.00, 1.00)}
def mu(x, t):
    a, b, c, d = t
    if b <= x <= c: return 1.0
    if a < x < b: return (x - a) / (b - a)
    if c < x < d: return (d - x) / (d - c)
    return 0.0
xs = np.linspace(0, 1, 200001)
cog = {k: float(np.sum(xs * np.array([mu(v, t) for v in xs])) / np.sum([mu(v, t) for v in xs])) for k, t in trap.items()}
out["difuso"] = {"mu(0,42)": {k: mu(0.42, t) for k, t in trap.items()},
                 "mu(0,35)": {k: mu(0.35, t) for k, t in trap.items()},
                 "COG": {k: round(v, 3) for k, v in cog.items()}}
print("10. Difuso:", out["difuso"])

# 11. Monotonía de F_beta en el ejemplo de §3.4 (pesos congelados de la Tabla 3.4)
b_vec = np.array([0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3])
congelados = {"Guardian": 4.0, "Sentinel": 2.4843, "Pragmatist": 0.9881, "Analyst": 0.6949,
              "Strategist": 0.5798, "Adventurer": 0.4771, "Innovator": 0.3889, "Visionary": 0.1765}
# (exponentes congelados en A-Fuzzy-OWA-Taxonomy-of-Investor-Risk-Profiles/data/owa/owa_profiles.json)
F = {k: round(float(pesos_rim(b, 7) @ b_vec), 3) for k, b in congelados.items()}
Fb = [float(pesos_rim(b, 7) @ b_vec) for b in np.linspace(0.05, 8, 400)]
out["F_beta"] = {"ejemplo": F, "no_creciente_en_beta": bool(np.all(np.diff(Fb) <= 1e-12))}
print("11. F_beta:", out["F_beta"])

# 12. Factibilidad del símplex con tope: N * cap >= 1
out["factibilidad_tope"] = {"N_min_cap_0.30": int(np.ceil(1 / 0.30))}

# 13. Orness efectivo inducido por régimen (src/regime.py)
alphas = np.linspace(0.01, 0.99, 197); acts = np.linspace(0, 1, 101)
E = np.array([[orness_efectivo(a, x) for a in alphas] for x in acts])
out["orness_efectivo"] = {
    "lambda": LAMBDA, "alpha_min": ALPHA_MIN, "s0": S0,
    "nunca_supera_nominal": bool(np.all(E <= alphas[None, :] + 1e-15)),
    "igual_sin_activacion": bool(np.allclose(E[0], alphas)),
    "estrictamente_creciente_en_alpha": bool(np.all(np.diff(E, axis=1) > 0)),
    "pendiente_minima": float(np.min(np.diff(E, axis=1) / np.diff(alphas)[None, :])),
    "cota_inferior_ok": bool(np.all(E >= np.minimum(alphas, ALPHA_MIN)[None, :] - 1e-15)),
    "ejemplos_activacion_1": {k: round(orness_efectivo(a, 1.0), 4) for k, a in ORNESS_OCTILES.items()}}
print("13. Orness efectivo:", out["orness_efectivo"])

# 14. Ejemplo de §4.1.4: orness inducido y exponente calibrado (anclas canónicas y v1)
a_oct = 0.6 * ORNESS_OCTILES["Sentinel"] + 0.4 * ORNESS_OCTILES["Pragmatist"]
a_v1 = 0.6 * ORNESS_V1["Sentinel"] + 0.4 * ORNESS_V1["Pragmatist"]
out["ejemplo_4_1_4"] = {"alpha_octiles": a_oct, "beta_S252": beta_para_orness(a_oct, 252),
                        "beta_asintotico": 1 / a_oct - 1, "alpha_v1": a_v1,
                        "beta_v1_S252": beta_para_orness(a_v1, 252)}
print("14. Ejemplo §4.1.4:", out["ejemplo_4_1_4"])

# 15. CVaR con theta*S no entero (rampa) frente a la definición con átomo fraccionario
S = 40; theta = 0.23; m = theta * S; k = int(np.floor(m))
r = rng.normal(0.0005, 0.015, S); rs = np.sort(r)[::-1]; worst = np.sort(r)
P = np.arange(0, S + 1) / S
psi_r = np.diff(np.maximum(0.0, (P - 1 + theta) / theta))
es = -(worst[:k].sum() + (m - k) * worst[k]) / m
out["rampa_no_entera"] = {"V_mas_ES": float(psi_r @ rs + es)}
print("15. Rampa no entera:", out["rampa_no_entera"])

os.makedirs("results", exist_ok=True)
json.dump(out, open("results/verificacion_propiedades_cap4.json", "w"), indent=1, ensure_ascii=False)
print("Guardado: results/verificacion_propiedades_cap4.json")
