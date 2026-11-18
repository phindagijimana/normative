# Building docs

Canonical site layout: **science/** (field theory + literature) and
**toolkit/** + **tutorials/** + **usage/** (this software only).

```bash
pip install -r docs/requirements.txt
sphinx-build -b html docs docs/_build/html
```

Live site: https://normative.readthedocs.io/ (`.readthedocs.yaml`).
