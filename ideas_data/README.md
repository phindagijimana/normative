# IDEAS tabular data — CentileBrain validation inputs

Downloaded 2026-09-18 via `fetch_figshare.py` (Playwright + Firefox drives
Figshare's WAF-gated share pages; downloads then go through
`ndownloader.figshare.com/files/<id>?private_link=<token>`).

Total footprint: ~3.3 MB across 17 files.

## Files

### FreeSurfer stats — patients (442 subjects, IDs 1–463 with gaps)
| File | Content | Rows × Cols |
|---|---|---|
| `aparc_thick.txt` | DK cortical **thickness** (both hemispheres stacked) | 75 × (1 + N) |
| `aparc_area.txt`  | DK cortical **surface area** | 75 × (1 + N) |
| `aparc_vol.txt`   | DK cortical **volume** (not used by CentileBrain) | 73 × (1 + N) |
| `aseg_vol.txt`    | Aseg **subcortical volumes** + global summaries | 64 × (1 + N) |

Layout is transposed: rows = features (region names), columns = subjects
(integer IDs matching `sub-<N>` in the BIDS tree). Each aparc file contains
two hemispheric blocks stacked (rh header + 34 rh regions + rh mean +
BrainSegVolNotVent + eTIV, then the same for lh).

### FreeSurfer stats — controls (100 subjects, IDs 4001–41xx)
`controls_aparc_thick.txt`, `controls_aparc_area.txt`,
`controls_aparc_vol.txt`, `controls_aseg_vol.txt` — same layout.

### Metadata
- `Metadata_Release_Anon.csv` — 442 patients. Cols: `ID, Sex, Binned_Onset_Age,
  FUS, fqFUS, FBTCS, fqFBTCS, SE, Op_Side, Op_Type, Pathology, OP MEMO,
  Number_ASMs, Binned_Age_at_Scan, Binned_Age_at_Surgery, ILAE_Year1..5`.
- `Metadata_Controls_Release.csv` — 100 controls. Cols: `ID, Sex,
  Binned_Age_at_Scan`.
- `readme_metadata.pdf` — CNNP's own README for these tables.

### IDEAS's own ComBat-harmonised Z-scores (patients scored vs. 100 controls)
`{thick,area,vol}_zscores_{patients,controls}.csv` — used as an internal
comparator for whatever we produce with CentileBrain.

## Cohort summary
| Group | N | Sex | Age bins present |
|---|---|---|---|
| Patients | 442 | 238 F / 205 M (1 missing) | 5-year bins in the working-age range + open-ended tails |
| Controls | 100 | 62 F / 38 M | `Less than 20`, `20–24`, `25–29`, `30–34`, `35–39` (15), `40–44`, `45–49`, `50–54`, `Over 55` |

## Critical caveats for CentileBrain application

1. **Age is binned in 5-year windows, not continuous.** CentileBrain's MFPR
   takes continuous age (with fractional-polynomial transforms). We must map
   bins to numeric midpoints (`20–24` → 22.5, `Over 55` → e.g. 60 or 70, etc.)
   and treat this as a source of expected error / smoothing. Same choice must
   be used for every downstream comparison.
2. **`Over 55` and `Less than 20`** are open-ended — need explicit imputation
   rules (median or upper-bound midpoint), documented in the analysis
   pipeline.
3. **One control row has a leading whitespace** (` 35 to 39` vs `35 to 39`) —
   strip whitespace before matching bins.
4. **Age at surgery ≠ age at scan** — patients have both; for CentileBrain
   use `Binned_Age_at_Scan`.
5. **eTIV is inside the aparc + aseg tables**, not a separate file. Extract
   from `aseg_vol.txt` (or `aparc_thick.txt` row `eTIV`) for the ICV
   covariate expected by CentileBrain's subcortical volume models.

## Not downloaded (available on demand)

From the same source pages:
- Resection percentages per DK region (`097ba0e254e36f0eee52`) — needed only
  for the Phase 2 resection-concordance analysis.
- Resection masks in native space (`476b37fd883c14f50324`) — same.
- Full FreeSurfer recon-all surfaces (~100–200 GB) — only if we need to
  regenerate anything.
- Raw T1w BIDS — already on OpenNeuro `ds005602` and locally at
  `~/Documents/IDEAS/bids_IDEAS/`.

## FreeSurfer version
Not stated on the Figshare page or in the readme_metadata.pdf. Need to check
Taylor et al. 2025 (*Epilepsia*, doi:10.1111/epi.18192) or the Veritas repo
(where IDEAS is the first target dataset, so the FS version must already be
pinned in `~/Documents/validator/`).
