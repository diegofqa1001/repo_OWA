# Snapshot versionado — corrida definitiva del componente adaptativo IOWA

Fecha de descarga (UTC): **2026-08-31T17:31:09Z** (serie `PFCIBEST.CL`: 2026-09-27)
Periodo cubierto: 2015-01-01 a 2025-01-02.

Este directorio congela, con fecha y checksum, los insumos de datos usados en
la corrida definitiva del componente adaptativo IOWA (§8.4.3 de la tesis), en
cumplimiento del PENDIENTE allí declarado: *"versionar un snapshot fechado de
las series de precios ... e incorporar al repositorio las series de inducción
de régimen —VIX y EPU—"*.

## Precios

| Archivo | Universo | Fuente | Emisores solicitados | Emisores retenidos | Regla de inclusión | SHA-256 (16) |
|---|---|---|---|---|---|---|
| `us_prices_snapshot.csv` | S&P 500 (EE. UU.) | Yahoo Finance (endpoint `chart`, precio ajustado por splits/dividendos) | 25 | 25/25 | cobertura ≥ 80 % del periodo | `906ca9dc8dcdfc22` |
| `co_prices_snapshot.csv` | BVC (Colombia) | Yahoo Finance (sufijo `.CL`) | 18 | 18/18 | cobertura ≥ 80 % del periodo | `b11ccd6b35449e40` |

**Universo EE. UU. (25):** AAPL, MSFT, AMZN, GOOGL, META, NVDA, JPM, JNJ, V, PG,
UNH, HD, MA, DIS, BAC, XOM, CVX, KO, PEP, WMT, MRK, ABBV, COST, ADBE, CSCO.

**Universo Colombia (18 solicitados y retenidos):** PFCIBEST.CL, ECOPETROL.CL,
GRUPOSURA.CL, PFGRUPSURA.CL, ISA.CL, CEMARGOS.CL, PFCEMARGOS.CL,
GRUPOARGOS.CL, PFGRUPOARG.CL, BOGOTA.CL, PFAVAL.CL, CELSIA.CL, CORFICOLCF.CL,
ETB.CL, NUTRESA.CL, TERPEL.CL, GEB.CL, PROMIGAS.CL.

**Bancolombia (acción preferencial):** se incluye mediante `PFCIBEST.CL`, el
símbolo vigente de Grupo Cibest tras la reorganización societaria de
Bancolombia; la fuente ya no devuelve serie para el símbolo anterior
(`PFBCOLOM.CL`) y publica la historia completa desde 2015 bajo el vigente
(diagnóstico en validacion-oe4, `scripts/diag_simbolos_bancolombia.py`). La
serie de `PFCIBEST.CL` se descargó el **2026-09-27** con el mismo endpoint,
periodo y campos que el resto del universo (`scripts/incorporar_bancolombia.py`;
respuesta cruda en `raw_PFCIBEST.CL.csv`, SHA-256 (16) `5237d28e16d82ade`) y se
añadió como columna a `co_prices_snapshot.csv` y `co_volume_snapshot.csv`
(SHA-256 (16) `b11ccd6b35449e40` y `fcad0b91f9763960`), con cobertura del
100 % del periodo.

**Nota de cobertura:** `PFCEMARGOS.CL` (Cementos Argos, acción preferencial)
tiene datos solo hasta 2024-09-20 (≈97 % de cobertura) por una reorganización
societaria de Grupo Argos ocurrida en 2024; se retiene por cumplir igualmente
el umbral del 80 %, y el hueco final se cubre por relleno hacia adelante
(`ffill`) del último precio observado, siguiendo la misma convención que
`market_from_prices`.

**Limitación heredada (no resuelta por este snapshot):** Yahoo Finance no es
una fuente auditada para la BVC; persiste el sesgo de supervivencia parcial ya
declarado en el Capítulo 5. Migrar a una fuente auditada (Refinitiv/LSEG)
sigue siendo tarea de la versión confirmatoria.

## Series de inducción de régimen (VIX / EPU)

| Archivo | Serie | Fuente | Frecuencia | SHA-256 (16) |
|---|---|---|---|---|
| `vix_raw.csv` | CBOE Volatility Index (VIXCLS) | FRED (Federal Reserve Bank of St. Louis) | diaria | `60ffed9e5be511ba` |
| `epu_raw.csv` | US Economic Policy Uncertainty Index (USEPUINDXM), Baker, Bloom y Davis (2016) | FRED | mensual, remuestreada a diaria por `ffill` | `7258d850098cf8e1` |

Ambas series se obtuvieron directamente de FRED (`fredgraph.csv`), una fuente
auditada y estable, en lugar de un scraping de policyuncertainty.com — una
mejora de auditabilidad respecto al diseño original de la §8.4.2, que solo
mencionaba "el índice EPU de Baker, Bloom y Davis (2016)" sin fijar la fuente
de acceso.

## Reproducibilidad

Para reproducir este snapshot: `python scripts/fetch_yahoo.py 2015-01-01
2025-01-02 <salida.csv> <tickers...>` (ver `scripts/fetch_yahoo.py`) y las dos
URL de FRED:

```
https://fred.stlouisfed.org/graph/fredgraph.csv?id=VIXCLS&cosd=2015-01-01&coed=2025-01-02
https://fred.stlouisfed.org/graph/fredgraph.csv?id=USEPUINDXM&cosd=2015-01-01&coed=2025-01-02
```

El script de análisis (`scripts/induced_route.py`) consume estos cuatro
archivos, construye el `MarketData` real vía `market_from_prices`, y ejecuta
la corrida adaptativa vs. estática descrita en `docs/informe_iowa.md`.
