# 2026-09-26T23:55Z the prepare image owns the corpus

Kevin: "I want gbnf-experiment's container to copy all relevant files to a
specific folder - so that will be packages/{language} and tests/{lang} - to
/reference/source and reference/tests. /reference is the folder that will be
synced back." And: "I think that that means the whitelist glob step can happen
in the docker container, right?" It can, and now does. The prepare image is
built once per condition, with the source language and the two test flags as
build args; it generates only the flagged suites, filters the source package
with an `rsync` merge file, and assembles `/reference`. The host builds the
image, copies `/reference` out with `docker create` plus `docker cp`, and hands
the folder to porting-harness. It selects nothing and stages nothing; the
manifest's `included` list is read back off the copied-out folder.

Gone with it: the content-keyed prepared-corpus cache, the host-side pattern
whitelist (`reference_patterns.py`), `assemble_reference_implementation`, and the
run-time `CMD` that copied `/prepared` out through a bind mount. The corpus is
now decided in exactly one place, and the eight listings under
`porting/gbnf-experiment/tests/integration/fixtures/reference/` are asserted file
for file against a real build of each condition. PR for #72.
