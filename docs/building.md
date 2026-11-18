# Building and publishing docs

## Local HTML (QSIPrep / Sphinx style)

```bash
pip install -r docs/requirements.txt
sphinx-build -b html docs docs/_build/html
```

Open `docs/_build/html/index.html`.

## Read the Docs

1. Sign in at https://readthedocs.org/ with GitHub.
2. Import **phindagijimana/normative**.
3. Use the repo’s [`.readthedocs.yaml`](https://github.com/phindagijimana/normative/blob/main/.readthedocs.yaml)
   (already points at `docs/conf.py`).
4. After the first build, the site URL is typically:

   `https://normative.readthedocs.io/`  
   (exact slug depends on the RTD project name you choose)

5. Optional: add a badge to the root README once the project exists:

   ```markdown
   [![Docs](https://readthedocs.org/projects/normative/badge/?version=latest)](https://normative.readthedocs.io/)
   ```

No research manuscript content is included — only install, usage, schemas,
and a short methods overview.
