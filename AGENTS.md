# Ports harness — project rules

Scoped to this research harness. Layers on top of the global user preferences.

## The gbnf reference — always

**Never modify the gbnf source, in either language, for any reason.** It is experiment input, not code under maintenance. Bugs in it are findings; a run that repairs one is a result worth recording, not a defect to fix upstream. Changing it changes the corpus hash and severs comparability with every banked run.

This holds for known bugs. `Graph.print()` raising `AttributeError`, `Graph.__init__` re-reading `unique_rules` so dedup never happens, and the unreachable missing-`root` guard are all real, all deliberate to leave alone. Do not fix them, do not file them, do not note them as TODOs in the tree.

The one sanctioned edit is removing whole colocated test files, driven by the `--include-*-tests` flags. Nothing else.

## Worktrees — always

**All work happens in git worktrees under `.worktrees/`.** Never edit files in
the primary checkout; it stays on `main` and clean. `.worktrees/` is
gitignored.

- Create one worktree per branch/PR: `git worktree add .worktrees/<branch> -b <branch>`.
  The worktree directory name and the branch name are **identical** —
  `.worktrees/<branch>` always contains branch `<branch>`.
- Branch names use **dashes only**: lowercase letters, digits, and `-`.
  No slashes, no spaces (e.g., `whitelist-assembly`, not `feat/whitelist-assembly`).
- Do all editing, building, and testing inside `.worktrees/<branch>/`.
- When the PR merges, remove the worktree: `cd` to the root checkout first, then
  `git worktree remove .worktrees/<branch>`.

## Merging — always

**Never merge into main locally.** Kevin, 2026-09-16: "never merge into main
locally again. Only on Github via PRs."

- Agents open PRs and stop there. Kevin merges through the GitHub UI.
- Never merge on your own initiative, however green the checks are.
- Never suggest merging, and never offer to merge as a next step.
- Never push to `main`. Local `main` only ever moves by pulling from GitHub.
- The only exception is an explicit, specific instruction from Kevin to merge a
  named PR. That instruction is always his to initiate, and it is rare.

## Journal — when something major happens

`JOURNAL.md` at the repo root is the append-only lab record. A run started or
finished, a finding, a decision, a tool landed: one entry each, UTC timestamp
in the heading, newest at the bottom. Never edit an earlier entry; add a new
one that corrects it.

## Running tests — always

Three recipes per package, and nothing else: `just test-unit` (colocated `_test.py` under `src/`), `just test-integration` (`tests/integration`), `just test-e2e` (`tests/e2e`).

**Never run a bare `uv run pytest`.** There is no pytest config narrowing collection, so a bare run at a package root collects `tests/e2e` — real containers, and in `porting-harness` twenty tests that make billed LLM calls. Name the tier you want.

Integration and e2e drive the package's public entry point with inputs and assert on outputs. They never import an internal function or constant, and never build their own `docker.run`.

## CI workflows

One workflow file per package/lane (`.github/workflows/<package>-ci.yml`), triggered by that lane's own paths on `pull_request` — the pattern in `thekevinscott/dirsql`. A change to a package runs that package's checks and nothing else; a change to no lane runs nothing.

Lanes deliberately do not list their own file as a trigger. Stacked branches carry every sibling lane file in their diff, so a self-trigger would fire every lane on every package PR and defeat the filtering. A lane-file edit is exercised by the next PR that touches that package.

No inline scripts in workflow YAML. Use native mechanisms — `paths:` filters, reusable-workflow inputs, matrix — instead of `run:` blocks implementing logic like change detection; when logic is genuinely needed, it lives in a committed script or composite action, not inline in the workflow.

## Testing — when a defect shows up in the wild

- **A bug observed is a test owed.** Anything that misbehaved in a real run — a crash, a leak, a silent wrong result, an orphaned resource, a value quietly dropped — gets captured as a reproducible test. The test fails first on the current code, then the fix turns it green. A fix without a test proving the defect is a fix that comes back.
- **Reproduce the mechanism, not the incident.** Test the condition that caused it — the teardown path that leaked, the branch that dropped the value — not the exact command that happened to trip it. If the trigger itself isn't coverable (a SIGKILL, a real outage), test the layer that should survive it and note in the test why the trigger is out of scope.
- **One defect, one named test.** The name states the behavior being guaranteed, so a later reader knows what breaks if it goes red.

