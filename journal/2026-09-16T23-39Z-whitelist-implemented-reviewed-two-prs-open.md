# 2026-09-16T23:39Z whitelist implemented, reviewed, two PRs open

The Sonnet subagent's whitelist reviewed and pushed. `assemble_tree` in
porting-harness on `pathspec`, default deny, symlinks skipped; `reference_patterns`
in gbnf-experiment with anchored root entries and one negation for withheld
colocated tests; the three removers deleted; manifest carries the patterns and
what was withheld. The 8-condition comparison against the cached derivation was
re-run independently: old and new differ only by 35 `__pycache__`/`.pyc` paths on
the python side, typescript identical. Unit suites 49 and 168 green. PR #23,
stacked on PR #22, a one-line conftest fix split out because it is unrelated:
main's integration suite patched a name lockdown no longer imports and failed at
fixture setup.

Found in passing, not fixed: `ClaudeAgent` binds the real `~/.claude` as a
default argument at definition time, so the integration fixture's patch never
reaches it and the suite mounts the real credentials file. The one failing test
prints the live token in its assertion diff. Separate fix due in
agent-harness-sandbox.
