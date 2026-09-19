"""Apply the PCN Toolkit lifespan_DK_46K_59sites pre-trained models
(Rutherford et al., eLife 2022 / Nature Protocols 2022; hierarchical
Bayesian regression) to the IDEAS cohort.

Because IDEAS is a new scanning site (Newcastle 3T Prisma) not present
in the 59 training sites, we use the PCN Toolkit's built-in adaptation
mechanism: IDEAS controls (100) supply the adaptation data, IDEAS
patients (442) are the test set. This is the PCN-specific implementation
of the same site-adaptation principle we apply for the CentileBrain
backends via mu_hat (Rutherford 2022; see ../mu_hat.md).

Output schema matches score/score_centilebrain_gamlss.R:
long-form CSV with columns
    subject_id, cohort, sex, age, measure, region, observed, z
"""
from __future__ import annotations

import os
import shutil
import sys
import tempfile
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path("/mnt/nfs/home/URMC-SH/pndagiji/Documents/Normative")
PCN_ROOT = ROOT / "pcn_models" / "braincharts"
MODEL_DIR = PCN_ROOT / "models" / "lifespan_DK_ct" / "lifespan_DK_46K_59sites"
DOCS = PCN_ROOT / "docs"
OUT_DIR = ROOT / "score"

# PCNtoolkit scripts folder must be on path for nm_utils
sys.path.insert(0, str(PCN_ROOT / "scripts"))
from pcntoolkit.normative import predict          # noqa: E402
from pcntoolkit.util.utils import create_design_matrix  # noqa: E402

# ---- Load region + site metadata -----------------------------------------
def _load_list(fp: Path) -> list:
    return [l.strip() for l in fp.read_text().splitlines() if l.strip()]

idp_lh = _load_list(DOCS / "phenotypes_ct_dk_lh.txt")  # 34
idp_rh = _load_list(DOCS / "phenotypes_ct_dk_rh.txt")  # 33 (PCN model is missing one — see below)
idp_sc = _load_list(DOCS / "phenotypes_sc.txt")        # 37 (includes many we don't have)
site_ids_tr = _load_list(DOCS / "site_ids_ct_dk_59sites.txt")

print(f"PCN model IDPs — LH cortical: {len(idp_lh)}, "
      f"RH cortical: {len(idp_rh)}, subcortical: {len(idp_sc)}")
print(f"PCN training sites: {len(site_ids_tr)}")

# ---- Map IDEAS column names ↔ PCN IDP names -----------------------------
# PCN cortical: L_bankssts, R_insula, ...
# IDEAS cortical: lh_bankssts_thickness, rh_insula_thickness, ...
def ideas_to_pcn_cortical(ideas_col: str) -> str:
    """lh_bankssts_thickness -> L_bankssts; rh_insula_thickness -> R_insula"""
    hemi_prefix = {"lh_": "L_", "rh_": "R_"}
    for h_ideas, h_pcn in hemi_prefix.items():
        if ideas_col.startswith(h_ideas) and ideas_col.endswith("_thickness"):
            region = ideas_col[len(h_ideas):-len("_thickness")]
            return h_pcn + region
    raise ValueError(f"Not a cortical thickness column: {ideas_col}")

# PCN subcortical: Left-Thalamus-Proper, Right-Hippocampus, etc.
# IDEAS aseg: Left-Thalamus, Right-Hippocampus, etc.
ASEG_MAP = {
    "Left-Thalamus":  "Left-Thalamus-Proper",
    "Right-Thalamus": "Right-Thalamus-Proper",
    "Left-Caudate":   "Left-Caudate",
    "Right-Caudate":  "Right-Caudate",
    "Left-Putamen":   "Left-Putamen",
    "Right-Putamen":  "Right-Putamen",
    "Left-Pallidum":  "Left-Pallidum",
    "Right-Pallidum": "Right-Pallidum",
    "Left-Hippocampus":  "Left-Hippocampus",
    "Right-Hippocampus": "Right-Hippocampus",
    "Left-Amygdala":  "Left-Amygdala",
    "Right-Amygdala": "Right-Amygdala",
    "Left-Accumbens-area":  "Left-Accumbens-area",
    "Right-Accumbens-area": "Right-Accumbens-area",
}

