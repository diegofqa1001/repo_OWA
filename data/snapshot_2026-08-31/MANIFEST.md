# Snapshot versionado de datos (v1.1.0)

Insumos únicos del Capítulo 5 y de la corrida adaptativa del §8.4 de la tesis.
Periodo: 2015-01-01 a 2024-12-31 (días de negociación).

| Archivo | Contenido | Fuente | Descarga (UTC) | SHA-256 (16) |
|---|---|---|---|---|
| us_prices_snapshot.csv | Precio ajustado, 25 emisores S&P 500 | Yahoo Finance, endpoint chart | 2026-08-31T17:31:09Z | 906ca9dc8dcdfc22 |
| co_prices_snapshot.csv | Precio ajustado, 18 emisores BVC | Yahoo Finance, endpoint chart | 2026-08-31T17:31:09Z (PFCIBEST.CL: 2026-09-27) | b11ccd6b35449e40 |
| us_volume_snapshot.csv | Volumen diario, mismos emisores | Yahoo Finance, endpoint chart | 2026-09-25 | 1d02fa57fed3a3de |
| co_volume_snapshot.csv | Volumen diario, mismos emisores | Yahoo Finance, endpoint chart | 2026-09-25 (PFCIBEST.CL: 2026-09-27) | fcad0b91f9763960 |
| raw_PFCIBEST.CL.csv | Respuesta cruda de PFCIBEST.CL (cierre, cierre ajustado, volumen) | Yahoo Finance, endpoint chart | 2026-09-27 | 5237d28e16d82ade |
| vix_raw.csv | VIXCLS diario | FRED | 2026-08-31 | 60ffed9e5be511ba |
| epu_raw.csv | USEPUINDXM mensual (Baker, Bloom y Davis, 2016) | FRED | 2026-08-31 | 7258d850098cf8e1 |

Universo EE. UU. (25): AAPL, MSFT, AMZN, GOOGL, META, NVDA, JPM, JNJ, V, PG, UNH, HD, MA,
DIS, BAC, XOM, CVX, KO, PEP, WMT, MRK, ABBV, COST, ADBE, CSCO.

Universo Colombia (18 solicitados, 18 retenidos): PFCIBEST, ECOPETROL, GRUPOSURA, PFGRUPSURA, ISA,
CEMARGOS, PFCEMARGOS, GRUPOARGOS, PFGRUPOARG, BOGOTA, PFAVAL, CELSIA, CORFICOLCF, ETB,
NUTRESA, TERPEL, GEB, PROMIGAS (sufijo .CL). Bancolombia (acción preferencial) se incluye
mediante el símbolo vigente de Grupo Cibest, PFCIBEST.CL, bajo el cual la fuente publica la
historia completa desde 2015 (cobertura del 100 % del periodo); la serie se descargó el
2026-09-27 con el mismo endpoint, periodo y campos que el resto del snapshot
(`scripts/incorporar_bancolombia.py`).

Regla de inclusión: cobertura de precios ≥ 80 % del periodo. Convenciones de carga
(src/data.py): se descartan las fechas sin negociación: (i) días en que menos de la mitad
de los emisores registra volumen positivo (en la BVC el endpoint rellena festivos con el
precio previo) y (ii) días en que todos los emisores repiten el precio del día anterior
(registros duplicados o festivos no marcados); los huecos residuales se rellenan hacia
adelante. Resultado: 2 516 días (EE. UU.; la regla (ii) no elimina ninguna fecha) y
2 299 días (Colombia).

Limitación: Yahoo Finance no es una fuente auditada para la BVC y el universo se
construye con emisores vigentes (sesgo de supervivencia parcial).
Los detalles de la descarga original de precios están en MANIFEST_precios_origen.md.
