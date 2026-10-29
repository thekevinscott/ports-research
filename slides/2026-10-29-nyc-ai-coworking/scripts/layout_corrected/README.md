# Layout-corrected similarity

Scratch scripts, kept as run on 2026-10-29 for provenance of `public/layout-corrected.csv`. Paths are hardcoded to the machine they ran on.

- `plan.py` lists the 134 models-effort ports whose package is not where the reference keeps it and the relocation to apply.
- `run.py` copies each port to scratch, moves the package directory, and measures with `measure-code-distance git-diff` (same `--a`, `--language` and excludes as the notebook).
- `rename.py` lower-cases and dashes every name under `src/` for the 62 Python → TypeScript ports that stayed flat after relocation, and measures again. `*_test.ts` files keep their names so the exclude still matches them.
- `measure.py` wraps the measure command.
