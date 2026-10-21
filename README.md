# pnas2026-solverfiles

Solver input files for the full-Stokes Elmer/Ice simulations in:

> Rines, J., et al. (2026). *[title TBD — fill at release]*. PNAS.

Each simulation directory is self-contained and ready to run: it holds the
exact solver input file (`.sif`), the mesh geometry (`.geo`), and the DEM /
auxiliary inputs that simulation needs, plus a short README with the commands
to mesh and run it.

## Layout

```
elmerice/
├── real_topography/        # 25 km × 25 km tiles on real Greenland topography
│   ├── viscous/            # free-slip slippery-patch simulations (pre/post drainage)
│   │   └── 2019cwNNNN/     # one directory per center-lake tile
│   └── elastic/            # pressurized-blister elastic simulations
│       └── 2019cwNNNN/
└── idealized/              # idealized-geometry simulations from the SI
```

(`elmerice/` is the Elmer/Ice group; viscoelastic SiStER inputs, if added
later, would live in a sibling directory.)

## Requirements

- Elmer/Ice version: **TBD — pinned from production run logs before release**
- The production runs used the Docker image `andrewdnolan/elmerice`.

## Status

Under construction — contents are being assembled and verified against the
production run inputs. Do not use until this notice is removed.
