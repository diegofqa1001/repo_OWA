# Datos

Todas las cifras del repositorio se calculan sobre el snapshot versionado
`data/snapshot_2026-08-31/` (ver su MANIFEST.md: fuentes, fechas de descarga,
SHA-256, universo y regla de inclusión). Ningún guion descarga datos en tiempo de
ejecución; `scripts/fetch_volume.py` documenta cómo se obtuvo el volumen y
`scripts/incorporar_bancolombia.py`, cómo se añadió al universo colombiano la acción
preferencial de Bancolombia bajo el símbolo vigente de Grupo Cibest (PFCIBEST.CL; serie
cruda en `raw_PFCIBEST.CL.csv`, descargada el 2026-09-27). El universo colombiano tiene
18 emisores y el estadounidense, 25.
