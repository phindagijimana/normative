# Building and publishing docs

Canonical user content lives under `docs/` (tutorials, install, methods,
usage reference). Package `README`s are short pointers only.

## Local HTML

```bash
pip install -r docs/requirements.txt
sphinx-build -b html docs docs/_build/html
```

Open `docs/_build/html/index.html`.

## Read the Docs

1. Sign in at https://readthedocs.org/ with GitHub.
2. Import **phindagijimana/normative** (uses `.readthedocs.yaml`).
3. Site URL is typically `https://<project-slug>.readthedocs.io/`.
4. Optional README badge after the first successful build:

   ```markdown
   [![Docs](https://readthedocs.org/projects/<slug>/badge/?version=latest)](https://<slug>.readthedocs.io/)
   ```
