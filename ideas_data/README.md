# `ideas_data/` — IDEAS tabular inputs

Download public IDEAS FreeSurfer stats + metadata and merge them into
`ideas_merged.csv` for the morphometry scorers.

Output schema: [`../docs/INPUT_SCHEMA.md`](../docs/INPUT_SCHEMA.md).

## Build the working table

```bash
# from repository root (Playwright Firefox required — see SETUP.md)
cd ideas_data
python3 fetch_figshare.py
python3 fetch_resection.py    # optional; needed for resection analyses
python3 load_ideas.py         # writes ideas_merged.csv
```

Raw `*.txt` / `*.csv` downloads are gitignored; only scripts +
`manifest.json` ship in the repo.

## What `load_ideas.py` produces

Per-subject rows with:

- `subject_id`, `cohort` (`patient` / `control`), `sex`, `age` (bin midpoint),
  `age_bin`, clinical metadata when present
- DK thickness + area columns (`lh_*_thickness`, …)
- 14 aseg volume columns + `eTIV` and simple globals

## Caveats (IDEAS release)

1. **Age is binned** (5-year windows). Scorers need continuous `age`; we map
   bins to midpoints (`20 to 24` → 22). Document that approximation if you
   publish IDEAS-based results.
2. Open-ended bins (`Less than 20`, `Over 55` / `70+`) use simple tail
   midpoints in `bin_to_midpoint()`.
3. Strip whitespace on age-bin labels before mapping.
4. Use age at **scan**, not surgery, for morphometry scoring.
5. `eTIV` is taken from the aseg / aparc tables, not a separate file.

## Files fetched

| Kind | Examples |
|---|---|
| Patient FS stats | `aparc_thick.txt`, `aparc_area.txt`, `aseg_vol.txt`, … |
| Control FS stats | `controls_aparc_*.txt`, `controls_aseg_vol.txt` |
| Metadata | `Metadata_Release_Anon.csv`, `Metadata_Controls_Release.csv` |
| IDEAS ComBat Z | `{thick,area,vol}_zscores_{patients,controls}.csv` (comparator) |
| Resection | percentages table via `fetch_resection.py` |

Figshare share pages are WAF-gated; the fetch scripts drive Firefox through
Playwright, then download via `ndownloader.figshare.com`.
