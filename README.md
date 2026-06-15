# Motor de recomendación OWA adaptativo al perfil conductual

[![License: MIT](https://img.shields.io/badge/Code-MIT-yellow.svg)](LICENSE)
[![License: CC BY 4.0](https://img.shields.io/badge/Content-CC%20BY%204.0-lightgrey.svg)](LICENSE-CONTENT.md)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.20695173.svg)](https://doi.org/10.5281/zenodo.20695173)

Código y datos reproducibles del artículo:

> **When Multicriteria Scoring Inverts the Investor: A Profile-Endogenous Spectral
> OWA Operator for Behaviorally Consistent Equity Portfolio Recommendation.**
> Quintero-Avellaneda, D. F., Ramírez-Angulo, P. J., & León-Castro, E. (2026).
> Universidad Nacional de Colombia, Sede Manizales.

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
│   ├── backtest.py          # ventanas rodantes, neto de costos, comparadores
│   └── inference.py         # monotonía por ventana + permutación + NW + DM
├── scripts/
│   ├── run_criteria.py            # reproduce la vía de criterios
│   ├── run_spectral_multistart.py # Tabla 2 + dispersión alpha>1/2 + figura
│   └── run_inference.py           # Tabla 1 (coherencia)
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
```

Los resultados se escriben en `results/` y las figuras en `figures/`. Los datos
se descargan con `yfinance` (ver `data/README.md`).

## Cita

Si usa este software o sus resultados, cite el artículo y el repositorio
(ver `CITATION.cff`). DOI del repositorio (Zenodo):
**10.5281/zenodo.20695173** — https://doi.org/10.5281/zenodo.20695173
# Motor de recomendación OWA adaptativo al perfil conductual

[![License: MIT](https://img.shields.io/badge/Code-MIT-yellow.svg)](LICENSE)
[![License: CC BY 4.0](https://img.shields.io/badge/Content-CC%20BY%204.0-lightgrey.svg)](LICENSE-CONTENT.md)

Código y datos reproducibles del artículo:

> **When Multicriteria Scoring Inverts the Investor: A Profile-Endogenous Spectral
> OWA Operator for Behaviorally Consistent Equity Portfolio Recommendation.**
> Quintero-Avellaneda, D. F., Ramírez-Angulo, P. J., & León-Castro, E. (2026).
> Universidad Nacional de Colombia, Sede Manizales.

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
│   ├── backtest.py          # ventanas rodantes, neto de costos, comparadores
│   └── inference.py         # monotonía por ventana + permutación + NW + DM
├── scripts/
│   ├── run_criteria.py            # reproduce la vía de criterios
│   ├── run_spectral_multistart.py # Tabla 2 + dispersión alpha>1/2 + figura
│   └── run_inference.py           # Tabla 1 (coherencia)
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
```

Los resultados se escriben en `results/` y las figuras en `figures/`. Los datos
se descargan con `yfinance` (ver `data/README.md`).

## Cita

Ver `CITATION.cff`. El DOI de Zenodo se añadirá tras el primer release
(ver `docs/PUBLISH.md`).