# ---- Load IDEAS data + build the PCN-format frame -----------------------
ideas = pd.read_csv(ROOT / "ideas_data" / "ideas_merged.csv")
ideas["sex"] = ideas["sex"].str.upper().str.strip()
ideas = ideas[ideas["sex"].isin(["M", "F"])].copy()
ideas = ideas[ideas["age"].notna()].copy()
ideas["sex_bin"] = (ideas["sex"] == "M").astype(int)  # PCN convention: 1=male, 0=female

# Assign IDEAS as a new synthetic site name (not in training list).
ideas["site"] = "IDEAS_Newcastle"
ideas["sitenum"] = len(site_ids_tr)  # placeholder, unique to IDEAS

# Build PCN-format dataframe
pcn_cols = {"sub_id": ideas["subject_id"].astype(str),
             "age": ideas["age"], "sex": ideas["sex_bin"],
             "site": ideas["site"], "sitenum": ideas["sitenum"]}

# Cortical IDPs (only include those PCN has a model for)
cortical_ideas_cols = []
pcn_names = set(idp_lh + idp_rh)
for h_ideas in ("lh_", "rh_"):
    for c in ideas.columns:
        if c.startswith(h_ideas) and c.endswith("_thickness"):
            pcn_name = ideas_to_pcn_cortical(c)
            if pcn_name in pcn_names and (MODEL_DIR / pcn_name).exists():
                pcn_cols[pcn_name] = ideas[c]
                cortical_ideas_cols.append((c, pcn_name))

# Subcortical
subcortical_ideas_cols = []
for ideas_name, pcn_name in ASEG_MAP.items():
    if ideas_name in ideas.columns and (MODEL_DIR / pcn_name).exists():
        pcn_cols[pcn_name] = ideas[ideas_name]
        subcortical_ideas_cols.append((ideas_name, pcn_name))

df_all = pd.DataFrame(pcn_cols)
print(f"IDEAS in PCN format: {len(df_all)} subjects, "
      f"{len(cortical_ideas_cols)} cortical + {len(subcortical_ideas_cols)} "
      f"subcortical IDPs")

# Split into adaptation (controls) + test (all subjects — patients + controls)
ideas_reset = ideas.reset_index(drop=True)
df_all = df_all.reset_index(drop=True)
mask_ctl = ideas_reset["cohort"] == "control"
df_ad = df_all[mask_ctl].copy()
df_te = df_all.copy()  # score everyone (controls will be near-zero if adapt works)
print(f"Adaptation (controls): N={len(df_ad)}   Test (all subjects): N={len(df_te)}")

# ---- Design matrix parameters (from apply_normative_models_ct.py) --------
cols_cov = ["age", "sex"]
xmin, xmax = -5, 110

# ---- Score IDP by IDP ----------------------------------------------------
all_idps = [(c[0], c[1], "thickness") for c in cortical_ideas_cols] + \
           [(c[0], c[1], "subcortical") for c in subcortical_ideas_cols]

results_rows = []
tmpdir = Path(tempfile.mkdtemp(prefix="pcn_score_"))
print(f"\nScoring {len(all_idps)} IDPs with PCN-Bayesian ... (tmpdir: {tmpdir})")

# Silence PyMC warnings during batch scoring
import warnings; warnings.filterwarnings("ignore")

cov_file_te = tmpdir / "cov_te.txt"
cov_file_ad = tmpdir / "cov_ad.txt"
sitenum_file_te = tmpdir / "sitenum_te.txt"
sitenum_file_ad = tmpdir / "sitenum_ad.txt"

