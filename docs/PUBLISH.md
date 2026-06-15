# Publicar y obtener un DOI (Zenodo)

El contenido del repositorio ya está publicado en GitHub. Esta guía cubre cómo
acuñar un DOI citable con Zenodo y cómo actualizar el repositorio en el futuro.

## Obtener el DOI con Zenodo

1. Entra a https://zenodo.org e inicia sesión **con tu cuenta de GitHub**.
2. Ve a https://zenodo.org/account/settings/github/ y activa (toggle ON) el
   repositorio `repo_OWA`.
3. En GitHub, crea un release: pestaña **Releases** -> **Draft a new release**
   -> Tag `v1.0.0` -> título "v1.0.0" -> **Publish release**.
4. Zenodo capturará el release automáticamente y generará un **DOI**.
5. Copia el "DOI badge" de Zenodo y pégalo en `README.md` y en
   `CITATION.cff` (campo `repository-code` y un nuevo campo `doi:`).

## Enlazar en el manuscrito

En la sección Declaraciones del manuscrito:

```
Código y datos: https://github.com/diegofqa1001/repo_OWA
DOI: 10.5281/zenodo.XXXXXXX
```

## Actualizar el repositorio desde tu computador (opcional)

```bash
git clone https://github.com/diegofqa1001/repo_OWA.git
cd repo_OWA
# ...editar archivos...
git add .
git commit -m "Actualización"
git push
```

> Nota: crear cuenta, autenticar y publicar son acciones que debe hacer la
> persona usuaria; no se pueden introducir credenciales de forma automática.
