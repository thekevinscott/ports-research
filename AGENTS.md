# Ports harness — project rules

Scoped to this research harness. Layers on top of the global user preferences.

## The gbnf reference — always

**Never modify the gbnf source, in either language, for any reason.** It is experiment input, not code under maintenance. Bugs in it are findings; a run that repairs one is a result worth recording, not a defect to fix upstream. Changing it changes the corpus hash and severs comparability with every banked run.

This holds for known bugs. `Graph.print()` raising `AttributeError`, `Graph.__init__` re-reading `unique_rules` so dedup never happens, and the unreachable missing-`root` guard are all real, all deliberate to leave alone. Do not fix them, do not file them, do not note them as TODOs in the tree.

The one sanctioned edit is removing whole colocated test files, driven by the `--include-*-tests` flags. Nothing else.

## Running tests — always

Three recipes per package, and nothing else: `just test-unit` (colocated `_test.py` under `src/`), `just test-integration` (`tests/integration`), `just test-e2e` (`tests/e2e`).

**Never run a bare `uv run pytest`.** There is no pytest config narrowing collection, so a bare run at a package root collects `tests/e2e` — real containers, and in `porting-harness` twenty tests that make billed LLM calls. Name the tier you want.

Integration and e2e drive the package's public entry point with inputs and assert on outputs. They never import an internal function or constant, and never build their own `docker.run`.

## Testing — when a defect shows up in the wild

- **A bug observed is a test owed.** Anything that misbehaved in a real run — a crash, a leak, a silent wrong result, an orphaned resource, a value quietly dropped — gets captured as a reproducible test. The test fails first on the current code, then the fix turns it green. A fix without a test proving the defect is a fix that comes back.
- **Reproduce the mechanism, not the incident.** Test the condition that caused it — the teardown path that leaked, the branch that dropped the value — not the exact command that happened to trip it. If the trigger itself isn't coverable (a SIGKILL, a real outage), test the layer that should survive it and note in the test why the trigger is out of scope.
- **One defect, one named test.** The name states the behavior being guaranteed, so a later reader knows what breaks if it goes red.
