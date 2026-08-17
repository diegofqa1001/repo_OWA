# Motor de recomendación OWA adaptativo al perfil conductual

[![License: MIT](https://img.shields.io/badge/Code-MIT-yellow.svg)](LICENSE)
[![License: CC BY 4.0](https://img.shields.io/badge/Content-CC%20BY%204.0-lightgrey.svg)](LICENSE-CONTENT.md)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.20695173.svg)](https://doi.org/10.5281/zenodo.20695173)

Código y datos reproducibles de la comparación entre dos operadores OWA
para recomendación de carteras coherente con el perfil conductual de riesgo.

## Resumen del aporte

Se comparan **dos operadores que consumen el mismo grado attitudinal (orness)**
derivado endógenamente de una taxonomía difusa validada de ocho perfiles
conductuales de riesgo:

1. **Vía de criterios** (base de la industria): aplica el orness sobre los
   criterios multicriterio de cada activo. Se demuestra (Prop. 2 + Contraejemplo 1)
   que mide **exigencia multicriterio (AND/OR), no aversión al riesgo**, y puede
   **invertir** al inversor (el conservador recibe la cartera más volátil).
2. **Vía espectral PR-WOWA** (corrección): aplica el orness sobre los resultados
   **ordenados de la cartera**. Es una medida de riesgo espectral coherente
   (Acerbi, 2002) para alpha<=1/2, que anida CVaR, maximin de Wald y Hurwicz, y en
   la que el riesgo **crece** con el orness. Restaura la coherencia conductual.

> **Nota de verificación (añadida 2026-08-17).** La Proposición 5 (Anexo B.6 de la
> tesis) afirma que para alpha<=1/2 (beta>=1) la cartera óptima se obtiene resolviendo
> un único programa lineal (mezcla de CVaR). `spectral_route.py` resuelve siempre con
> SLSQP multi-start, sin ejercer esa tratabilidad. `spectral_lp.py` implementa el LP
> exacto y `scripts/verify_lp_vs_slsqp.py` lo usa para verificar, en el régimen
> coherente, que el heurístico alcanza el óptimo global que el LP certifica — cerrando
> la brecha entre el enunciado formal y el código.

> **Nota de verificación (añadida 2026-08-17).** La Proposición 4 (Anexo B.7 de la
> tesis) afirma dos casos límite del operador espectral V_beta, presentados hasta
> ahora solo como argumento analítico: (a) cuando beta -> infinito, V_beta converge
> al maximin de Wald (el peor escenario individual de la cartera); (b) un
> cuantificador escalón (peso uniforme 1/m sobre los m peores escenarios) reproduce
> exactamente el CVaR de los m peores, calculado de forma independiente con la
> fórmula directa de Rockafellar-Uryasev. `scripts/verify_nesting.py` convierte
> ambas afirmaciones en pruebas numéricas reproducibles: con beta=100 000 la
> diferencia con min(R·w) es 0 hasta precisión de máquina, y el cuantificador
> escalón coincide con el CVaR directo hasta ~3×10⁻¹⁸ para m entre 1 y 100 (S=200
> escenarios) — cerrando la brecha entre el enunciado formal y el código.

**Hallazgo empírico** (backtests de ventanas rodantes 2015-2025, EE. UU. y
Colombia, neto de costos): en el eje de **volatilidad**, la vía de criterios
invierte el orden del perfil (conservador más volátil en 67-91% de las ventanas)
y la vía espectral lo restaura (riesgo creciente con el orness en 82-100% de las
ventanas). El criterio de éxito es la **consecuencia conductual (suitability)**,
no la maximización de utilidad.

## Estructura

```
repo_OWA/
├── src/
│   ├── owa_core.py          # OWA, RIM, orness, beta*(alpha,n)  (Def. 1-4, Prop. 1)
│   ├── criteria_route.py    # vía de criterios (resultado de inversión)
│   ├── spectral_route.py    # PR-WOWA + barrido multi-start (alpha>1/2)
│   ├── spectral_lp.py       # LP exacto (Prop. 5, alpha<=1/2): verificacion del optimo global
│   ├── backtest.py          # ventanas rodantes, neto de costos, comparadores
│   └── inference.py         # monotonía por ventana + permutación + NW + DM
├── scripts/
│   ├── run_criteria.py            # reproduce la vía de criterios
│   ├── run_spectral_multistart.py # Tabla 2 + dispersión alpha>1/2 + figura
│   ├── run_inference.py           # Tabla 1 (coherencia)
│   ├── verify_lp_vs_slsqp.py      # Prop. 5: LP vs. heurístico SLSQP multi-start
│   └── verify_nesting.py          # Prop. 4: anidamiento de CVaR y maximin de Wald
├── data/README.md           # universo, fuente y regla de inclusión
├── docs/PUBLISH.md          # cómo obtener el DOI (Zenodo)
├── requirements.txt
├── CITATION.cff
├── LICENSE                  # MIT (código)
└── LICENSE-CONTENT.md       # CC-BY-4.0 (texto y figuras)
```

## Reproducir

```bash
python -m pip install -r requirements.txt
python scripts/run_spectral_multistart.py   # Tabla 2 + dispersión + figura
python scripts/run_inference.py             # Tabla 1 (coherencia por ventana + permutación)
python scripts/run_criteria.py              # vía de criterios (inversión)
python scripts/verify_lp_vs_slsqp.py        # Prop. 5: verificación del óptimo global (LP vs. SLSQP)
python scripts/verify_nesting.py            # Prop. 4: anidamiento de CVaR y maximin de Wald
```

Los resultados se escriben en `results/` y las figuras en `figures/`. Los datos
se descargan con `yfinance` (ver `data/README.md`).

## Cita

Si usa este software o sus resultados, cite el repositorio (ver `CITATION.cff`).
DOI (Zenodo): **10.5281/zenodo.20695173** — https://doi.org/10.5281/zenodo.20695173
