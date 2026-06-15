# Datos

No se versionan precios en el repositorio: se descargan reproduciblemente con
yfinance (Yahoo Finance) al correr los scripts. Periodo: 2015-01-01 a
2025-01-01, precios diarios ajustados (auto_adjust=True).

## Universo EE. UU. (S&P 500, mercado profundo)

25 emisores líquidos solicitados; regla de inclusión: cobertura >= 80% del
periodo. Tickers en src/backtest.py (TICKERS_US). Retenidos: 25/25.

## Universo Colombia (BVC, mercado emergente)

18 emisores solicitados; regla de inclusión: cobertura >= 80%. Descartado
PFBCOLOM por deslistamiento. Retenidos: 17/18. Tickers en src/backtest.py
(TICKERS_CO).

## Limitación declarada (sesgo de supervivencia)

yfinance no es una fuente auditada para la BVC; el universo se construye sobre
emisores vigentes, por lo que persiste un sesgo de supervivencia parcial. Para
una versión confirmatoria se recomienda validar con fuente auditada
(p. ej., Refinitiv/LSEG) e incluir emisores deslistados/OPA del periodo.
