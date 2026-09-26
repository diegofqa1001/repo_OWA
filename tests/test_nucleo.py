"""Pruebas mínimas del núcleo (v1.1.0)."""
import numpy as np
from src.owa_core import orness_n, beta_para_orness, ORNESS_OCTILES
from src.spectral_route import V_beta, _V_y_grad, espectro, pesos_espectral
from src.regime import orness_efectivo
from src.inference import permutacion_exacta


def test_orness_neutral():
    for n in (4, 10, 252):
        assert abs(orness_n(1.0, n) - 0.5) < 1e-12


def test_octiles():
    assert [round(v, 4) for v in ORNESS_OCTILES.values()] == [(2 * k - 1) / 16 for k in range(1, 9)]


def test_gradiente_espectral():
    rng = np.random.default_rng(0); R = rng.normal(0, 0.01, (60, 6)); w = np.full(6, 1 / 6)
    psi = espectro(3.0, 60); v, g = _V_y_grad(w, R, psi); h = 1e-7
    num = np.array([(V_beta(w + h * e, R, 3.0) - V_beta(w - h * e, R, 3.0)) / (2 * h) for e in np.eye(6)])
    assert np.allclose(g, num, atol=1e-6)


def test_conservador_menos_volatil():
    rng = np.random.default_rng(1)
    R = np.column_stack([rng.normal(0.0002, 0.005, 252), rng.normal(0.0008, 0.03, 252),
                         rng.normal(0.0004, 0.01, 252), rng.normal(0.0006, 0.02, 252)])
    wg, _ = pesos_espectral(R, 0.0625, cap=1.0); wv, _ = pesos_espectral(R, 0.9375, cap=1.0)
    assert np.std(R @ wg) < np.std(R @ wv)


def test_orness_efectivo():
    for a in ORNESS_OCTILES.values():
        assert orness_efectivo(a, 0.0) == a
        assert orness_efectivo(a, 1.0) <= a
    assert orness_efectivo(0.3, 1.0) < orness_efectivo(0.5, 1.0)


def test_permutacion_exacta():
    r = permutacion_exacta(np.arange(8), np.arange(8.0))
    assert abs(r["rho_obs"] - 1) < 1e-12 and r["n_perm"] == 40320 and abs(r["p_perm"] - 2 / 40320) < 1e-12
