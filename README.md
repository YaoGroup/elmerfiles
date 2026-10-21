# pnas2026-solverfiles

Elmer/Ice solver input files for:

> Lai, C.-Y., Rines, J. H., Coffey, N. B., Lee, E., Clerc, F., Hilditch, J. P.,
> Gagliardini, O., & Stevens, L. A. (2026). *From blistering to sliding:
> Ice-sheet stress perturbations from water injection to the bed.* PNAS.

These are the exact solver input files (`.sif`) used for the full-Stokes
Elmer/Ice simulations in the paper: viscous (free-slip slippery patch) and
elastic (pressurized subglacial blister) stress-perturbation simulations of
seven supraglacial-lake tiles on real Greenland topography (lakes 1910, 1951,
2394, 2411, 2416, 2511, 2520 in the naming of the Dunmire et al. 2021 catalog),
plus the idealized-slab simulations from the SI.

Each simulation directory is self-contained and ready to run: the `.sif`, the
mesh geometry (`.geo`), and the DEM / auxiliary inputs that simulation needs,
with a short README giving the commands to mesh and run it.

## Layout

```
elmerice/
├── real_topography/        # 25 km × 25 km tiles on real Greenland topography
│   ├── viscous/            # free-slip slippery-patch simulations (pre/post drainage)
│   │   └── 2019cwNNNN/     # one directory per center-lake tile
│   └── elastic/            # pressurized-blister elastic simulations
│       └── 2019cwNNNN/
└── idealized/              # idealized-slab simulations from the SI
```

(`elmerice/` is the Elmer/Ice group; the 2D viscoelastic SiStER configurations,
if added later, would live in a sibling directory.)

## Software versions

- **Elmer/Ice: Elmer v 9.0 (Rev: cf291b69, compiled 2021-11-03)**, with MUMPS
  and the Lua interpreter linked in.
- Production runs used the Docker image `andrewdnolan/elmerice`.

## Status

Under construction — contents are being assembled and verified against the
production run inputs. Do not use until this notice is removed.
