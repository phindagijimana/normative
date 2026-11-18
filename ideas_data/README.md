# `ideas_data/`

Download public IDEAS FreeSurfer stats + metadata and merge
`ideas_merged.csv` for the morphometry scorers.

**Docs:** [Tutorial 1](../docs/tutorials/01_ideas_morphometry.md) ·
[Input schema](../docs/inputs.md) · [Install](../docs/installation.md)

```bash
python3 fetch_figshare.py
python3 fetch_resection.py   # optional
python3 load_ideas.py        # → ideas_merged.csv
```

Raw downloads are gitignored; scripts + `manifest.json` ship in the repo.

## IDEAS caveats

1. Age is **binned**; `load_ideas.py` maps bins to midpoints.  
2. Strip whitespace on age-bin labels.  
3. Use age at **scan**, not surgery.  
4. `eTIV` comes from aseg / aparc tables.  
5. Figshare is WAF-gated — Playwright Firefox is required for fetchers.
