# 2026-10-15T12:55Z Run data merged into one tree and moved under DVC

Run directories had accumulated in three places: the root checkout's `data/runs` (42 V1 runs tracked in git, plus later runs untracked), the `sandbox-prompt` worktree, and the `botbox-bump` worktree. They are now one tree, every manifest names its study, and `data/runs`, `data/judge` and `data/walkthroughs` are tracked by DVC. The remote lives in `.dvc/config.local`, outside git.

| Study | Runs |
| --- | --- |
| `v1` | 42 |
| `v2-test-configurations` | 267 |
| `v2-model-effort` | 121 |
| total | 430 |

`"study"` was backfilled into every manifest between `exit_code`/`error` and `condition`, where the writer now puts it (PR #184). The 121 `v2-model-effort` runs include the 6 Fable runs made from the `botbox-bump` worktree.

Left out, still untracked at the root checkout: 17 run directories (3 `claude-opus-5` probes, 1 Haiku 4.5 probe, 11 that never got an exit code, 2 exit-1 runs from the same batch) and 2 probe jsonls.

Six empty run skeletons (no manifest) created in the `sandbox-prompt` worktree by test runs on 2026-10-15 were discarded. They are the defect `--output` fixes: the harness defaulted the run directory from the package path, so a worktree's test run could land there.

DVC does not store dangling symlinks and would follow a loop, so `.dvcignore` excludes 60 symlinks agents left in `ported_implementation/` (`node_modules/vitest`, `node_modules/gbnf`, `.venv/bin/python*`, `.venv/lib64`). Every regular file is tracked: 24,202 under `runs`. A complete snapshot including the links is `data-2026-10-15.zip` at the repo root, gitignored.
