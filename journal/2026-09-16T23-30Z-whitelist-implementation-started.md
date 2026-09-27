# 2026-09-16T23:30Z whitelist implementation started

Worktree `whitelist-assembly` off main. A Sonnet subagent has the brief:
generic `assemble_tree` in porting-harness on `pathspec` patterns, default deny;
the gbnf pattern set in gbnf-experiment, positive names for directories and
files, negation only for the colocated-test conditional; the three removers
deleted, `strip_builder_reexports` kept as the one post-copy edit; pattern list
and included/excluded counts written to the manifest. Red test first: a
`__pycache__` `.pyc` and a `.pytest_cache` in the fixture. Acceptance: file
lists for all 8 conditions against the real derivation differ from the old code
only by `__pycache__`, `*.pyc`, `.pytest_cache`. Reviewed here before any push.
