# 2026-09-26T22:30Z repo laid out as porting/ and analysis/

Kevin: "There is code related to performing the porting; then there's code
related to analysis and scoring after the fact. They're very different things."
PR #67 moved the three chain packages under `porting/`, the notebook and every
measurement tool under `analysis/`, the 42 banked runs to `data/runs/`, and the
paper corpus and harvester under `literature/`. `packages/` and
`proposed-projects/` are gone as labels. template-viewer (#66) and
contamination-probe (#68) deleted: nothing called either, no banked run used
them, and no ask from Kevin created them. Kevin on execute-test-suite, when an
agent called it the scorer: "It absolutely is NOT the scorer. We are NOT
scoring on integration test fidelity." The root README sentence that said so
was agent text and is removed.
