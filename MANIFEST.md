# Simulation manifest

Every simulation in this repository appears in a figure of the paper or its
SI. Lake directories are named by the paper's lake IDs (Dunmire et al. 2025
catalog); the table below maps them to the internal `2019cw` IDs used in the
original run filenames (internal ID + 1523 = paper ID).

| Paper lake ID | Internal ID | c_b (viscous) [Pa s^m L^-m] | P_w/P_i (elastic blister) |
|---|---|---|---|
| 1910 | 2019cw387 | 5.4e6 | 1.0378 |
| 1951 | 2019cw428 | 6.5e6 | 1.0276 |
| 2394 | 2019cw871 | 8.5e6 | 1.0164 |
| 2411 | 2019cw888 | 8.5e6 | 1.0306 |
| 2416 | 2019cw893 | 7.5e6 | 1.0309 |
| 2511 | 2019cw988 | 8.6e6 | 1.0298 |
| 2520 | 2019cw997 | 6.7e6 | 1.0257 |

## Contents and where each simulation appears

**`real_topography/viscous/lakeNNNN/`** — one Glen-rheology free-slip-patch
simulation per lake (`*_tsic_base.sif`, run twice: patch and no-patch case
toggled inside the SIF). Feed main-text Figs. 1, 4, 5 and the SI per-lake
viscous overview and phase-space figures.
`lake2394/resolution_convergence/` holds the coarse/mid/fine mesh-resolution
runs behind the SI convergence figure.

**`real_topography/elastic/lakeNNNN/`** — two simulations per lake at
E = 3.077 GPa with the local-thickness blister pressure BC: the undisturbed
reference (`*_nopatch_u0p0*.sif`) and the pressurized blister at the
calibrated water pressure (`*_blister_u0p0_Pw*.sif`). Feed main-text Fig. 1
and the SI per-lake elastic overview and phase-space figures.
`lake2394/patch_experiments_E9GPa/` holds the basal-sliding sensitivity sweep
(patch/no-patch at u_b = 0, 0.5, 1.0 m, E = 9 GPa) behind the SI
`patch_perturbation_vs_ub` figure. The E value differs from the rest of the
paper by design; this is faithful to what that figure shows.

**`idealized_slab/`** — 26 Newtonian flat-slab simulations (`flatslabnewt_*_G01`)
behind published Fig. 3: the sim-vs-theory maps (panel A), profile collapse
(panel C) and maxima scatter (panel D), plus the SI polar stress comparison.
All have cH/η = 0.1 (`G01`). `flatslabnewt_R2500_H1000_a05_G01` is the
quickstart worked example in the README.

## Provenance and verification

Files were taken from the production run environment and verified against the
run logs and the output files consumed by the figure pipeline (solver version,
output-name tokens, and physics-critical parameters: E at its three sites in
the elastic SIFs, the local-thickness blister BC, SICOPOLIS temperature
profile, per-lake c_b and P_w). Renaming to paper lake IDs was mechanical and
checked by reverse-mapping every file back to its original (byte-identical).

Four files are documented reconstructions, where the file on disk had been
edited after its production run (parameter-sweep leftovers). Each was restored
to the state of the run the paper used, anchored to the run logs and output
filenames:

1. `viscous/lake2416/*_tsic_base.sif` — c_b restored from a later 5.5e6 trial
   to the production 7.5e6 (the paper's c_b for lake 2416).
2. `viscous/lake2394/*_tsic_base.sif` — a post-run `_vl20` output-name edit
   reverted to the production output names.
3. `elastic/lake2394/patch_experiments_E9GPa/*_u0p0.sif` (both cases) — the
   u_b = 0 member of the 9 GPa sweep, recovered from the untouched u_b = 0.5
   sibling by changing only u_b and its filename token (the on-disk u0p0 file
   had been overwritten by a later, different-generation rerun).
