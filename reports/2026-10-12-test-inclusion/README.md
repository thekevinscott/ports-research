# What effect does including tests have on an LLM's port?

2026-10-12

The question, in Kevin’s words: “what effect does test inclusion have on produced output”.

An agent (`claude-opus-5-5`, effort medium) ports the gbnf library between Python and JavaScript. Three flags control the supplied suites: `include_unit_tests`, `include_source_integration_tests`, and `include_target_integration_tests`. Two source languages × eight flag combinations = 16 cells × 12 successful runs = 192 ports. Unit tests describe internals, source integration tests describe behaviour in the source language, and target integration tests describe the expected interface in the target language.

“unit” means source unit tests, “source” means source integration tests, “target” means target integration tests, and “all” means all three. Counts below come from the five matrix logs dated 2026-10-12 at 02:13:10Z, 09:49:53Z, 10:09:20Z, 11:03:50Z, and 12:08:14Z; their `cell` objects are mapped to the notebook’s condition labels. Nonzero exits are excluded from every chart and successful-port summary.

| Source | Given tests | Successful ports | Exit 1 | Exit 137 |
| --- | --- | --- | --- | --- |
| python | none | 12 | 4 | 0 |
| python | unit | 12 | 4 | 0 |
| python | source | 12 | 4 | 0 |
| python | target | 12 | 4 | 0 |
| python | unit + source | 12 | 5 | 0 |
| python | unit + target | 12 | 5 | 0 |
| python | source + target | 12 | 4 | 0 |
| python | all | 12 | 4 | 0 |
| javascript | none | 12 | 5 | 3 |
| javascript | unit | 12 | 4 | 0 |
| javascript | source | 12 | 4 | 3 |
| javascript | target | 12 | 4 | 0 |
| javascript | unit + source | 12 | 4 | 0 |
| javascript | unit + target | 12 | 4 | 0 |
| javascript | source + target | 12 | 4 | 1 |
| javascript | all | 12 | 4 | 1 |

## Does including tests change what the port does?

