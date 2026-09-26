---
name: gbnf-reference-tests-in-pycache
description: "The GBNF reference_implementation's deleted *_test.py sources are recoverable from its __pycache__ .pyc files"
metadata: 
  node_type: memory
  type: project
  originSessionId: 4e4dd317-77b2-4a62-9897-12985f433dfc
  modified: 2026-09-09T01:14:28.654Z
---

In `/workspace`, `reference_implementation/` ships with all `*_test.py` sources deleted, but
the compiled `__pycache__/*_test.cpython-314-pytest-9.1.1.pyc` files remain, and the container's
Python is 3.14 — the same version that produced them. The full test suite is recoverable:
`marshal.loads(open(pyc,'rb').read()[16:])` yields the module code object, which can be
`exec`'d after stubbing `pytest` and `_pytest.assertion.rewrite` in `sys.modules`. Stubbing
`pytest.mark.parametrize` with a recorder captures the test tables verbatim (41 grammar cases
for `rules_builder_test`, 12 for `build_rule_stack_test`); pytest-describe `describe_*` bodies
must be invoked manually since they only run at collection time. Recovered test functions can
then be executed against the reference — if `_pytest.assertion.rewrite` helpers are never
called, every assertion passed.

**Why:** Without this, the reference's expected values have to be guessed or re-derived, and
a port has no ground truth to check against.

**How to apply:** Use this to extract golden fixtures before porting or refactoring the GBNF
reference. See also [[gbnf-workspace-tests-dir-readonly]].
