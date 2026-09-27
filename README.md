# Motor de recomendación OWA adaptativo al perfil conductual — v1.1.0

[![License: MIT](https://img.shields.io/badge/Code-MIT-yellow.svg)](LICENSE)
[![License: CC BY 4.0](https://img.shields.io/badge/Content-CC%20BY%204.0-lightgrey.svg)](LICENSE-CONTENT.md)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.20695172.svg)](https://doi.org/10.5281/zenodo.20695172)

Código, datos congelados y resultados del **Capítulo 5** (validación empírica de las dos
vías OWA) y del **§8.4** (componente adaptativo inducido por régimen) de la tesis doctoral
*Modelo adaptativo de recomendación para el diseño de portafolios de inversión en renta
variable bajo incertidumbre* (Universidad Nacional de Colombia, Sede Manizales).

## Qué contiene

Dos operadores consumen el mismo grado actitudinal (orness) de ocho perfiles conductuales:

1. **Vía de criterios** (`src/criteria_route.py`): aplica el orness sobre cuatro criterios
   normalizados de cada activo (rentabilidad, baja volatilidad, baja caída, liquidez) y
   selecciona los ocho mejores puntajes. Mide exigencia multicriterio (Proposición 2) y puede
   invertir el orden de riesgo (Contraejemplo 1).
2. **Vía espectral PR-WOWA** (`src/spectral_route.py`): aplica el orness sobre los rendimientos
   ordenados de la cartera. Para orness ≤ 1/2 es una medida de riesgo espectral coherente
   (Acerbi, 2002), cóncava y resoluble como LP (`src/spectral_lp.py`).
3. **Componente adaptativo inducido por régimen** (`src/regime.py`): el índice de estrés
   VIX/EPU (EPU con rezago de publicación) reduce el orness del perfil por encima del umbral
   s₀ = 0,55: α_eff = α − λ·a(t)·max(0, α − α_min), λ = 0,85, α_min = 0,12.

Anclas de orness canónicas: octiles (2k − 1)/16. Las anclas históricas v1 (0,158–0,865) se
ejecutan como análisis de sensibilidad.

## Resultados principales (anclas por octiles, neto de 10 pb por rotación, 2015–2024)

| Mercado | Vía | ρ̄ Spearman por ventana (t NW) | % ventanas coherentes | ρ permutación exacta (p) |
|---|---|---|---|---|
| EE. UU. (107 ventanas) | Criterios | −0,583 (−11,0) | 11,2 % | −0,929 (0,002) |
| EE. UU. | Espectral | +0,766 (49,9) | 99,1 % | +0,762 (0,037) |
| Colombia (97 ventanas) | Criterios | −0,211 (−3,0) | 33,0 % | −0,905 (0,005) |
| Colombia | Espectral | +0,655 (16,7) | 90,7 % | +0,833 (0,015) |

Componente adaptativo, ventanas con estrés activo: reducción media de volatilidad de
2,72 pp (EE. UU., p < 0,001) y 2,08 pp (Colombia, p = 0,003), sin pérdida significativa de
coherencia. Tablas completas en `results/cap5/` y `results/iowa/`.

## Reproducir

```bash
python -m pip install -r requirements.txt
pytest -q                                   # pruebas del núcleo
python scripts/run_cap5.py                  # Cap. 5: 2 mercados x 2 anclas (≈ 1 h por mercado)
python scripts/analyze_cap5.py              # Tablas 5.1-5.3 y Figuras 5.1-5.3
python scripts/analyze_cap5_complementos.py # coherencia en rentabilidad y caída; concentración espectral
python scripts/run_iowa.py                  # §8.4: corrida adaptativa (≈ 40 min por mercado)
python scripts/analyze_iowa.py              # pruebas del §8.4 y figura del orness efectivo
python scripts/fig_iowa.py                  # Figuras 4.2 y 8.2-8.4 y sus descriptivos
python scripts/verify_lp_vs_slsqp.py        # Prop. 5: LP exacto frente a SLSQP
python scripts/verify_lp_vs_slsqp_ventanas.py
python scripts/verify_nesting.py            # Prop. 4: anidamientos
python scripts/verify_propiedades_cap4.py   # propiedades formales del Cap. 4
```

Semilla 42; 8 arranques en el régimen cóncavo (todo óptimo local es global) y 40 en el no
cóncavo. Los resultados publicados en `results/` son los de referencia de la tesis.

## Cambios de la v1.1.0 respecto de la v1.0.0

- Corrección: los guiones de la v1.0.0 pasaban niveles de precio al optimizador espectral;
  ahora recibe rendimientos.
- Todas las estrategias pasan por `backtest()`, con costos de 10 pb por rotación y
  comparadores 1/N y Markowitz (máxima razón de Sharpe) implementados.
- Datos congelados en un snapshot versionado con SHA-256; ningún guion descarga en ejecución.
- Resultados y figuras versionados (antes excluidos por `.gitignore`).
- Permutación exacta sobre 8! reasignaciones y Diebold-Mariano con corrección HLN.
- Componente adaptativo implementado sobre la vía espectral.

## Licencia y cita

DOI de la versión 1.1.0: [10.5281/zenodo.22981781](https://doi.org/10.5281/zenodo.22981781). DOI de concepto (todas las versiones): [10.5281/zenodo.20695172](https://doi.org/10.5281/zenodo.20695172).

Código MIT; texto, figuras y resultados CC BY 4.0. Cite el repositorio con `CITATION.cff`.