**Why.** Each port and the reference in its target language run the same held-out corpus: 100 grammars and 799 grammar–input pairs, never supplied to the agent. We count agreement on accept, reject, error, or crash, then divide by 799. A high percentage means more equal outcomes, including equal errors; a low percentage means more different outcomes. The hypothesis is that source and target integration tests increase agreement by giving behavioural examples; unit tests may increase agreement on internal cases. A difference would establish different agreement on this corpus, not correctness on all inputs or whether the reference’s behaviour is desirable. The confusion counts show which outcomes were compared. [Measure definition](https://github.com/thekevinscott/ports-research/blob/8999c36b8d8ed765f20682fc54f9799a317750ad/analysis/measure-behavior/README.md).

![Held-out behavior agreement with the reference (%)](charts/behavior-agreement-pct.png)

Held-out behavior agreement with the reference (%): each dot is one port, the tick is its condition’s median, the faint bar spans its interquartile range, and one panel represents each source language; n counts nonmissing values.

![Pairs the reference accepts and the port accepts](charts/reference-accept-port-accept.png)

Pairs the reference accepts and the port accepts: each dot is one port, the tick is its condition’s median, the faint bar spans its interquartile range, and one panel represents each source language; n counts nonmissing values.

![Pairs the reference accepts and the port crashes on](charts/reference-accept-port-crash.png)

Pairs the reference accepts and the port crashes on: each dot is one port, the tick is its condition’s median, the faint bar spans its interquartile range, and one panel represents each source language; n counts nonmissing values.

![Pairs the reference accepts and the port errors on](charts/reference-accept-port-error.png)

Pairs the reference accepts and the port errors on: each dot is one port, the tick is its condition’s median, the faint bar spans its interquartile range, and one panel represents each source language; n counts nonmissing values.

![Pairs the reference accepts and the port rejects](charts/reference-accept-port-reject.png)

Pairs the reference accepts and the port rejects: each dot is one port, the tick is its condition’s median, the faint bar spans its interquartile range, and one panel represents each source language; n counts nonmissing values.

![Pairs the reference crashes on and the port accepts](charts/reference-crash-port-accept.png)

Pairs the reference crashes on and the port accepts: each dot is one port, the tick is its condition’s median, the faint bar spans its interquartile range, and one panel represents each source language; n counts nonmissing values.

![Pairs the reference crashes on and the port crashes on](charts/reference-crash-port-crash.png)

Pairs the reference crashes on and the port crashes on: each dot is one port, the tick is its condition’s median, the faint bar spans its interquartile range, and one panel represents each source language; n counts nonmissing values.

![Pairs the reference crashes on and the port errors on](charts/reference-crash-port-error.png)

Pairs the reference crashes on and the port errors on: each dot is one port, the tick is its condition’s median, the faint bar spans its interquartile range, and one panel represents each source language; n counts nonmissing values.

![Pairs the reference crashes on and the port rejects](charts/reference-crash-port-reject.png)

Pairs the reference crashes on and the port rejects: each dot is one port, the tick is its condition’s median, the faint bar spans its interquartile range, and one panel represents each source language; n counts nonmissing values.

![Pairs the reference errors on and the port accepts](charts/reference-error-port-accept.png)

Pairs the reference errors on and the port accepts: each dot is one port, the tick is its condition’s median, the faint bar spans its interquartile range, and one panel represents each source language; n counts nonmissing values.

![Pairs the reference errors on and the port crashes on](charts/reference-error-port-crash.png)

Pairs the reference errors on and the port crashes on: each dot is one port, the tick is its condition’s median, the faint bar spans its interquartile range, and one panel represents each source language; n counts nonmissing values.

![Pairs the reference errors on and the port errors on](charts/reference-error-port-error.png)

Pairs the reference errors on and the port errors on: each dot is one port, the tick is its condition’s median, the faint bar spans its interquartile range, and one panel represents each source language; n counts nonmissing values.

![Pairs the reference errors on and the port rejects](charts/reference-error-port-reject.png)

Pairs the reference errors on and the port rejects: each dot is one port, the tick is its condition’s median, the faint bar spans its interquartile range, and one panel represents each source language; n counts nonmissing values.

![Pairs the reference rejects and the port accepts](charts/reference-reject-port-accept.png)

Pairs the reference rejects and the port accepts: each dot is one port, the tick is its condition’s median, the faint bar spans its interquartile range, and one panel represents each source language; n counts nonmissing values.

![Pairs the reference rejects and the port crashes on](charts/reference-reject-port-crash.png)

Pairs the reference rejects and the port crashes on: each dot is one port, the tick is its condition’s median, the faint bar spans its interquartile range, and one panel represents each source language; n counts nonmissing values.

![Pairs the reference rejects and the port errors on](charts/reference-reject-port-error.png)

Pairs the reference rejects and the port errors on: each dot is one port, the tick is its condition’s median, the faint bar spans its interquartile range, and one panel represents each source language; n counts nonmissing values.

![Pairs the reference rejects and the port rejects](charts/reference-reject-port-reject.png)

Pairs the reference rejects and the port rejects: each dot is one port, the tick is its condition’s median, the faint bar spans its interquartile range, and one panel represents each source language; n counts nonmissing values.

Notebook medians [25th, 75th percentiles] by condition; n counts successful ports, and missing values are omitted from each measure.

| Source | Given tests | n | Behaviour agreement (%) |
| --- | --- | --- | --- |
| python | none | 12 | 97.5 [86.7, 97.5] |
| python | unit | 12 | 56.2 [9.64, 56.2] |
| python | source | 12 | 9.64 [9.64, 97.5] |
| python | target | 12 | 97.5 [97.5, 97.5] |
| python | unit + source | 12 | 97.5 [9.64, 97.5] |
| python | unit + target | 12 | 97.5 [97.5, 97.5] |
| python | source + target | 12 | 97.18 [0.0, 97.5] |
| python | all | 12 | 97.5 [97.5, 97.5] |
| javascript | none | 12 | 99.37 [99.37, 99.37] |
| javascript | unit | 12 | 0.0 [0.0, 39.8] |
| javascript | source | 12 | 0.0 [0.0, 39.8] |
| javascript | target | 12 | 99.37 [99.37, 99.37] |
| javascript | unit + source | 12 | 39.8 [39.8, 51.38] |
| javascript | unit + target | 12 | 99.37 [99.37, 99.37] |
| javascript | source + target | 12 | 99.37 [99.37, 99.37] |
| javascript | all | 12 | 99.37 [99.37, 99.37] |

Counts summed over the ports in each condition: each outcome column names reference outcome → port outcome; the denominator is 799 pairs per port.

| Source | Given tests | Ports | accept → accept | accept → reject | accept → error | accept → crash | reject → accept | reject → reject | reject → error | reject → crash | error → accept | error → reject | error → error | error → crash | crash → accept | crash → reject | crash → error | crash → crash |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| python | none | 12 | 3150 | 1050 | 0 | 0 | 180 | 4279 | 5 | 0 | 0 | 0 | 924 | 0 | 0 | 0 | 0 | 0 |
| python | unit | 12 | 700 | 2100 | 1400 | 0 | 40 | 2931 | 1493 | 0 | 0 | 0 | 924 | 0 | 0 | 0 | 0 | 0 |
| python | source | 12 | 1750 | 0 | 2450 | 0 | 100 | 1755 | 2609 | 0 | 0 | 0 | 924 | 0 | 0 | 0 | 0 | 0 |
| python | target | 12 | 3850 | 0 | 0 | 350 | 220 | 3872 | 0 | 372 | 0 | 0 | 847 | 77 | 0 | 0 | 0 | 0 |
| python | unit + source | 12 | 2800 | 0 | 1400 | 0 | 160 | 2816 | 1488 | 0 | 0 | 0 | 924 | 0 | 0 | 0 | 0 | 0 |
| python | unit + target | 12 | 3850 | 0 | 0 | 350 | 220 | 3872 | 0 | 372 | 0 | 0 | 847 | 77 | 0 | 0 | 0 | 0 |
| python | source + target | 12 | 2450 | 0 | 0 | 1750 | 140 | 2459 | 5 | 1860 | 0 | 0 | 539 | 385 | 0 | 0 | 0 | 0 |
| python | all | 12 | 4187 | 13 | 0 | 0 | 233 | 4231 | 0 | 0 | 0 | 0 | 924 | 0 | 0 | 0 | 0 | 0 |
| javascript | none | 12 | 4050 | 20 | 0 | 370 | 0 | 3817 | 0 | 347 | 0 | 55 | 847 | 82 | 0 | 0 | 0 | 0 |
| javascript | unit | 12 | 0 | 0 | 1480 | 2960 | 0 | 964 | 424 | 2776 | 0 | 20 | 308 | 656 | 0 | 0 | 0 | 0 |
| javascript | source | 12 | 0 | 0 | 1480 | 2960 | 0 | 964 | 424 | 2776 | 0 | 20 | 308 | 656 | 0 | 0 | 0 | 0 |
| javascript | target | 12 | 4070 | 0 | 0 | 370 | 0 | 3817 | 0 | 347 | 0 | 55 | 847 | 82 | 0 | 0 | 0 | 0 |
| javascript | unit + source | 12 | 1110 | 0 | 2590 | 740 | 212 | 2516 | 742 | 694 | 0 | 50 | 770 | 164 | 0 | 0 | 0 | 0 |
| javascript | unit + target | 12 | 4440 | 0 | 0 | 0 | 0 | 4164 | 0 | 0 | 0 | 60 | 924 | 0 | 0 | 0 | 0 | 0 |
| javascript | source + target | 12 | 4440 | 0 | 0 | 0 | 0 | 4164 | 0 | 0 | 0 | 60 | 924 | 0 | 0 | 0 | 0 | 0 |
| javascript | all | 12 | 4440 | 0 | 0 | 0 | 0 | 4164 | 0 | 0 | 0 | 60 | 924 | 0 | 0 | 0 | 0 | 0 |

## Does including tests change the port's public interface?

**Why.** Each port and the target-language reference execute 999 held-out API cases over 100 grammars: construction, adding a whole input, and adding up to 16 code points one at a time. A case agrees only when every compared step returns the same rule set or the same error class and position under the comparison rules. A high agreement percentage means more complete matching cases; a low percentage means more cases with a differing step or a crash. The hypothesis is that target integration tests increase agreement by specifying the target interface, with source integration tests providing behavioural constraints. A difference would show agreement on these exercised calls, not completeness of every public API or compatibility for all callers. Matching errors count as agreement. [Measure definition](https://github.com/thekevinscott/ports-research/blob/8999c36b8d8ed765f20682fc54f9799a317750ad/analysis/measure-api/README.md).

![Held-out API agreement with the reference (%)](charts/api-agreement-pct.png)

Held-out API agreement with the reference (%): each dot is one port, the tick is its condition’s median, the faint bar spans its interquartile range, and one panel represents each source language; n counts nonmissing values.

![Cases where either side crashed](charts/api-crash.png)

Cases where either side crashed: each dot is one port, the tick is its condition’s median, the faint bar spans its interquartile range, and one panel represents each source language; n counts nonmissing values.

![Cases where every step matches and one raised](charts/api-error-match.png)

Cases where every step matches and one raised: each dot is one port, the tick is its condition’s median, the faint bar spans its interquartile range, and one panel represents each source language; n counts nonmissing values.

![Cases where the first differing step raised on one side](charts/api-error-mismatch.png)

Cases where the first differing step raised on one side: each dot is one port, the tick is its condition’s median, the faint bar spans its interquartile range, and one panel represents each source language; n counts nonmissing values.

![Cases where every step matches and none raised](charts/api-match.png)

Cases where every step matches and none raised: each dot is one port, the tick is its condition’s median, the faint bar spans its interquartile range, and one panel represents each source language; n counts nonmissing values.

![Cases where the first differing step returned rules on both sides](charts/api-mismatch.png)

Cases where the first differing step returned rules on both sides: each dot is one port, the tick is its condition’s median, the faint bar spans its interquartile range, and one panel represents each source language; n counts nonmissing values.

![Cases the reference crashes on and the port crashes on](charts/api-reference-crash-port-crash.png)

Cases the reference crashes on and the port crashes on: each dot is one port, the tick is its condition’s median, the faint bar spans its interquartile range, and one panel represents each source language; n counts nonmissing values.

![Cases the reference crashes on and the port raises on](charts/api-reference-crash-port-error.png)

Cases the reference crashes on and the port raises on: each dot is one port, the tick is its condition’s median, the faint bar spans its interquartile range, and one panel represents each source language; n counts nonmissing values.

![Cases the reference crashes on and the port runs without raising](charts/api-reference-crash-port-ok.png)

Cases the reference crashes on and the port runs without raising: each dot is one port, the tick is its condition’s median, the faint bar spans its interquartile range, and one panel represents each source language; n counts nonmissing values.

![Cases the reference raises on and the port crashes on](charts/api-reference-error-port-crash.png)

Cases the reference raises on and the port crashes on: each dot is one port, the tick is its condition’s median, the faint bar spans its interquartile range, and one panel represents each source language; n counts nonmissing values.

![Cases the reference raises on and the port raises on](charts/api-reference-error-port-error.png)

Cases the reference raises on and the port raises on: each dot is one port, the tick is its condition’s median, the faint bar spans its interquartile range, and one panel represents each source language; n counts nonmissing values.

![Cases the reference raises on and the port runs without raising](charts/api-reference-error-port-ok.png)

Cases the reference raises on and the port runs without raising: each dot is one port, the tick is its condition’s median, the faint bar spans its interquartile range, and one panel represents each source language; n counts nonmissing values.

![Cases the reference runs without raising and the port crashes on](charts/api-reference-ok-port-crash.png)

Cases the reference runs without raising and the port crashes on: each dot is one port, the tick is its condition’s median, the faint bar spans its interquartile range, and one panel represents each source language; n counts nonmissing values.

![Cases the reference runs without raising and the port raises on](charts/api-reference-ok-port-error.png)

Cases the reference runs without raising and the port raises on: each dot is one port, the tick is its condition’s median, the faint bar spans its interquartile range, and one panel represents each source language; n counts nonmissing values.

![Cases the reference runs without raising and the port runs without raising](charts/api-reference-ok-port-ok.png)

Cases the reference runs without raising and the port runs without raising: each dot is one port, the tick is its condition’s median, the faint bar spans its interquartile range, and one panel represents each source language; n counts nonmissing values.

Notebook medians [25th, 75th percentiles] by condition; n counts successful ports, and missing values are omitted from each measure.

| Source | Given tests | n | API agreement (%) |
| --- | --- | --- | --- |
| python | none | 12 | 87.79 [66.82, 87.79] |
| python | unit | 12 | 10.51 [0.0, 10.51] |
| python | source | 12 | 0.0 [0.0, 87.79] |
| python | target | 12 | 87.79 [87.79, 87.79] |
| python | unit + source | 12 | 87.79 [0.0, 87.79] |
| python | unit + target | 12 | 87.79 [87.79, 88.26] |
| python | source + target | 12 | 86.69 [0.0, 87.79] |
| python | all | 12 | 87.79 [87.79, 88.26] |
| javascript | none | 12 | 94.89 [94.89, 94.89] |
| javascript | unit | 12 | 9.01 [6.76, 9.01] |
| javascript | source | 12 | 0.0 [0.0, 9.01] |
| javascript | target | 12 | 94.89 [94.89, 94.89] |
| javascript | unit + source | 12 | 9.01 [9.01, 9.01] |
| javascript | unit + target | 12 | 94.89 [94.89, 94.89] |
| javascript | source + target | 12 | 94.89 [94.89, 94.89] |
| javascript | all | 12 | 94.89 [94.89, 94.89] |

API outcome counts summed over the ports in each condition, over 999 cases per port: match means all steps agree without errors; error match means all steps agree with at least one error; mismatch and error mismatch name the first unequal step; crash means either side crashed.

| Source | Given tests | Ports | match | mismatch | error match | error mismatch | crash |
| --- | --- | --- | --- | --- | --- | --- | --- |
| python | none | 12 | 3861 | 3201 | 4325 | 601 | 0 |
| python | unit | 12 | 858 | 5330 | 1497 | 4303 | 0 |
| python | source | 12 | 2145 | 335 | 2218 | 7290 | 0 |
| python | target | 12 | 4719 | 737 | 4966 | 567 | 999 |
| python | unit + source | 12 | 3432 | 536 | 3603 | 4417 | 0 |
| python | unit + target | 12 | 4719 | 737 | 4970 | 563 | 999 |
| python | source + target | 12 | 3003 | 469 | 3114 | 407 | 4995 |
| python | all | 12 | 5177 | 739 | 5437 | 635 | 0 |
| javascript | none | 12 | 5349 | 741 | 5047 | 851 | 0 |
| javascript | unit | 12 | 0 | 7794 | 810 | 387 | 2997 |
| javascript | source | 12 | 0 | 3464 | 360 | 172 | 7992 |
| javascript | target | 12 | 5412 | 0 | 5016 | 561 | 999 |
| javascript | unit + source | 12 | 492 | 8660 | 1356 | 481 | 999 |
| javascript | unit + target | 12 | 5904 | 0 | 5472 | 612 | 0 |
| javascript | source + target | 12 | 5904 | 0 | 5472 | 612 | 0 |
| javascript | all | 12 | 5904 | 0 | 5472 | 612 | 0 |

API confusion counts summed over the same cases: each column names reference status → port status; “ok” means no step raised and “error” means at least one step raised.

| Source | Given tests | ok → ok | ok → error | ok → crash | error → ok | error → error | error → crash | crash → ok | crash → error | crash → crash |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| python | none | 5688 | 0 | 0 | 216 | 6084 | 0 | 0 | 0 | 0 |
| python | unit | 3792 | 1896 | 0 | 144 | 6156 | 0 | 0 | 0 | 0 |
| python | source | 2370 | 3318 | 0 | 90 | 6210 | 0 | 0 | 0 | 0 |
| python | target | 5214 | 0 | 474 | 198 | 5577 | 525 | 0 | 0 | 0 |
| python | unit + source | 3792 | 1896 | 0 | 144 | 6156 | 0 | 0 | 0 | 0 |
| python | unit + target | 5214 | 0 | 474 | 198 | 5577 | 525 | 0 | 0 | 0 |
| python | source + target | 3318 | 0 | 2370 | 126 | 3549 | 2625 | 0 | 0 | 0 |
| python | all | 5674 | 14 | 0 | 209 | 6091 | 0 | 0 | 0 | 0 |
| javascript | none | 5493 | 411 | 0 | 0 | 6084 | 0 | 0 | 0 | 0 |
| javascript | unit | 4428 | 0 | 1476 | 0 | 4563 | 1521 | 0 | 0 | 0 |
| javascript | source | 1968 | 0 | 3936 | 0 | 2028 | 4056 | 0 | 0 | 0 |
| javascript | target | 5412 | 0 | 492 | 0 | 5577 | 507 | 0 | 0 | 0 |
| javascript | unit + source | 5412 | 0 | 492 | 0 | 5577 | 507 | 0 | 0 | 0 |
| javascript | unit + target | 5904 | 0 | 0 | 0 | 6084 | 0 | 0 | 0 | 0 |
| javascript | source + target | 5904 | 0 | 0 | 0 | 6084 | 0 | 0 | 0 | 0 |
| javascript | all | 5904 | 0 | 0 | 0 | 6084 | 0 | 0 | 0 | 0 |

## Does including tests change how closely the port mirrors the reference's structure?

**Why.** We compare each port with the hand-written reference in its target language, pairing named functions by normalized name and declared parameter count, comparing their syntax trees, comparing branching distributions, and following resolved package calls from shared public entry points. A high matched fraction means more reference functions have counterparts; a high edge recall means more reference call edges are present. Small normalized tree or trace distances mean more similar shapes or ordered call paths; larger distances mean more changes. A zero port-minus-reference delta means equal counts, not identical code. The hypothesis is that unit tests preserve internal function structure, raising matching and lowering distances, while target integration tests may preserve exported signatures and entry-point paths. Differences measure structural drift, not quality or functional correctness; static name-and-arity call resolution can miss or overmatch calls, and identifiers and literals are abstracted in tree comparison. [Measure definition](https://github.com/thekevinscott/ports-research/blob/8999c36b8d8ed765f20682fc54f9799a317750ad/analysis/measure-ast/README.md); [analysis plan](https://github.com/thekevinscott/ports-research/blob/8999c36b8d8ed765f20682fc54f9799a317750ad/notes/ANALYSIS_PLAN_2026-10-12.md).

![Public API entries only the port exports](charts/ast-api-port-only.png)

Public API entries only the port exports: each dot is one port, the tick is its condition’s median, the faint bar spans its interquartile range, and one panel represents each source language; n counts nonmissing values.

![Public API entries only the reference exports](charts/ast-api-reference-only.png)

Public API entries only the reference exports: each dot is one port, the tick is its condition’s median, the faint bar spans its interquartile range, and one panel represents each source language; n counts nonmissing values.

![Public API entries the port shares with the reference](charts/ast-api-shared.png)

Public API entries the port shares with the reference: each dot is one port, the tick is its condition’s median, the faint bar spans its interquartile range, and one panel represents each source language; n counts nonmissing values.

![Distance between the port's and the reference's branching distributions](charts/ast-branching-wasserstein.png)

Distance between the port's and the reference's branching distributions: each dot is one port, the tick is its condition’s median, the faint bar spans its interquartile range, and one panel represents each source language; n counts nonmissing values.

![Functions, port minus reference](charts/ast-delta-function-count.png)

Functions, port minus reference: each dot is one port, the tick is its condition’s median, the faint bar spans its interquartile range, and one panel represents each source language; n counts nonmissing values.

![Highest cyclomatic complexity, port minus reference](charts/ast-delta-max-cyclomatic.png)

Highest cyclomatic complexity, port minus reference: each dot is one port, the tick is its condition’s median, the faint bar spans its interquartile range, and one panel represents each source language; n counts nonmissing values.

![Deepest AST node, port minus reference](charts/ast-delta-max-depth.png)

Deepest AST node, port minus reference: each dot is one port, the tick is its condition’s median, the faint bar spans its interquartile range, and one panel represents each source language; n counts nonmissing values.

![Longest function in lines, port minus reference](charts/ast-delta-max-function-lines.png)

Longest function in lines, port minus reference: each dot is one port, the tick is its condition’s median, the faint bar spans its interquartile range, and one panel represents each source language; n counts nonmissing values.

![Mean cyclomatic complexity, port minus reference](charts/ast-delta-mean-cyclomatic.png)

Mean cyclomatic complexity, port minus reference: each dot is one port, the tick is its condition’s median, the faint bar spans its interquartile range, and one panel represents each source language; n counts nonmissing values.

![Mean function length in lines, port minus reference](charts/ast-delta-mean-function-lines.png)

Mean function length in lines, port minus reference: each dot is one port, the tick is its condition’s median, the faint bar spans its interquartile range, and one panel represents each source language; n counts nonmissing values.

![AST nodes, port minus reference](charts/ast-delta-node-count.png)

AST nodes, port minus reference: each dot is one port, the tick is its condition’s median, the faint bar spans its interquartile range, and one panel represents each source language; n counts nonmissing values.

![Public entry points traced](charts/ast-entry-point-count.png)

Public entry points traced: each dot is one port, the tick is its condition’s median, the faint bar spans its interquartile range, and one panel represents each source language; n counts nonmissing values.

![Functions paired with a reference function](charts/ast-matched-count.png)

Functions paired with a reference function: each dot is one port, the tick is its condition’s median, the faint bar spans its interquartile range, and one panel represents each source language; n counts nonmissing values.

![Share of the reference's functions the port has a counterpart for](charts/ast-matched-fraction.png)

Share of the reference's functions the port has a counterpart for: each dot is one port, the tick is its condition’s median, the faint bar spans its interquartile range, and one panel represents each source language; n counts nonmissing values.

![Share of the reference's call edges the port also makes, mean over entry points](charts/ast-mean-edge-recall.png)

Share of the reference's call edges the port also makes, mean over entry points: each dot is one port, the tick is its condition’s median, the faint bar spans its interquartile range, and one panel represents each source language; n counts nonmissing values.

![Median length difference of paired functions in lines, port minus reference](charts/ast-median-line-drift.png)

Median length difference of paired functions in lines, port minus reference: each dot is one port, the tick is its condition’s median, the faint bar spans its interquartile range, and one panel represents each source language; n counts nonmissing values.

![Edit distance between the reference's and the port's call traces, median over entry points](charts/ast-median-trace-normalised.png)

Edit distance between the reference's and the port's call traces, median over entry points: each dot is one port, the tick is its condition’s median, the faint bar spans its interquartile range, and one panel represents each source language; n counts nonmissing values.

![Port functions with no reference counterpart](charts/ast-port-only-count.png)

Port functions with no reference counterpart: each dot is one port, the tick is its condition’s median, the faint bar spans its interquartile range, and one panel represents each source language; n counts nonmissing values.

![Share of the port's functions reachable from an entry point](charts/ast-reachable-fraction-port.png)

Share of the port's functions reachable from an entry point: each dot is one port, the tick is its condition’s median, the faint bar spans its interquartile range, and one panel represents each source language; n counts nonmissing values.

![Share of the reference's functions reachable from an entry point](charts/ast-reachable-fraction-reference.png)

Share of the reference's functions reachable from an entry point: each dot is one port, the tick is its condition’s median, the faint bar spans its interquartile range, and one panel represents each source language; n counts nonmissing values.

![Reference functions with no port counterpart](charts/ast-reference-only-count.png)

Reference functions with no port counterpart: each dot is one port, the tick is its condition’s median, the faint bar spans its interquartile range, and one panel represents each source language; n counts nonmissing values.

![Mean tree edit distance between paired functions, normalised](charts/ast-tree-edit-mean.png)

Mean tree edit distance between paired functions, normalised: each dot is one port, the tick is its condition’s median, the faint bar spans its interquartile range, and one panel represents each source language; n counts nonmissing values.

![Median tree edit distance between paired functions, normalised](charts/ast-tree-edit-median.png)

Median tree edit distance between paired functions, normalised: each dot is one port, the tick is its condition’s median, the faint bar spans its interquartile range, and one panel represents each source language; n counts nonmissing values.

![Port functions reachable from no entry point](charts/ast-unreachable-port-only.png)

Port functions reachable from no entry point: each dot is one port, the tick is its condition’s median, the faint bar spans its interquartile range, and one panel represents each source language; n counts nonmissing values.

Notebook medians [25th, 75th percentiles] by condition; n counts successful ports, and missing values are omitted from each measure.

| Source | Given tests | n | Reference functions paired (share) | Paired tree distance | Branching distribution distance |
| --- | --- | --- | --- | --- | --- |
| python | none | 12 | 0.78 [0.77, 0.79] | 0.26 [0.25, 0.28] | 0.27 [0.25, 0.29] |
| python | unit | 12 | 0.79 [0.79, 0.81] | 0.26 [0.25, 0.28] | 0.31 [0.28, 0.34] |
| python | source | 12 | 0.77 [0.77, 0.78] | 0.28 [0.26, 0.3] | 0.27 [0.25, 0.29] |
| python | target | 12 | 0.75 [0.75, 0.78] | 0.26 [0.24, 0.28] | 0.36 [0.35, 0.38] |
| python | unit + source | 12 | 0.81 [0.8, 0.81] | 0.27 [0.26, 0.28] | 0.31 [0.25, 0.34] |
| python | unit + target | 12 | 0.79 [0.78, 0.8] | 0.25 [0.25, 0.27] | 0.31 [0.27, 0.35] |
| python | source + target | 12 | 0.75 [0.75, 0.76] | 0.25 [0.24, 0.26] | 0.39 [0.36, 0.43] |
| python | all | 12 | 0.77 [0.76, 0.8] | 0.25 [0.25, 0.26] | 0.33 [0.31, 0.37] |
| javascript | none | 12 | 0.76 [0.74, 0.77] | 0.35 [0.33, 0.35] | 0.27 [0.22, 0.32] |
| javascript | unit | 12 | 0.75 [0.74, 0.75] | 0.33 [0.29, 0.34] | 0.23 [0.22, 0.25] |
| javascript | source | 12 | 0.73 [0.71, 0.73] | 0.33 [0.32, 0.34] | 0.22 [0.18, 0.23] |
| javascript | target | 12 | 0.66 [0.64, 0.71] | 0.32 [0.29, 0.34] | 0.2 [0.17, 0.24] |
| javascript | unit + source | 12 | 0.75 [0.75, 0.77] | 0.34 [0.3, 0.35] | 0.24 [0.21, 0.28] |
| javascript | unit + target | 12 | 0.78 [0.76, 0.79] | 0.31 [0.3, 0.32] | 0.26 [0.21, 0.29] |
| javascript | source + target | 12 | 0.75 [0.72, 0.76] | 0.31 [0.28, 0.32] | 0.24 [0.22, 0.27] |
| javascript | all | 12 | 0.76 [0.76, 0.79] | 0.3 [0.29, 0.31] | 0.24 [0.22, 0.27] |

Notebook medians [25th, 75th percentiles] by condition; n counts successful ports, and missing values are omitted from each measure.

| Source | Given tests | n | Reference call edges retained (mean share) | Call-trace distance (median) |
| --- | --- | --- | --- | --- |
| python | none | 12 | 0.46 [0.46, 0.48] | 0.36 [0.33, 0.38] |
| python | unit | 12 | 0.47 [0.46, 0.51] | 0.4 [0.39, 0.42] |
| python | source | 12 | 0.46 [0.46, 0.49] | 0.33 [0.33, 0.37] |
| python | target | 12 | 0.47 [0.45, 0.49] | 0.33 [0.33, 0.34] |
| python | unit + source | 12 | 0.47 [0.46, 0.47] | 0.42 [0.4, 0.44] |
| python | unit + target | 12 | 0.47 [0.46, 0.52] | 0.33 [0.33, 0.37] |
| python | source + target | 12 | 0.52 [0.47, 0.55] | 0.33 [0.33, 0.33] |
| python | all | 12 | 0.47 [0.46, 0.52] | 0.34 [0.33, 0.39] |
| javascript | none | 12 | 0.68 [0.67, 0.73] | 0.41 [0.33, 0.5] |
| javascript | unit | 12 | 0.7 [0.67, 0.73] | 0.45 [0.43, 0.48] |
| javascript | source | 12 | 0.72 [0.67, 0.72] | 0.41 [0.39, 0.49] |
| javascript | target | 12 | 0.65 [0.65, 0.7] | 0.25 [0.18, 0.33] |
| javascript | unit + source | 12 | 0.72 [0.66, 0.73] | 0.44 [0.43, 0.48] |
| javascript | unit + target | 12 | 0.74 [0.73, 0.74] | 0.38 [0.33, 0.41] |
| javascript | source + target | 12 | 0.73 [0.67, 0.74] | 0.29 [0.23, 0.33] |
| javascript | all | 12 | 0.73 [0.71, 0.73] | 0.39 [0.37, 0.43] |

## Does including tests change how the agent reads the reference?

**Why.** Mechanical transcript measures count recognized source and test reads, distinct paths read before the first write, rereads, searches per distinct path, and reads after the last write; counts include subagent transcripts. First-read tables distinguish the first read’s file class from whether the first source code file read is the package entry point. High counts mean more recognized reading or revisiting; low counts mean less, and missing means the required event was not observed. The hypothesis is that unit and source integration tests increase source-test reading, target integration tests increase target-test reading, and giving tests increases reading before implementation. A difference would show changed recorded actions, not comprehension, a better strategy, or reads the parser cannot recognize. A recursive directory search counts as one path read. [Measure definition](https://github.com/thekevinscott/ports-research/blob/8999c36b8d8ed765f20682fc54f9799a317750ad/analysis/measure-transcript/README.md).

![Files read before the first write into the port](charts/files-read-before-first-write.png)

Files read before the first write into the port: each dot is one port, the tick is its condition’s median, the faint bar spans its interquartile range, and one panel represents each source language; n counts nonmissing values.

![Most rereads of one file](charts/max-rereads-of-one-file.png)

Most rereads of one file: each dot is one port, the tick is its condition’s median, the faint bar spans its interquartile range, and one panel represents each source language; n counts nonmissing values.

![Reads of the source language's shipped tests](charts/read-source-tests.png)

Reads of the source language's shipped tests: each dot is one port, the tick is its condition’s median, the faint bar spans its interquartile range, and one panel represents each source language; n counts nonmissing values.

![Reads of the source implementation](charts/read-source.png)

Reads of the source implementation: each dot is one port, the tick is its condition’s median, the faint bar spans its interquartile range, and one panel represents each source language; n counts nonmissing values.

![Reads of the target language's shipped tests](charts/read-target-tests.png)

Reads of the target language's shipped tests: each dot is one port, the tick is its condition’s median, the faint bar spans its interquartile range, and one panel represents each source language; n counts nonmissing values.

![Reads after the last write into the port](charts/reads-after-last-write.png)

Reads after the last write into the port: each dot is one port, the tick is its condition’s median, the faint bar spans its interquartile range, and one panel represents each source language; n counts nonmissing values.

![Reads of a file already read](charts/reread-count.png)

Reads of a file already read: each dot is one port, the tick is its condition’s median, the faint bar spans its interquartile range, and one panel represents each source language; n counts nonmissing values.

![Glob and Grep calls per file read](charts/search-calls-per-file-read.png)

Glob and Grep calls per file read: each dot is one port, the tick is its condition’s median, the faint bar spans its interquartile range, and one panel represents each source language; n counts nonmissing values.

![Source files read before the first write into the port](charts/source-files-read-before-first-write.png)

Source files read before the first write into the port: each dot is one port, the tick is its condition’s median, the faint bar spans its interquartile range, and one panel represents each source language; n counts nonmissing values.

Notebook medians [25th, 75th percentiles] by condition; n counts successful ports, and missing values are omitted from each measure.

| Source | Given tests | n | Source-test reads | Target-test reads | Paths read before first write | Rereads |
| --- | --- | --- | --- | --- | --- | --- |
| python | none | 12 | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 40.0 [39.75, 40.0] | 0.0 [0.0, 1.25] |
| python | unit | 12 | 5.0 [3.75, 6.0] | 0.0 [0.0, 0.0] | 61.5 [61.0, 62.25] | 10.5 [7.25, 13.25] |
| python | source | 12 | 3.5 [3.0, 4.0] | 0.0 [0.0, 0.0] | 44.0 [43.0, 44.0] | 7.0 [5.75, 10.25] |
| python | target | 12 | 0.0 [0.0, 0.0] | 4.0 [3.0, 4.0] | 47.0 [46.0, 47.25] | 6.0 [5.5, 7.25] |
| python | unit + source | 12 | 7.0 [6.0, 8.25] | 0.0 [0.0, 0.0] | 67.5 [63.0, 69.0] | 15.0 [10.75, 19.75] |
| python | unit + target | 12 | 9.0 [7.75, 10.5] | 3.0 [2.0, 4.0] | 57.5 [51.5, 72.0] | 39.5 [31.75, 50.25] |
| python | source + target | 12 | 1.0 [0.75, 1.0] | 4.0 [3.0, 5.0] | 47.0 [16.75, 48.25] | 9.0 [7.0, 10.25] |
| python | all | 12 | 9.0 [8.0, 11.0] | 3.5 [3.0, 4.0] | 66.5 [51.75, 70.0] | 40.5 [28.0, 46.25] |
| javascript | none | 12 | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 24.0 [8.0, 38.25] | 0.0 [0.0, 0.25] |
| javascript | unit | 12 | 4.5 [3.0, 6.0] | 0.0 [0.0, 0.0] | 21.0 [10.0, 31.0] | 7.0 [6.0, 11.25] |
| javascript | source | 12 | 4.5 [4.0, 5.0] | 0.0 [0.0, 0.0] | 43.0 [42.0, 44.0] | 10.5 [7.75, 14.25] |
| javascript | target | 12 | 0.0 [0.0, 0.0] | 3.0 [3.0, 4.0] | 41.0 [40.75, 42.25] | 9.5 [6.0, 11.0] |
| javascript | unit + source | 12 | 11.0 [9.75, 14.0] | 0.0 [0.0, 0.0] | 59.5 [52.0, 67.5] | 20.0 [12.0, 41.0] |
| javascript | unit + target | 12 | 9.0 [7.75, 10.25] | 3.5 [3.0, 4.0] | 46.0 [36.5, 54.25] | 29.5 [24.0, 39.5] |
| javascript | source + target | 12 | 2.0 [1.0, 2.0] | 3.0 [3.0, 4.0] | 43.0 [42.5, 44.0] | 9.0 [8.0, 14.5] |
| javascript | all | 12 | 10.5 [9.0, 12.0] | 3.5 [3.0, 4.25] | 50.5 [45.25, 64.5] | 39.5 [29.5, 54.25] |

First-read counts from the notebook, in runs: the first three categories concern the first source code file; the remaining categories concern the first read of any class.

| Source | Given tests | Runs | Entry point first | Other source code first | No source code read | First read: source | First read: source tests | First read: target tests | First read: port | First read: other |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| python | none | 12 | 2 | 10 | 0 | 1 | 0 | 0 | 0 | 11 |
| python | unit | 12 | 1 | 10 | 1 | 10 | 0 | 0 | 0 | 2 |
| python | source | 12 | 7 | 4 | 1 | 12 | 0 | 0 | 0 | 0 |
| python | target | 12 | 5 | 5 | 2 | 0 | 0 | 0 | 0 | 12 |
| python | unit + source | 12 | 1 | 11 | 0 | 6 | 0 | 0 | 0 | 6 |
| python | unit + target | 12 | 4 | 8 | 0 | 0 | 0 | 0 | 0 | 12 |
| python | source + target | 12 | 3 | 5 | 4 | 0 | 0 | 0 | 0 | 12 |
| python | all | 12 | 7 | 4 | 1 | 0 | 0 | 0 | 0 | 12 |
| javascript | none | 12 | 1 | 10 | 1 | 0 | 0 | 0 | 0 | 12 |
| javascript | unit | 12 | 0 | 3 | 9 | 1 | 0 | 0 | 0 | 11 |
| javascript | source | 12 | 2 | 10 | 0 | 0 | 0 | 0 | 0 | 12 |
| javascript | target | 12 | 5 | 5 | 2 | 0 | 0 | 0 | 0 | 12 |
| javascript | unit + source | 12 | 4 | 8 | 0 | 0 | 0 | 0 | 0 | 12 |
| javascript | unit + target | 12 | 2 | 10 | 0 | 2 | 0 | 0 | 0 | 10 |
| javascript | source + target | 12 | 7 | 3 | 2 | 0 | 0 | 0 | 0 | 12 |
| javascript | all | 12 | 5 | 7 | 0 | 1 | 0 | 0 | 0 | 11 |

Runs that touched supplied suites or contained a recognized differential script; “touched” includes reads, writes, edits, searches, shell arguments, and suite execution, so it is broader than reading.

| Source | Given tests | Runs | Touched source tests | Touched target tests | Differential script |
| --- | --- | --- | --- | --- | --- |
| python | none | 12 | 0 | 0 | 6 |
| python | unit | 12 | 12 | 0 | 4 |
| python | source | 12 | 12 | 0 | 5 |
| python | target | 12 | 0 | 12 | 1 |
| python | unit + source | 12 | 12 | 0 | 3 |
| python | unit + target | 12 | 12 | 12 | 4 |
| python | source + target | 12 | 11 | 12 | 1 |
| python | all | 12 | 12 | 12 | 4 |
| javascript | none | 12 | 7 | 0 | 7 |
| javascript | unit | 12 | 12 | 0 | 11 |
| javascript | source | 12 | 12 | 0 | 11 |
| javascript | target | 12 | 0 | 12 | 4 |
| javascript | unit + source | 12 | 12 | 0 | 12 |
| javascript | unit + target | 12 | 12 | 12 | 10 |
| javascript | source + target | 12 | 12 | 12 | 11 |
| javascript | all | 12 | 12 | 12 | 11 |

## Does including tests change how much work the port takes?

**Why.** Per run, we count tokens, assistant turns, tool calls, test-suite executions, newly written test files, and elapsed wall time. The token charts split usage before the first write and from that write onward, counting input, output, cache creation, and cache reads; suite charts count the last observed passed or failed tests when a summary is recognized. High values mean more recorded activity or elapsed time; low values mean less, and missing suite counts mean no usable summary, not zero tests. The hypothesis is that any supplied suite adds reading and test execution, increasing those counts, while target integration tests could reduce revision work, tokens, and elapsed time by clarifying the required interface. Differences would describe resource use and recorded testing, not productivity or port quality; elapsed time also includes waits. The notebook includes model-call counts and wall time in its rank statistics, but does not export separate V2 charts for them.

![Bash calls](charts/bash-calls.png)

Bash calls: each dot is one port, the tick is its condition’s median, the faint bar spans its interquartile range, and one panel represents each source language; n counts nonmissing values.

![Edit calls](charts/edit-calls.png)

Edit calls: each dot is one port, the tick is its condition’s median, the faint bar spans its interquartile range, and one panel represents each source language; n counts nonmissing values.

![Network fetch and install attempts](charts/fetch-attempts.png)

Network fetch and install attempts: each dot is one port, the tick is its condition’s median, the faint bar spans its interquartile range, and one panel represents each source language; n counts nonmissing values.

![Turn of the first write into the port](charts/first-write-turn.png)

Turn of the first write into the port: each dot is one port, the tick is its condition’s median, the faint bar spans its interquartile range, and one panel represents each source language; n counts nonmissing values.

![Failed tests in the last run of the agent's own tests](charts/last-own-tests-failed.png)

Failed tests in the last run of the agent's own tests: each dot is one port, the tick is its condition’s median, the faint bar spans its interquartile range, and one panel represents each source language; n counts nonmissing values.

![Passed tests in the last run of the agent's own tests](charts/last-own-tests-passed.png)

Passed tests in the last run of the agent's own tests: each dot is one port, the tick is its condition’s median, the faint bar spans its interquartile range, and one panel represents each source language; n counts nonmissing values.

![Failed tests in the last run of the source language's shipped tests](charts/last-source-tests-failed.png)

Failed tests in the last run of the source language's shipped tests: each dot is one port, the tick is its condition’s median, the faint bar spans its interquartile range, and one panel represents each source language; n counts nonmissing values.

![Passed tests in the last run of the source language's shipped tests](charts/last-source-tests-passed.png)

Passed tests in the last run of the source language's shipped tests: each dot is one port, the tick is its condition’s median, the faint bar spans its interquartile range, and one panel represents each source language; n counts nonmissing values.

![Turn of the last test suite run](charts/last-suite-run-turn.png)

Turn of the last test suite run: each dot is one port, the tick is its condition’s median, the faint bar spans its interquartile range, and one panel represents each source language; n counts nonmissing values.

![Failed tests in the last run of the target language's shipped tests](charts/last-target-tests-failed.png)

Failed tests in the last run of the target language's shipped tests: each dot is one port, the tick is its condition’s median, the faint bar spans its interquartile range, and one panel represents each source language; n counts nonmissing values.

![Passed tests in the last run of the target language's shipped tests](charts/last-target-tests-passed.png)

Passed tests in the last run of the target language's shipped tests: each dot is one port, the tick is its condition’s median, the faint bar spans its interquartile range, and one panel represents each source language; n counts nonmissing values.

![Failed tests in the last run of a suite of more than one class](charts/last-unknown-failed.png)

Failed tests in the last run of a suite of more than one class: each dot is one port, the tick is its condition’s median, the faint bar spans its interquartile range, and one panel represents each source language; n counts nonmissing values.

![Passed tests in the last run of a suite of more than one class](charts/last-unknown-passed.png)

Passed tests in the last run of a suite of more than one class: each dot is one port, the tick is its condition’s median, the faint bar spans its interquartile range, and one panel represents each source language; n counts nonmissing values.

![Test files the agent wrote itself](charts/own-tests-written.png)

Test files the agent wrote itself: each dot is one port, the tick is its condition’s median, the faint bar spans its interquartile range, and one panel represents each source language; n counts nonmissing values.

![Read calls](charts/read-calls.png)

Read calls: each dot is one port, the tick is its condition’s median, the faint bar spans its interquartile range, and one panel represents each source language; n counts nonmissing values.

![Glob and Grep calls](charts/search-calls.png)

Glob and Grep calls: each dot is one port, the tick is its condition’s median, the faint bar spans its interquartile range, and one panel represents each source language; n counts nonmissing values.

![Test suite runs](charts/suite-run-count.png)

Test suite runs: each dot is one port, the tick is its condition’s median, the faint bar spans its interquartile range, and one panel represents each source language; n counts nonmissing values.

![Tokens from the first write into the port on](charts/tokens-after-first-write.png)

Tokens from the first write into the port on: each dot is one port, the tick is its condition’s median, the faint bar spans its interquartile range, and one panel represents each source language; n counts nonmissing values.

![Tokens before the first write into the port](charts/tokens-before-first-write.png)

Tokens before the first write into the port: each dot is one port, the tick is its condition’s median, the faint bar spans its interquartile range, and one panel represents each source language; n counts nonmissing values.

![Assistant turns](charts/turns.png)

Assistant turns: each dot is one port, the tick is its condition’s median, the faint bar spans its interquartile range, and one panel represents each source language; n counts nonmissing values.

![Write calls](charts/write-calls.png)

Write calls: each dot is one port, the tick is its condition’s median, the faint bar spans its interquartile range, and one panel represents each source language; n counts nonmissing values.

Notebook medians [25th, 75th percentiles] by condition; n counts successful ports, and missing values are omitted from each measure.

| Source | Given tests | n | Total tokens | Suite runs | Own test files |
| --- | --- | --- | --- | --- | --- |
| python | none | 12 | 1112026.5 [1040397.75, 1285314.75] | 4.0 [2.75, 5.25] | 2.0 [1.0, 2.0] |
| python | unit | 12 | 2995979.5 [2734251.75, 3134006.75] | 10.0 [9.0, 11.25] | 24.0 [23.0, 25.0] |
| python | source | 12 | 1360515.5 [1296947.5, 1496816.75] | 4.5 [3.75, 6.0] | 1.0 [0.75, 6.0] |
| python | target | 12 | 1073723.5 [967378.25, 1178212.5] | 4.0 [3.75, 4.0] | 1.0 [0.0, 1.0] |
| python | unit + source | 12 | 3236537.5 [2919203.0, 3585524.25] | 9.0 [7.75, 10.0] | 22.5 [21.75, 23.25] |
| python | unit + target | 12 | 2842488.5 [2792119.25, 2941703.25] | 10.0 [9.0, 11.0] | 22.0 [21.0, 22.25] |
| python | source + target | 12 | 1072875.5 [976667.75, 1190370.25] | 3.0 [2.75, 4.0] | 0.0 [0.0, 1.0] |
| python | all | 12 | 2716913.5 [2565081.5, 2971104.25] | 11.0 [8.0, 12.0] | 22.0 [21.0, 22.0] |
| javascript | none | 12 | 1474019.0 [1417619.0, 1623198.0] | 8.0 [5.75, 10.25] | 1.0 [1.0, 1.25] |
| javascript | unit | 12 | 2457313.5 [2235225.5, 2843651.0] | 4.0 [3.75, 6.5] | 7.0 [6.0, 14.5] |
| javascript | source | 12 | 1595021.5 [1529789.25, 1846382.5] | 3.0 [2.0, 3.75] | 0.5 [0.0, 6.25] |
| javascript | target | 12 | 842847.5 [809326.0, 936980.75] | 3.0 [1.75, 4.0] | 0.0 [0.0, 0.0] |
| javascript | unit + source | 12 | 3287713.0 [2679757.5, 4080672.25] | 7.5 [5.75, 9.5] | 22.0 [11.25, 25.0] |
| javascript | unit + target | 12 | 2869219.5 [2621371.25, 3354633.75] | 10.5 [9.0, 12.25] | 23.0 [23.0, 24.0] |
| javascript | source + target | 12 | 1254455.5 [1188150.0, 1543225.0] | 3.0 [2.75, 4.0] | 1.0 [0.75, 1.0] |
| javascript | all | 12 | 3085734.5 [2993864.0, 3363053.0] | 10.0 [10.0, 11.0] | 23.0 [23.0, 24.0] |

The notebook’s failure and token table below counts all selected attempts; tokens per success divides total recorded tokens across those attempts by successful ports. `api_error` is a recorded terminal reason and is distinct from the exit-1 count above.

| Source | Given tests | Attempts | Exit 0 | Exit 137 | API errors | Tokens per success |
| --- | --- | --- | --- | --- | --- | --- |
| python | none | 16 | 12 | 0 | 4 | 1141352.83 |
| python | unit | 16 | 12 | 0 | 4 | 2904434.75 |
| python | source | 16 | 12 | 0 | 4 | 1385997.33 |
| python | target | 16 | 12 | 0 | 4 | 1092986.75 |
| python | unit + source | 17 | 12 | 0 | 5 | 3303547.25 |
| python | unit + target | 17 | 12 | 0 | 5 | 3105329.83 |
| python | source + target | 16 | 12 | 0 | 4 | 1105363.25 |
| python | all | 16 | 12 | 0 | 4 | 2791548.33 |
| javascript | none | 20 | 12 | 3 | 5 | 1778007.67 |
| javascript | unit | 16 | 12 | 0 | 4 | 2485619.83 |
| javascript | source | 19 | 12 | 3 | 4 | 2068407.75 |
| javascript | target | 16 | 12 | 0 | 4 | 948710.92 |
| javascript | unit + source | 16 | 12 | 0 | 4 | 3405525.92 |
| javascript | unit + target | 16 | 12 | 0 | 4 | 3047596.33 |
| javascript | source + target | 17 | 12 | 1 | 4 | 1568387.33 |
| javascript | all | 17 | 12 | 1 | 4 | 3374072 |

## Does including tests change the port's similarity in embedding space?

**Why.** The intended comparison embeds code files and averages nearest-file distances, weighted by file length, between a port and the reference or another port. Low distance means nearby representations and high distance means separated representations. The hypothesis is that unit and source integration tests constrain implementation choices, lowering distances between ports receiving the same suites; target integration tests may similarly constrain interface code. Such a difference would concern this representation and weighting, not prove behavioural agreement or correctness.

The separate embedding-pair export failed validation: `ValueError: cached file selection differs from source` for the Python reference embedding cache. No V2 embedding chart is emitted by this notebook revision. Its embedding charts and the separate embedding-pair export select V1 runs, so they are not included as measurements of this study. [Export selection](https://github.com/thekevinscott/ports-research/blob/8999c36b8d8ed765f20682fc54f9799a317750ad/analysis/notebook/export_embedding_pairs.py).

## Which differences are larger than chance?

**Why.** For each lead measure, the notebook compares the median with each flag on against its median with that flag off, both pooled and within source language; it also correlates per-run ranks. A large positive gap means a larger on median, a negative gap a smaller one, and a gap near zero similar medians. A small permutation p means few shuffled labels give as large an absolute gap; a wide bootstrap interval means less precise estimation. A rank correlation near +1 or −1 means consistent same-order or reverse-order ranks; near zero means little monotonic association. These screen the directional hypotheses above for each flag, and test whether structural or process measures track held-out agreement. They do not establish a mechanism, validate a proxy as correctness, or establish absence of an effect. This study is exploratory and runs many tests without correction, so these are screening numbers, not confirmations.

Each row sets the runs with the flag on against the runs with it off, pooled over both source languages and then within each. `gap` is the on median minus the off median. `p` is the share of 10,000 shuffles of the on/off labels (seed 0) whose gap is at least as far from zero. `low` to `high` is a 95% bootstrap interval on the gap (10,000 resamples, seed 0). A gap has to be larger than `minimum_detectable_gap` for the same shuffles to give p < 0.05 at this n. A row with p ≥ 0.05 reads as a gap too small to see with this n, never as no effect.

The following per-flag permutation and bootstrap tables retain the notebook’s rows, columns, and rounding; `source_language = pooled` combines both directions.

### Held-out behavior agreement with the reference (%)

| flag | source_language | n_on | n_off | median_on | median_off | gap | low | high | p | minimum_detectable_gap |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| include_unit_tests | pooled | 96 | 96 | 97.5 | 97.5 | 0 | -1.88 | 0 | 1 | 0 |
| include_unit_tests | python | 48 | 48 | 97.5 | 97.5 | 0 | 0 | 0.63 | 1 | 0 |
| include_unit_tests | javascript | 48 | 48 | 99.37 | 99.37 | 0 | -59.57 | 0 | 1 | 1.25 |
| include_source_integration_tests | pooled | 96 | 96 | 97.5 | 97.5 | 0 | -11.39 | 0 | 1 | 0 |
| include_source_integration_tests | python | 48 | 48 | 97.5 | 97.5 | 0 | -0.63 | 0 | 1 | 0 |
| include_source_integration_tests | javascript | 48 | 48 | 99.37 | 99.37 | 0 | -59.57 | 0 | 1 | 1.25 |
| include_target_integration_tests | pooled | 96 | 96 | 97.5 | 39.8 | 57.7 | 28.22 | 59.57 | 0.0001 | 0 |
| include_target_integration_tests | python | 48 | 48 | 97.5 | 76.53 | 20.96 | 0 | 41.3 | 0.0005 | 0 |
| include_target_integration_tests | javascript | 48 | 48 | 99.37 | 39.8 | 59.57 | 59.57 | 99.37 | 0.0033 | 1.25 |

### Held-out API agreement with the reference (%)

| flag | source_language | n_on | n_off | median_on | median_off | gap | low | high | p | minimum_detectable_gap |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| include_unit_tests | pooled | 96 | 96 | 87.79 | 87.79 | 0 | -7.11 | 0 | 1 | 0 |
| include_unit_tests | python | 48 | 48 | 87.79 | 87.79 | 0 | 0 | 2.2 | 1 | 0 |
| include_unit_tests | javascript | 48 | 48 | 94.89 | 94.89 | 0 | -85.89 | 0 | 1 | 5.41 |
| include_source_integration_tests | pooled | 96 | 96 | 87.79 | 87.79 | 0 | -40.49 | 0 | 1 | 0 |
| include_source_integration_tests | python | 48 | 48 | 87.79 | 87.79 | 0 | -2.2 | 0.75 | 1 | 0 |
| include_source_integration_tests | javascript | 48 | 48 | 94.89 | 94.89 | 0 | -85.89 | 0 | 1 | 5.41 |
| include_target_integration_tests | pooled | 96 | 96 | 91.34 | 9.01 | 82.33 | 78.23 | 85.89 | 0.0001 | 0 |
| include_target_integration_tests | python | 48 | 48 | 87.79 | 48.05 | 39.74 | 0 | 77.28 | 0.0005 | 0 |
| include_target_integration_tests | javascript | 48 | 48 | 94.89 | 9.01 | 85.89 | 85.89 | 85.89 | 0.0119 | 5.41 |

### Share of the reference's functions the port has a counterpart for

| flag | source_language | n_on | n_off | median_on | median_off | gap | low | high | p | minimum_detectable_gap |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| include_unit_tests | pooled | 96 | 96 | 0.78 | 0.75 | 0.03 | 0.02 | 0.04 | 0.0001 | 0.01 |
| include_unit_tests | python | 48 | 48 | 0.79 | 0.77 | 0.02 | 0.02 | 0.04 | 0.0334 | 0.01 |
| include_unit_tests | javascript | 48 | 48 | 0.76 | 0.73 | 0.03 | 0.01 | 0.04 | 0.0001 | 0.01 |
| include_source_integration_tests | pooled | 96 | 96 | 0.76 | 0.77 | -0.01 | -0.02 | 0.01 | 0.7745 | 0.01 |
| include_source_integration_tests | python | 48 | 48 | 0.77 | 0.79 | -0.01 | -0.02 | 0 | 0.0796 | 0.01 |
| include_source_integration_tests | javascript | 48 | 48 | 0.75 | 0.75 | -0.01 | -0.02 | 0.01 | 0.6851 | 0.01 |
| include_target_integration_tests | pooled | 96 | 96 | 0.76 | 0.77 | -0.01 | -0.02 | 0.01 | 0.7755 | 0.01 |
| include_target_integration_tests | python | 48 | 48 | 0.77 | 0.79 | -0.02 | -0.03 | 0 | 0.0331 | 0.01 |
| include_target_integration_tests | javascript | 48 | 48 | 0.76 | 0.75 | 0.01 | 0 | 0.02 | 0.0523 | 0.01 |

### Median tree edit distance between paired functions, normalised

| flag | source_language | n_on | n_off | median_on | median_off | gap | low | high | p | minimum_detectable_gap |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| include_unit_tests | pooled | 96 | 96 | 0.28 | 0.29 | -0.01 | -0.03 | 0.01 | 0.1813 | 0.02 |
| include_unit_tests | python | 48 | 48 | 0.26 | 0.26 | 0 | -0.01 | 0.01 | 0.8939 | 0.01 |
| include_unit_tests | javascript | 48 | 48 | 0.31 | 0.33 | -0.02 | -0.04 | 0 | 0.0518 | 0.02 |
| include_source_integration_tests | pooled | 96 | 96 | 0.29 | 0.29 | 0 | -0.02 | 0.01 | 0.6752 | 0.02 |
| include_source_integration_tests | python | 48 | 48 | 0.26 | 0.26 | 0 | -0.01 | 0.01 | 0.8434 | 0.01 |
| include_source_integration_tests | javascript | 48 | 48 | 0.32 | 0.33 | -0.01 | -0.03 | 0 | 0.1397 | 0.02 |
| include_target_integration_tests | pooled | 96 | 96 | 0.28 | 0.3 | -0.01 | -0.04 | 0 | 0.0598 | 0.02 |
| include_target_integration_tests | python | 48 | 48 | 0.25 | 0.27 | -0.02 | -0.02 | -0.01 | 0.0021 | 0.01 |
| include_target_integration_tests | javascript | 48 | 48 | 0.3 | 0.34 | -0.04 | -0.04 | -0.02 | 0.0001 | 0.02 |

### Distance between the port's and the reference's branching distributions

| flag | source_language | n_on | n_off | median_on | median_off | gap | low | high | p | minimum_detectable_gap |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| include_unit_tests | pooled | 96 | 96 | 0.28 | 0.26 | 0.01 | -0.02 | 0.04 | 0.3559 | 0.03 |
| include_unit_tests | python | 48 | 48 | 0.32 | 0.31 | 0.01 | -0.05 | 0.04 | 0.792 | 0.03 |
| include_unit_tests | javascript | 48 | 48 | 0.24 | 0.22 | 0.01 | -0.01 | 0.03 | 0.0854 | 0.02 |
| include_source_integration_tests | pooled | 96 | 96 | 0.27 | 0.27 | -0.01 | -0.04 | 0.02 | 0.7854 | 0.03 |
| include_source_integration_tests | python | 48 | 48 | 0.32 | 0.31 | 0.01 | -0.03 | 0.04 | 0.8617 | 0.03 |
| include_source_integration_tests | javascript | 48 | 48 | 0.23 | 0.23 | 0 | -0.03 | 0.02 | 0.8974 | 0.02 |
| include_target_integration_tests | pooled | 96 | 96 | 0.29 | 0.26 | 0.03 | 0 | 0.07 | 0.0146 | 0.03 |
| include_target_integration_tests | python | 48 | 48 | 0.36 | 0.28 | 0.07 | 0.05 | 0.1 | 0.0001 | 0.03 |
| include_target_integration_tests | javascript | 48 | 48 | 0.23 | 0.23 | 0 | -0.02 | 0.02 | 0.7338 | 0.02 |

### Share of the reference's call edges the port also makes, mean over entry points

| flag | source_language | n_on | n_off | median_on | median_off | gap | low | high | p | minimum_detectable_gap |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| include_unit_tests | pooled | 96 | 96 | 0.61 | 0.57 | 0.04 | -0.11 | 0.11 | 0.6448 | 0.12 |
| include_unit_tests | python | 48 | 48 | 0.47 | 0.47 | 0 | -0.01 | 0 | 1 | 0 |
| include_unit_tests | javascript | 48 | 48 | 0.73 | 0.68 | 0.05 | 0 | 0.06 | 0.0271 | 0.04 |
| include_source_integration_tests | pooled | 96 | 96 | 0.57 | 0.57 | 0 | -0.11 | 0.12 | 0.9988 | 0.12 |
| include_source_integration_tests | python | 48 | 48 | 0.47 | 0.47 | 0 | 0 | 0.01 | 1 | 0 |
| include_source_integration_tests | javascript | 48 | 48 | 0.72 | 0.7 | 0.03 | -0.01 | 0.05 | 0.1251 | 0.04 |
| include_target_integration_tests | pooled | 96 | 96 | 0.57 | 0.57 | 0 | -0.11 | 0.12 | 0.9979 | 0.12 |
| include_target_integration_tests | python | 48 | 48 | 0.47 | 0.47 | 0 | 0 | 0.05 | 1 | 0 |
| include_target_integration_tests | javascript | 48 | 48 | 0.73 | 0.72 | 0.01 | -0.02 | 0.06 | 0.372 | 0.04 |

### Edit distance between the reference's and the port's call traces, median over entry points

| flag | source_language | n_on | n_off | median_on | median_off | gap | low | high | p | minimum_detectable_gap |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| include_unit_tests | pooled | 96 | 96 | 0.4 | 0.33 | 0.07 | 0.06 | 0.09 | 0.0005 | 0.04 |
| include_unit_tests | python | 48 | 48 | 0.4 | 0.33 | 0.06 | 0.03 | 0.08 | 0.0002 | 0.04 |
| include_unit_tests | javascript | 48 | 48 | 0.43 | 0.33 | 0.1 | 0.03 | 0.13 | 0.0001 | 0.04 |
| include_source_integration_tests | pooled | 96 | 96 | 0.38 | 0.37 | 0.01 | -0.03 | 0.05 | 0.5754 | 0.04 |
| include_source_integration_tests | python | 48 | 48 | 0.34 | 0.36 | -0.01 | -0.05 | 0.04 | 0.6858 | 0.04 |
| include_source_integration_tests | javascript | 48 | 48 | 0.4 | 0.39 | 0.01 | -0.02 | 0.08 | 0.3256 | 0.04 |
| include_target_integration_tests | pooled | 96 | 96 | 0.33 | 0.41 | -0.07 | -0.09 | -0.07 | 0.0001 | 0.04 |
| include_target_integration_tests | python | 48 | 48 | 0.33 | 0.39 | -0.06 | -0.07 | -0.04 | 0.0021 | 0.04 |
| include_target_integration_tests | javascript | 48 | 48 | 0.33 | 0.43 | -0.1 | -0.16 | -0.05 | 0.0001 | 0.04 |

### Total tokens

| flag | source_language | n_on | n_off | median_on | median_off | gap | low | high | p | minimum_detectable_gap |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| include_unit_tests | pooled | 96 | 96 | 2944917.5 | 1236706 | 1708211.5 | 1576081 | 1843637.45 | 0.0001 | 884390 |
| include_unit_tests | python | 48 | 48 | 2908043 | 1131662 | 1776381 | 1603192.16 | 1887206 | 0.0001 | 1196819 |
| include_unit_tests | javascript | 48 | 48 | 2995255.5 | 1403736 | 1591519.5 | 1340403.5 | 1853011 | 0.0001 | 859816.5 |
| include_source_integration_tests | pooled | 96 | 96 | 2295962 | 1818696 | 477266 | -615016.3 | 1106226.08 | 0.4838 | 878610.5 |
| include_source_integration_tests | python | 48 | 48 | 1991383 | 1859621 | 131762 | -1150085.82 | 1313721 | 0.9124 | 1196256 |
| include_source_integration_tests | javascript | 48 | 48 | 2512115.5 | 1818696 | 693419.5 | -493707.67 | 1286513 | 0.171 | 861394.5 |
| include_target_integration_tests | pooled | 96 | 96 | 2190526 | 2016821.5 | 173704.5 | -955289 | 843075.12 | 0.8204 | 892343.5 |
| include_target_integration_tests | python | 48 | 48 | 1860776 | 1960712 | -99936 | -1456272.04 | 1079213.22 | 0.9336 | 1200375 |
| include_target_integration_tests | javascript | 48 | 48 | 2296659 | 2016821.5 | 279837.5 | -929054 | 1045305 | 0.6957 | 866518 |

### LOC

| flag | source_language | n_on | n_off | median_on | median_off | gap | low | high | p | minimum_detectable_gap |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| include_unit_tests | pooled | 96 | 96 | 996.5 | 966 | 30.5 | 12 | 63.5 | 0.0012 | 16 |
| include_unit_tests | python | 48 | 48 | 1000 | 967.5 | 32.5 | 10 | 69.01 | 0.0007 | 16.5 |
| include_unit_tests | javascript | 48 | 48 | 994 | 962 | 32 | -13 | 78 | 0.1441 | 40 |
| include_source_integration_tests | pooled | 96 | 96 | 982.5 | 978 | 4.5 | -15 | 21.5 | 0.7108 | 16 |
| include_source_integration_tests | python | 48 | 48 | 983 | 984 | -1 | -20.5 | 18 | 0.8603 | 16.5 |
| include_source_integration_tests | javascript | 48 | 48 | 978 | 971 | 7 | -30.5 | 53 | 0.7613 | 39.5 |
| include_target_integration_tests | pooled | 96 | 96 | 997 | 971 | 26 | 8.5 | 55 | 0.0023 | 16.5 |
| include_target_integration_tests | python | 48 | 48 | 984 | 980 | 4 | -18.5 | 22 | 0.5024 | 16.5 |
| include_target_integration_tests | javascript | 48 | 48 | 1017.5 | 941.5 | 76 | 41 | 102 | 0.0001 | 40 |

### Reads of the source language's shipped tests

| flag | source_language | n_on | n_off | median_on | median_off | gap | low | high | p | minimum_detectable_gap |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| include_unit_tests | pooled | 96 | 96 | 8 | 0 | 8 | 6.5 | 9 | 0.0001 | 2 |
| include_unit_tests | python | 48 | 48 | 7.5 | 0 | 7.5 | 6 | 9 | 0.0001 | 2.5 |
| include_unit_tests | javascript | 48 | 48 | 9 | 0.5 | 8.5 | 6.5 | 10 | 0.0001 | 3 |
| include_source_integration_tests | pooled | 96 | 96 | 5 | 0.5 | 4.5 | 1 | 7 | 0.0001 | 2 |
| include_source_integration_tests | python | 48 | 48 | 4.5 | 1 | 3.5 | -0.5 | 6 | 0.011 | 2.5 |
| include_source_integration_tests | javascript | 48 | 48 | 6.5 | 0.5 | 6 | 1.5 | 9 | 0.0001 | 3 |
| include_target_integration_tests | pooled | 96 | 96 | 3 | 4 | -1 | -3 | 3.5 | 0.3274 | 2 |
| include_target_integration_tests | python | 48 | 48 | 3 | 4 | -1 | -3.5 | 4 | 0.4638 | 2.5 |
| include_target_integration_tests | javascript | 48 | 48 | 3 | 4.5 | -1.5 | -3.5 | 4 | 0.4677 | 3 |

### Reads of the target language's shipped tests

| flag | source_language | n_on | n_off | median_on | median_off | gap | low | high | p | minimum_detectable_gap |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| include_unit_tests | pooled | 96 | 96 | 1 | 1 | 0 | -3 | 3 | 1 | 3 |
| include_unit_tests | python | 48 | 48 | 1 | 1 | 0 | -3 | 2.5 | 1 | 3 |
| include_unit_tests | javascript | 48 | 48 | 1 | 1 | 0 | -3 | 3 | 1 | 3 |
| include_source_integration_tests | pooled | 96 | 96 | 1 | 1 | 0 | -3 | 3 | 1 | 3 |
| include_source_integration_tests | python | 48 | 48 | 1 | 1 | 0 | -3 | 3 | 1 | 3 |
| include_source_integration_tests | javascript | 48 | 48 | 1 | 1 | 0 | -3 | 3 | 1 | 3 |
| include_target_integration_tests | pooled | 96 | 96 | 3 | 0 | 3 | 3 | 4 | 0.1096 | 3 |
| include_target_integration_tests | python | 48 | 48 | 4 | 0 | 4 | 3 | 4 | 0.0001 | 3 |
| include_target_integration_tests | javascript | 48 | 48 | 3 | 0 | 3 | 3 | 4 | 0.3095 | 3 |

### Test suite runs

| flag | source_language | n_on | n_off | median_on | median_off | gap | low | high | p | minimum_detectable_gap |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| include_unit_tests | pooled | 96 | 96 | 9.5 | 4 | 5.5 | 5 | 7 | 0.0001 | 2 |
| include_unit_tests | python | 48 | 48 | 10 | 4 | 6 | 5 | 7 | 0.0001 | 3 |
| include_unit_tests | javascript | 48 | 48 | 9 | 3 | 6 | 4 | 7 | 0.0001 | 2.5 |
| include_source_integration_tests | pooled | 96 | 96 | 6 | 6 | 0 | -3 | 2 | 1 | 2 |
| include_source_integration_tests | python | 48 | 48 | 6 | 6.5 | -0.5 | -3.5 | 2.5 | 1 | 3 |
| include_source_integration_tests | javascript | 48 | 48 | 5.5 | 6 | -0.5 | -3.5 | 2.5 | 0.9954 | 2.5 |
| include_target_integration_tests | pooled | 96 | 96 | 7 | 6 | 1 | -2 | 3 | 0.3534 | 2 |
| include_target_integration_tests | python | 48 | 48 | 7 | 6 | 1 | -4 | 3 | 0.7134 | 3 |
| include_target_integration_tests | javascript | 48 | 48 | 6 | 6 | 0 | -2.5 | 4 | 1 | 2.5 |

### Test files the agent wrote itself

| flag | source_language | n_on | n_off | median_on | median_off | gap | low | high | p | minimum_detectable_gap |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| include_unit_tests | pooled | 96 | 96 | 22.5 | 1 | 21.5 | 21 | 22 | 0.0001 | 9 |
| include_unit_tests | python | 48 | 48 | 22 | 1 | 21 | 21 | 22 | 0.0002 | 19 |
| include_unit_tests | javascript | 48 | 48 | 23 | 1 | 22 | 21 | 23 | 0.0001 | 6 |
| include_source_integration_tests | pooled | 96 | 96 | 7 | 4.5 | 2.5 | -5 | 19 | 0.2933 | 9 |
| include_source_integration_tests | python | 48 | 48 | 14 | 12 | 2 | -19 | 19 | 0.8378 | 19 |
| include_source_integration_tests | javascript | 48 | 48 | 7 | 4 | 3 | -3.5 | 19.5 | 0.3659 | 6 |
| include_target_integration_tests | pooled | 96 | 96 | 4.5 | 6 | -1.5 | -6 | 16 | 0.4865 | 9.5 |
| include_target_integration_tests | python | 48 | 48 | 11 | 13.5 | -2.5 | -21 | 17 | 0.8437 | 19 |
| include_target_integration_tests | javascript | 48 | 48 | 4.5 | 6 | -1.5 | -6 | 18.5 | 0.6399 | 6 |

### Files read before the first write into the port

| flag | source_language | n_on | n_off | median_on | median_off | gap | low | high | p | minimum_detectable_gap |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| include_unit_tests | pooled | 96 | 96 | 55 | 42.5 | 12.5 | 8.5 | 20 | 0.0001 | 2.5 |
| include_unit_tests | python | 48 | 48 | 62.5 | 44 | 18.5 | 16 | 24 | 0.0001 | 5 |
| include_unit_tests | javascript | 48 | 48 | 46 | 41 | 5 | -4 | 11 | 0.0012 | 3 |
| include_source_integration_tests | pooled | 96 | 96 | 46 | 41 | 5 | 0 | 9 | 0.0008 | 2.5 |
| include_source_integration_tests | python | 48 | 48 | 48.5 | 48.5 | 0 | -8 | 5.5 | 1 | 5 |
| include_source_integration_tests | javascript | 48 | 48 | 44 | 38 | 6 | 3 | 21 | 0.0002 | 3 |
| include_target_integration_tests | pooled | 96 | 96 | 47 | 43 | 4 | 1.5 | 6.5 | 0.0079 | 2.5 |
| include_target_integration_tests | python | 48 | 48 | 49 | 45 | 4 | -12.5 | 7.5 | 0.2695 | 5 |
| include_target_integration_tests | javascript | 48 | 48 | 44 | 39.5 | 4.5 | 0.5 | 12 | 0.0016 | 3 |

### Reads of a file already read

| flag | source_language | n_on | n_off | median_on | median_off | gap | low | high | p | minimum_detectable_gap |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| include_unit_tests | pooled | 96 | 96 | 24.5 | 7 | 17.5 | 11 | 24 | 0.0001 | 3.5 |
| include_unit_tests | python | 48 | 48 | 24.5 | 6 | 18.5 | 10 | 27 | 0.0001 | 5 |
| include_unit_tests | javascript | 48 | 48 | 24.5 | 8 | 16.5 | 7.5 | 22.5 | 0.0001 | 4.5 |
| include_source_integration_tests | pooled | 96 | 96 | 14 | 8 | 6 | 3 | 10 | 0.0006 | 3.5 |
| include_source_integration_tests | python | 48 | 48 | 13.5 | 7.5 | 6 | 0.5 | 10 | 0.023 | 5 |
| include_source_integration_tests | javascript | 48 | 48 | 16 | 9.5 | 6.5 | 2 | 16 | 0.0083 | 4.5 |
| include_target_integration_tests | pooled | 96 | 96 | 17 | 9 | 8 | 3 | 17.5 | 0.0001 | 3.5 |
| include_target_integration_tests | python | 48 | 48 | 16 | 8.5 | 7.5 | -1 | 22.5 | 0.003 | 5 |
| include_target_integration_tests | javascript | 48 | 48 | 17 | 10 | 7 | 1 | 18 | 0.0044 | 4.5 |

### Rank correlation with held-out behaviour

The notebook’s Spearman table correlates each listed measure with held-out behaviour agreement over paired nonmissing runs; n is the number of such pairs, and coefficients retain the notebook’s three-decimal rounding.

| Measure | Spearman ρ | n |
| --- | --- | --- |
| api_agreement_pct | 0.977 | 192 |
| reference_accept_port_accept | 0.959 | 192 |
| reference_error_port_error | 0.622 | 192 |
| reference_accept_port_crash | -0.621 | 192 |
| reference_reject_port_crash | -0.621 | 192 |
| reference_error_port_crash | -0.621 | 192 |
| reference_error_port_reject | 0.617 | 192 |
| read_target_tests | 0.458 | 192 |
| reference_reject_port_error | -0.447 | 192 |
| reference_reject_port_reject | 0.442 | 192 |
| reference_accept_port_error | -0.427 | 192 |
| loc | 0.403 | 192 |
| ast_median_trace_normalised | -0.316 | 192 |
| ast_mean_edge_recall | 0.303 | 192 |
| duration_ms | -0.292 | 192 |
| suite_run_count | 0.153 | 192 |
| reference_accept_port_reject | -0.152 | 192 |
| ast_tree_edit_median | 0.132 | 192 |
| reread_count | 0.108 | 192 |
| read_source_tests | -0.087 | 192 |
| api_calls | 0.081 | 192 |
| file_count | -0.078 | 192 |
| reference_reject_port_accept | 0.058 | 192 |
| total_tokens | -0.048 | 192 |
| own_tests_written | 0.028 | 192 |
| files_read_before_first_write | -0.026 | 192 |
| ast_branching_wasserstein | 0 | 192 |
| ast_matched_fraction | 0 | 192 |

![How per-run measures rank against each other on V2 runs (Spearman)](charts/spearman-matrix.png)

Each square plots the Spearman rank correlation between two per-run measures across the successful ports, with color and a printed coefficient from −1 to +1.

Reference diff similarity and test pass rates are not measured on V2 runs: `measure-code-distance` takes no javascript target and `execute-test-suite` finds no V2 suite in the derivation cache.

## Does a judge see a difference?

**Why.** The code rubric judges API parity, structure, semantic divergences, idiom, and an ordinal fidelity score; the transcript rubric judges cheating, structure decisions, and reading strategy. Higher fidelity scores would mean greater rubric-rated fidelity, while lower scores would mean less. The hypothesis is that source integration tests improve judged semantic parity, unit tests preserve judged structure, and target integration tests improve judged API parity. A difference would show what these judges rate under the rubrics, not establish correctness or agreement with human review; the human reference pair is judged blind as a baseline. [Rubric design](https://github.com/thekevinscott/ports-research/blob/8999c36b8d8ed765f20682fc54f9799a317750ad/notes/ANALYSIS_PLAN_2026-10-12.md).

In progress; both rubrics are being judged, results will be added here: the code rubric and the transcript rubric.

## Do LLM walkthroughs of the port cover the reference's?

**Why.** Independent LLM walkthroughs describe each implementation’s public entry points, happy paths, error paths, and invariants; embedding alignment then counts the share of reference steps matched, their order agreement, and extra port steps. High coverage would mean more reference explanation steps have aligned port steps; low coverage would mean fewer. The hypothesis is that source integration tests increase coverage of behavioural and error paths, while target integration tests increase coverage of public interface steps. A difference would show agreement between generated explanations and their alignment, not prove code equivalence; repeated-reference and cross-language-reference comparisons provide comparison lines for explanation variability. [Walkthrough design](https://github.com/thekevinscott/ports-research/blob/8999c36b8d8ed765f20682fc54f9799a317750ad/notes/ANALYSIS_PLAN_2026-10-12.md).

In progress; port and reference walkthroughs are being generated and compared, results will be added here.

## What this report does not do.

No conclusions are drawn here; results are reviewed with Kevin. The [methodology review](https://github.com/thekevinscott/ports-research/blob/methodology-review/notes/REVIEW_2026-10-12-methodology.md) records the measurement limits; [PR #153](https://github.com/thekevinscott/ports-research/pull/153) is open at report generation.

## How this was made.

Every chart is a direct export of the [analysis notebook](https://github.com/thekevinscott/ports-research/blob/8999c36b8d8ed765f20682fc54f9799a317750ad/analysis/notebook/runs.py) at commit `8999c36b8d8ed765f20682fc54f9799a317750ad`. The embedding server is `qwen3-embedding-0.6b-q8_0`, last-token pooling, llama.cpp on tower (`http://100.124.147.77:8180/v1`). The [notebook README](https://github.com/thekevinscott/ports-research/blob/8999c36b8d8ed765f20682fc54f9799a317750ad/analysis/notebook/README.md) describes both exports.

`PORTS_RUNS_DIR` selects an input directory containing the five matrices’ run directories plus the V1 inputs required by the unchanged exporter. The report copies only V2 PNGs. The input directories use hardlinked files; no port or transcript was inspected for this report. The initial directory-symlink selection was skipped by the scanner and failed in the notebook’s first cell with `ColumnNotFoundError: "include_python_tests" not found`; the directory selection was corrected without editing the notebook.

```sh
GENERATE_EMBEDDING_BASE_URL=http://100.124.147.77:8180/v1 UV_NO_CONFIG=1 uv run --directory analysis/notebook python export_charts.py
UV_NO_CONFIG=1 uv run --directory analysis/notebook python export_embedding_pairs.py
```

This report includes 87 light PNG charts; their combined size is below 20 MB, with no downscaling. Summary medians and quartiles, first-read and touched-test counts, failure/token tables, flag comparisons, and Spearman coefficients come from the notebook’s own table functions; confusion counts sum the notebook’s per-run counts by condition.