# Design matrices are IDP-agnostic — build once
X_te = create_design_matrix(df_te[cols_cov], site_ids=df_te["site"],
                             all_sites=site_ids_tr, basis="bspline",
                             xmin=xmin, xmax=xmax)
X_ad = create_design_matrix(df_ad[cols_cov], site_ids=df_ad["site"],
                             all_sites=site_ids_tr, basis="bspline",
                             xmin=xmin, xmax=xmax)
np.savetxt(cov_file_te, X_te)
np.savetxt(cov_file_ad, X_ad)
np.savetxt(sitenum_file_te, df_te["sitenum"].to_numpy(dtype=int))
np.savetxt(sitenum_file_ad, df_ad["sitenum"].to_numpy(dtype=int))

fail_count = 0
for i, (ideas_name, pcn_name, measure) in enumerate(all_idps):
    idp_model = MODEL_DIR / pcn_name / "Models"
    if not idp_model.exists():
        continue
    # Response variables
    resp_te = tmpdir / f"resp_te_{pcn_name}.txt"
    resp_ad = tmpdir / f"resp_ad_{pcn_name}.txt"
    np.savetxt(resp_te, df_te[pcn_name].to_numpy())
    np.savetxt(resp_ad, df_ad[pcn_name].to_numpy())

    # Working dir must be the IDP model dir per PCN convention
    cwd = os.getcwd()
    idp_workdir = tmpdir / pcn_name
    idp_workdir.mkdir(exist_ok=True)
    os.chdir(idp_workdir)
    try:
        yhat, s2, Z = predict(
            str(cov_file_te), alg="blr", respfile=str(resp_te),
            model_path=str(idp_model),
            adaptrespfile=str(resp_ad),
            adaptcovfile=str(cov_file_ad),
            adaptvargroupfile=str(sitenum_file_ad),
            testvargroupfile=str(sitenum_file_te),
        )
    except Exception as e:
        os.chdir(cwd)
        fail_count += 1
        if fail_count <= 3:
            print(f"  [{i}/{len(all_idps)}] {pcn_name}: FAILED — {e}")
        continue
    os.chdir(cwd)

    # Z is a numpy array (N x 1). Flatten.
    Z_flat = np.asarray(Z).squeeze()
    y_flat = df_te[pcn_name].to_numpy()

    if (i + 1) % 20 == 0:
        print(f"  [{i+1}/{len(all_idps)}] {pcn_name}: mean Z={np.nanmean(Z_flat):+.3f}  "
              f"SD Z={np.nanstd(Z_flat):.3f}")

    for j in range(len(df_te)):
        results_rows.append({
            "subject_id": df_te["sub_id"].iloc[j],
            "cohort":     ideas_reset["cohort"].iloc[j],
            "sex":        ideas_reset["sex"].iloc[j],
            "age":        ideas_reset["age"].iloc[j],
            "measure":    measure,
            "region":     ideas_name,   # store using OUR canonical naming
            "pcn_region": pcn_name,
            "observed":   y_flat[j],
            "z":          Z_flat[j] if Z_flat.ndim >= 1 else Z_flat,
        })

# ---- Save + report ------------------------------------------------------
long = pd.DataFrame(results_rows)
out_csv = OUT_DIR / "ideas_zscores_pcn.csv"
long.to_csv(out_csv, index=False)
print(f"\nWrote {len(long)} rows to {out_csv}")
print(f"Failed IDPs: {fail_count} / {len(all_idps)}")

# Distribution summary matching the CentileBrain outputs
print("\n=== PCN Toolkit Z distribution ===")
for co in long["cohort"].unique():
    z = long.loc[long["cohort"] == co, "z"].to_numpy()
    print(f"  cohort={co:8s}  n={len(z)}  mean={np.nanmean(z):+.3f}  sd={np.nanstd(z):.3f}")

# Cleanup tmp
shutil.rmtree(tmpdir, ignore_errors=True)
print(f"\nDone. Tmpdir cleaned.")
