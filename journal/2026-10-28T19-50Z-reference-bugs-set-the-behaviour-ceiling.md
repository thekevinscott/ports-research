# 2026-10-28T19:50Z — The two handwritten references disagree on 25 of 799 behaviour pairs, and those 25 are the whole residual for 119 of 126 driven ports

`measure-behavior compare --reference corpus/reference-typescript.jsonl --port corpus/reference-python.jsonl`: the Python and TypeScript references agree on 774/799 held-out pairs.

The 25 disagreements:

- 20: TypeScript rejects, Python accepts. Every input contains U+1F600; the TypeScript reference stores it as UTF-16 code units (API cache: reference `value: [55357]`, ports `128512`). Grammars g0030, g0051, g0059, g0063, g0073, g0083, g0099.
- 5: TypeScript rejects, Python raises `IndexError: list index out of range` on inputs that run past a fully matched literal root (g0055 inputs 4, 5; g0088 7; g0095 7, 8).

Neither reference's own tests contain U+1F600, so no supplied suite could expose either case.

Three-way run over all 192 v2-tests-configuration ports (`measure-behavior run` per port against the corpus, then per-pair comparison with both references):

| driven ports | 126 |
|---|---|
| match the target on all 774 agreed pairs, and match neither bug on the 25 | 119 |
| carried the source reference's bug (3 py→js raise on the 5; 1 js→py rejects the 20) | 4 |
| carried the target reference's bug | 0 |
| own defects (2 js→py unit+source ports with the identical 111-pair over-accept set; 1 py→js all-tests port rejecting 13 emoji inputs both references accept) | 3 |

The 4 source-bug carriers were in conditions none, source, source+target (py→js) and none (js→py); none had unit tests.

Consequence for the notebook's numbers: 97.5% (py→js) and 99.4% (js→py) median agreement are 779/799 and 794/799, the ceilings a correct port can reach against each target reference as the scorer. Per AGENTS.md the gbnf bugs stay in place; this entry records them as findings.
