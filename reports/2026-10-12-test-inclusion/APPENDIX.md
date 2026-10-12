# Appendix: How including tests changes an LLM's port

2026-10-12. Every chart and table behind the [report](README.md) that the report itself does not show. Charts read as in the report: one dot per port, a tick at the median, a faint bar over the middle half of the ports, one panel per direction.

## Held-out behaviour

The agent never saw these 100 grammars and 799 grammar–input pairs. Each pair runs through the port and through the reference in the target language. Each side ends in accept, reject, error or crash. Agreement is the share of pairs where both sides end the same way.

Near 100% means the port acts like the reference on these inputs, errors included. Lower means it accepts, rejects, errors or crashes where the reference does not. The pairs reach the port through a driver that expects the reference's names, file layout and end-of-input state, so a port without them fails every pair (see the report's interface section).

The hypothesis was that source and target integration tests would raise agreement by showing behaviour by example. A difference shows the tests changed behaviour on this corpus. It does not show correctness on other inputs, or that the reference is right. It matters because it is the direct check of whether the port does what the original does. [Measure definition](https://github.com/thekevinscott/ports-research/blob/3e610fb80bcc3d51cb93142c5b732e2c08fad64b/analysis/measure-behavior/README.md).

![Pairs the reference accepts and the port accepts](charts/reference-accept-port-accept.png)

Count of the 799 pairs on which the reference accepts the input and the port accepts it.

![Pairs the reference accepts and the port crashes on](charts/reference-accept-port-crash.png)

Count of the 799 pairs on which the reference accepts the input and the port crashes on it.

![Pairs the reference accepts and the port errors on](charts/reference-accept-port-error.png)

Count of the 799 pairs on which the reference accepts the input and the port raises an error on it.

![Pairs the reference accepts and the port rejects](charts/reference-accept-port-reject.png)

Count of the 799 pairs on which the reference accepts the input and the port rejects it.

![Pairs the reference crashes on and the port accepts](charts/reference-crash-port-accept.png)

Count of the 799 pairs on which the reference crashes on the input and the port accepts it.

![Pairs the reference crashes on and the port crashes on](charts/reference-crash-port-crash.png)

Count of the 799 pairs on which the reference crashes on the input and the port crashes on it.

![Pairs the reference crashes on and the port errors on](charts/reference-crash-port-error.png)

Count of the 799 pairs on which the reference crashes on the input and the port raises an error on it.

![Pairs the reference crashes on and the port rejects](charts/reference-crash-port-reject.png)

Count of the 799 pairs on which the reference crashes on the input and the port rejects it.

![Pairs the reference errors on and the port accepts](charts/reference-error-port-accept.png)

Count of the 799 pairs on which the reference raises an error on the input and the port accepts it.

![Pairs the reference errors on and the port crashes on](charts/reference-error-port-crash.png)

Count of the 799 pairs on which the reference raises an error on the input and the port crashes on it.

![Pairs the reference errors on and the port errors on](charts/reference-error-port-error.png)

Count of the 799 pairs on which the reference raises an error on the input and the port raises an error on it.

![Pairs the reference errors on and the port rejects](charts/reference-error-port-reject.png)

Count of the 799 pairs on which the reference raises an error on the input and the port rejects it.

![Pairs the reference rejects and the port accepts](charts/reference-reject-port-accept.png)

Count of the 799 pairs on which the reference rejects the input and the port accepts it.

![Pairs the reference rejects and the port crashes on](charts/reference-reject-port-crash.png)

Count of the 799 pairs on which the reference rejects the input and the port crashes on it.

![Pairs the reference rejects and the port errors on](charts/reference-reject-port-error.png)

Count of the 799 pairs on which the reference rejects the input and the port raises an error on it.

![Pairs the reference rejects and the port rejects](charts/reference-reject-port-reject.png)

Count of the 799 pairs on which the reference rejects the input and the port rejects it.

Median [25th, 75th percentile] per condition, from the notebook; n counts successful ports.

| Direction | Given tests | n | Behaviour agreement (%) |
| --- | --- | --- | --- |
| python → javascript | none | 12 | 97.5 [86.7, 97.5] |
| python → javascript | unit | 12 | 56.2 [9.64, 56.2] |
| python → javascript | source | 12 | 9.64 [9.64, 97.5] |
| python → javascript | target | 12 | 97.5 [97.5, 97.5] |
| python → javascript | unit + source | 12 | 97.5 [9.64, 97.5] |
| python → javascript | unit + target | 12 | 97.5 [97.5, 97.5] |
| python → javascript | source + target | 12 | 97.18 [0.0, 97.5] |
| python → javascript | all | 12 | 97.5 [97.5, 97.5] |
| javascript → python | none | 12 | 99.37 [99.37, 99.37] |
| javascript → python | unit | 12 | 0.0 [0.0, 39.8] |
| javascript → python | source | 12 | 0.0 [0.0, 39.8] |
| javascript → python | target | 12 | 99.37 [99.37, 99.37] |
| javascript → python | unit + source | 12 | 39.8 [39.8, 51.38] |
| javascript → python | unit + target | 12 | 99.37 [99.37, 99.37] |
| javascript → python | source + target | 12 | 99.37 [99.37, 99.37] |
| javascript → python | all | 12 | 99.37 [99.37, 99.37] |

Pairs summed over each condition's ports (12 × 799 = 9,588); each column is reference outcome → port outcome.

| Direction | Given tests | Ports | accept → accept | accept → reject | accept → error | accept → crash | reject → accept | reject → reject | reject → error | reject → crash | error → accept | error → reject | error → error | error → crash | crash → accept | crash → reject | crash → error | crash → crash |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| python → javascript | none | 12 | 3150 | 1050 | 0 | 0 | 180 | 4279 | 5 | 0 | 0 | 0 | 924 | 0 | 0 | 0 | 0 | 0 |
| python → javascript | unit | 12 | 700 | 2100 | 1400 | 0 | 40 | 2931 | 1493 | 0 | 0 | 0 | 924 | 0 | 0 | 0 | 0 | 0 |
| python → javascript | source | 12 | 1750 | 0 | 2450 | 0 | 100 | 1755 | 2609 | 0 | 0 | 0 | 924 | 0 | 0 | 0 | 0 | 0 |
| python → javascript | target | 12 | 3850 | 0 | 0 | 350 | 220 | 3872 | 0 | 372 | 0 | 0 | 847 | 77 | 0 | 0 | 0 | 0 |
| python → javascript | unit + source | 12 | 2800 | 0 | 1400 | 0 | 160 | 2816 | 1488 | 0 | 0 | 0 | 924 | 0 | 0 | 0 | 0 | 0 |
| python → javascript | unit + target | 12 | 3850 | 0 | 0 | 350 | 220 | 3872 | 0 | 372 | 0 | 0 | 847 | 77 | 0 | 0 | 0 | 0 |
| python → javascript | source + target | 12 | 2450 | 0 | 0 | 1750 | 140 | 2459 | 5 | 1860 | 0 | 0 | 539 | 385 | 0 | 0 | 0 | 0 |
| python → javascript | all | 12 | 4187 | 13 | 0 | 0 | 233 | 4231 | 0 | 0 | 0 | 0 | 924 | 0 | 0 | 0 | 0 | 0 |
| javascript → python | none | 12 | 4050 | 20 | 0 | 370 | 0 | 3817 | 0 | 347 | 0 | 55 | 847 | 82 | 0 | 0 | 0 | 0 |
| javascript → python | unit | 12 | 0 | 0 | 1480 | 2960 | 0 | 964 | 424 | 2776 | 0 | 20 | 308 | 656 | 0 | 0 | 0 | 0 |
| javascript → python | source | 12 | 0 | 0 | 1480 | 2960 | 0 | 964 | 424 | 2776 | 0 | 20 | 308 | 656 | 0 | 0 | 0 | 0 |
| javascript → python | target | 12 | 4070 | 0 | 0 | 370 | 0 | 3817 | 0 | 347 | 0 | 55 | 847 | 82 | 0 | 0 | 0 | 0 |
| javascript → python | unit + source | 12 | 1110 | 0 | 2590 | 740 | 212 | 2516 | 742 | 694 | 0 | 50 | 770 | 164 | 0 | 0 | 0 | 0 |
| javascript → python | unit + target | 12 | 4440 | 0 | 0 | 0 | 0 | 4164 | 0 | 0 | 0 | 60 | 924 | 0 | 0 | 0 | 0 | 0 |
| javascript → python | source + target | 12 | 4440 | 0 | 0 | 0 | 0 | 4164 | 0 | 0 | 0 | 60 | 924 | 0 | 0 | 0 | 0 | 0 |
| javascript → python | all | 12 | 4440 | 0 | 0 | 0 | 0 | 4164 | 0 | 0 | 0 | 60 | 924 | 0 | 0 | 0 | 0 | 0 |

## Held-out API

999 short call sequences over the same 100 grammars: build the grammar, add a whole input, then add up to 16 characters one at a time. A case agrees when every step returns the same set of next rules as the reference, or raises the same error class at the same position. Agreement is the share of the 999 cases.

High means a caller gets the same answers from the port as from the reference. The cases reach the port through the same kind of driver as the behaviour measure.

The hypothesis was that target integration tests would raise agreement by spelling out the interface. A difference shows the tests changed the answers on these calls. It does not show that the whole public API matches. It matters because a port with the right behaviour behind a different interface is not a drop-in replacement. [Measure definition](https://github.com/thekevinscott/ports-research/blob/3e610fb80bcc3d51cb93142c5b732e2c08fad64b/analysis/measure-api/README.md).

![Cases where either side crashed](charts/api-crash.png)

Count of cases where the port or the reference crashes (10 s timeout, non-zero exit, or no output).

![Cases where every step matches with an error](charts/api-error-match.png)

Count of cases where every step matches and at least one step raises the same error on both sides.

![Cases whose first differing step raised an error](charts/api-error-mismatch.png)

Count of cases whose first unequal step raises on at least one side, or is missing on one side.

![Cases where every step matches with no error](charts/api-match.png)

Count of the 999 cases where every step returns the same rules on both sides and none raises.

![Cases whose first differing step returned different rules](charts/api-mismatch.png)

Count of cases whose first unequal step returns rules on both sides, but different ones.

![Cases where the reference crashes and the port crashes](charts/api-reference-crash-port-crash.png)

Count of the 999 cases where the reference crashes and the port crashes.

![Cases where the reference crashes and the port raises an error](charts/api-reference-crash-port-error.png)

Count of the 999 cases where the reference crashes and the port raises an error.

![Cases where the reference crashes and the port runs without error](charts/api-reference-crash-port-ok.png)

Count of the 999 cases where the reference crashes and the port runs without error.

![Cases where the reference raises an error and the port crashes](charts/api-reference-error-port-crash.png)

Count of the 999 cases where the reference raises an error and the port crashes.

![Cases where the reference raises an error and the port raises an error](charts/api-reference-error-port-error.png)

Count of the 999 cases where the reference raises an error and the port raises an error.

![Cases where the reference raises an error and the port runs without error](charts/api-reference-error-port-ok.png)

Count of the 999 cases where the reference raises an error and the port runs without error.

![Cases where the reference runs without error and the port crashes](charts/api-reference-ok-port-crash.png)

Count of the 999 cases where the reference runs without error and the port crashes.

![Cases where the reference runs without error and the port raises an error](charts/api-reference-ok-port-error.png)

Count of the 999 cases where the reference runs without error and the port raises an error.

![Cases where the reference runs without error and the port runs without error](charts/api-reference-ok-port-ok.png)

Count of the 999 cases where the reference runs without error and the port runs without error.

Median [25th, 75th percentile] per condition, from the notebook; n counts successful ports.

| Direction | Given tests | n | API agreement (%) |
| --- | --- | --- | --- |
| python → javascript | none | 12 | 87.79 [66.82, 87.79] |
| python → javascript | unit | 12 | 10.51 [0.0, 10.51] |
| python → javascript | source | 12 | 0.0 [0.0, 87.79] |
| python → javascript | target | 12 | 87.79 [87.79, 87.79] |
| python → javascript | unit + source | 12 | 87.79 [0.0, 87.79] |
| python → javascript | unit + target | 12 | 87.79 [87.79, 88.26] |
| python → javascript | source + target | 12 | 86.69 [0.0, 87.79] |
| python → javascript | all | 12 | 87.79 [87.79, 88.26] |
| javascript → python | none | 12 | 94.89 [94.89, 94.89] |
| javascript → python | unit | 12 | 9.01 [6.76, 9.01] |
| javascript → python | source | 12 | 0.0 [0.0, 9.01] |
| javascript → python | target | 12 | 94.89 [94.89, 94.89] |
| javascript → python | unit + source | 12 | 9.01 [9.01, 9.01] |
| javascript → python | unit + target | 12 | 94.89 [94.89, 94.89] |
| javascript → python | source + target | 12 | 94.89 [94.89, 94.89] |
| javascript → python | all | 12 | 94.89 [94.89, 94.89] |

API cases summed over each condition's ports (12 × 999 = 11,988), by outcome as in the charts above.

| Direction | Given tests | Ports | match | mismatch | error match | error mismatch | crash |
| --- | --- | --- | --- | --- | --- | --- | --- |
| python → javascript | none | 12 | 3861 | 3201 | 4325 | 601 | 0 |
| python → javascript | unit | 12 | 858 | 5330 | 1497 | 4303 | 0 |
| python → javascript | source | 12 | 2145 | 335 | 2218 | 7290 | 0 |
| python → javascript | target | 12 | 4719 | 737 | 4966 | 567 | 999 |
| python → javascript | unit + source | 12 | 3432 | 536 | 3603 | 4417 | 0 |
| python → javascript | unit + target | 12 | 4719 | 737 | 4970 | 563 | 999 |
| python → javascript | source + target | 12 | 3003 | 469 | 3114 | 407 | 4995 |
| python → javascript | all | 12 | 5177 | 739 | 5437 | 635 | 0 |
| javascript → python | none | 12 | 5349 | 741 | 5047 | 851 | 0 |
| javascript → python | unit | 12 | 0 | 7794 | 810 | 387 | 2997 |
| javascript → python | source | 12 | 0 | 3464 | 360 | 172 | 7992 |
| javascript → python | target | 12 | 5412 | 0 | 5016 | 561 | 999 |
| javascript → python | unit + source | 12 | 492 | 8660 | 1356 | 481 | 999 |
| javascript → python | unit + target | 12 | 5904 | 0 | 5472 | 612 | 0 |
| javascript → python | source + target | 12 | 5904 | 0 | 5472 | 612 | 0 |
| javascript → python | all | 12 | 5904 | 0 | 5472 | 612 | 0 |

API cases summed over the same ports, by reference status → port status: “ok” no step raised, “error” at least one step raised.

| Direction | Given tests | ok → ok | ok → error | ok → crash | error → ok | error → error | error → crash | crash → ok | crash → error | crash → crash |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| python → javascript | none | 5688 | 0 | 0 | 216 | 6084 | 0 | 0 | 0 | 0 |
| python → javascript | unit | 3792 | 1896 | 0 | 144 | 6156 | 0 | 0 | 0 | 0 |
| python → javascript | source | 2370 | 3318 | 0 | 90 | 6210 | 0 | 0 | 0 | 0 |
| python → javascript | target | 5214 | 0 | 474 | 198 | 5577 | 525 | 0 | 0 | 0 |
| python → javascript | unit + source | 3792 | 1896 | 0 | 144 | 6156 | 0 | 0 | 0 | 0 |
| python → javascript | unit + target | 5214 | 0 | 474 | 198 | 5577 | 525 | 0 | 0 | 0 |
| python → javascript | source + target | 3318 | 0 | 2370 | 126 | 3549 | 2625 | 0 | 0 | 0 |
| python → javascript | all | 5674 | 14 | 0 | 209 | 6091 | 0 | 0 | 0 | 0 |
| javascript → python | none | 5493 | 411 | 0 | 0 | 6084 | 0 | 0 | 0 | 0 |
| javascript → python | unit | 4428 | 0 | 1476 | 0 | 4563 | 1521 | 0 | 0 | 0 |
| javascript → python | source | 1968 | 0 | 3936 | 0 | 2028 | 4056 | 0 | 0 | 0 |
| javascript → python | target | 5412 | 0 | 492 | 0 | 5577 | 507 | 0 | 0 | 0 |
| javascript → python | unit + source | 5412 | 0 | 492 | 0 | 5577 | 507 | 0 | 0 | 0 |
| javascript → python | unit + target | 5904 | 0 | 0 | 0 | 6084 | 0 | 0 | 0 | 0 |
| javascript → python | source + target | 5904 | 0 | 0 | 0 | 6084 | 0 | 0 | 0 | 0 |
| javascript → python | all | 5904 | 0 | 0 | 0 | 6084 | 0 | 0 | 0 | 0 |

## Work

Counted per run, from the transcript: tokens before and after the first write into the port; assistant turns; calls per tool; network fetch or install attempts; the turn of the first write and of the last test run; test-suite runs; test files the agent wrote itself; passed and failed counts from the last run of each suite.

More means more activity. No dot means the event did not happen or no test summary was readable, not zero tests.

The hypothesis was that any given suite adds reading and test runs, and that target tests might lower tokens by making the interface explicit. A difference shows the tests changed the effort spent. It does not show productivity or port quality.

![Shell commands](charts/bash-calls.png)

Bash tool calls.

![File edits](charts/edit-calls.png)

Edit tool calls.

![Network fetch and install attempts](charts/fetch-attempts.png)

WebFetch and WebSearch calls plus `curl`, `wget`, `pip install` and `npm install` commands.

![Turn of the first write into the port](charts/first-write-turn.png)

Assistant turn at which the agent first writes into the port.

![Failed tests in the last run of the agent's own tests](charts/last-own-tests-failed.png)

Tests reported failed by the last run of the agent's own tests; no dot when no run or no readable summary.

![Passed tests in the last run of the agent's own tests](charts/last-own-tests-passed.png)

Tests reported passed by the last run of the agent's own tests; no dot when no run or no readable summary.

![Failed tests in the last run of the source language's tests](charts/last-source-tests-failed.png)

Tests reported failed by the last run of the source language's tests; no dot when no run or no readable summary.

![Passed tests in the last run of the source language's tests](charts/last-source-tests-passed.png)

Tests reported passed by the last run of the source language's tests; no dot when no run or no readable summary.

![Turn of the last test run](charts/last-suite-run-turn.png)

Assistant turn of the last test-suite run.

![Failed tests in the last run of the target language's tests](charts/last-target-tests-failed.png)

Tests reported failed by the last run of the target language's tests; no dot when no run or no readable summary.

![Passed tests in the last run of the target language's tests](charts/last-target-tests-passed.png)

Tests reported passed by the last run of the target language's tests; no dot when no run or no readable summary.

![Failed tests in the last test run covering more than one of source tests, target tests and own tests](charts/last-unknown-failed.png)

Tests reported failed by the last test run covering more than one of source tests, target tests and own tests; no dot when no run or no readable summary.

![Passed tests in the last test run covering more than one of source tests, target tests and own tests](charts/last-unknown-passed.png)

Tests reported passed by the last test run covering more than one of source tests, target tests and own tests; no dot when no run or no readable summary.

![File reads by the Read tool](charts/read-calls.png)

Read tool calls (shell reads such as `cat` are not included).

![File searches](charts/search-calls.png)

Glob and Grep tool calls.

![Tokens from the first write into the port on](charts/tokens-after-first-write.png)

Input, output and cache tokens summed over turns from the first write on.

![Tokens before the first write into the port](charts/tokens-before-first-write.png)

Input, output and cache tokens summed over turns before the first write.

![Assistant turns](charts/turns.png)

Assistant messages in the run.

![Whole-file writes](charts/write-calls.png)

Write tool calls.

Median [25th, 75th percentile] per condition, from the notebook; n counts successful ports.

| Direction | Given tests | n | Total tokens | Suite runs | Own test files |
| --- | --- | --- | --- | --- | --- |
| python → javascript | none | 12 | 1112026.5 [1040397.75, 1285314.75] | 4.0 [2.75, 5.25] | 2.0 [1.0, 2.0] |
| python → javascript | unit | 12 | 2995979.5 [2734251.75, 3134006.75] | 10.0 [9.0, 11.25] | 24.0 [23.0, 25.0] |
| python → javascript | source | 12 | 1360515.5 [1296947.5, 1496816.75] | 4.5 [3.75, 6.0] | 1.0 [0.75, 6.0] |
| python → javascript | target | 12 | 1073723.5 [967378.25, 1178212.5] | 4.0 [3.75, 4.0] | 1.0 [0.0, 1.0] |
| python → javascript | unit + source | 12 | 3236537.5 [2919203.0, 3585524.25] | 9.0 [7.75, 10.0] | 22.5 [21.75, 23.25] |
| python → javascript | unit + target | 12 | 2842488.5 [2792119.25, 2941703.25] | 10.0 [9.0, 11.0] | 22.0 [21.0, 22.25] |
| python → javascript | source + target | 12 | 1072875.5 [976667.75, 1190370.25] | 3.0 [2.75, 4.0] | 0.0 [0.0, 1.0] |
| python → javascript | all | 12 | 2716913.5 [2565081.5, 2971104.25] | 11.0 [8.0, 12.0] | 22.0 [21.0, 22.0] |
| javascript → python | none | 12 | 1474019.0 [1417619.0, 1623198.0] | 8.0 [5.75, 10.25] | 1.0 [1.0, 1.25] |
| javascript → python | unit | 12 | 2457313.5 [2235225.5, 2843651.0] | 4.0 [3.75, 6.5] | 7.0 [6.0, 14.5] |
| javascript → python | source | 12 | 1595021.5 [1529789.25, 1846382.5] | 3.0 [2.0, 3.75] | 0.5 [0.0, 6.25] |
| javascript → python | target | 12 | 842847.5 [809326.0, 936980.75] | 3.0 [1.75, 4.0] | 0.0 [0.0, 0.0] |
| javascript → python | unit + source | 12 | 3287713.0 [2679757.5, 4080672.25] | 7.5 [5.75, 9.5] | 22.0 [11.25, 25.0] |
| javascript → python | unit + target | 12 | 2869219.5 [2621371.25, 3354633.75] | 10.5 [9.0, 12.25] | 23.0 [23.0, 24.0] |
| javascript → python | source + target | 12 | 1254455.5 [1188150.0, 1543225.0] | 3.0 [2.75, 4.0] | 1.0 [0.75, 1.0] |
| javascript → python | all | 12 | 3085734.5 [2993864.0, 3363053.0] | 10.0 [10.0, 11.0] | 23.0 [23.0, 24.0] |

All attempts per condition, failed ones included, from the notebook; tokens per success is all attempts' tokens over successful ports; API errors counts attempts whose result records `api_error`.

| Direction | Given tests | Attempts | Exit 0 | Exit 137 | API errors | Tokens per success |
| --- | --- | --- | --- | --- | --- | --- |
| python → javascript | none | 16 | 12 | 0 | 4 | 1141352.83 |
| python → javascript | unit | 16 | 12 | 0 | 4 | 2904434.75 |
| python → javascript | source | 16 | 12 | 0 | 4 | 1385997.33 |
| python → javascript | target | 16 | 12 | 0 | 4 | 1092986.75 |
| python → javascript | unit + source | 17 | 12 | 0 | 5 | 3303547.25 |
| python → javascript | unit + target | 17 | 12 | 0 | 5 | 3105329.83 |
| python → javascript | source + target | 16 | 12 | 0 | 4 | 1105363.25 |
| python → javascript | all | 16 | 12 | 0 | 4 | 2791548.33 |
| javascript → python | none | 20 | 12 | 3 | 5 | 1778007.67 |
| javascript → python | unit | 16 | 12 | 0 | 4 | 2485619.83 |
| javascript → python | source | 19 | 12 | 3 | 4 | 2068407.75 |
| javascript → python | target | 16 | 12 | 0 | 4 | 948710.92 |
| javascript → python | unit + source | 16 | 12 | 0 | 4 | 3405525.92 |
| javascript → python | unit + target | 16 | 12 | 0 | 4 | 3047596.33 |
| javascript → python | source + target | 17 | 12 | 1 | 4 | 1568387.33 |
| javascript → python | all | 17 | 12 | 1 | 4 | 3374072 |

## Reading

Counted from each run's transcript, subagents included: the files read, in order. A read is a Read call or a reading shell command such as `cat`, `head` or `grep`. Each file is classed as source code, source-language tests, target-language tests, the port, or other.

Measures: reads per class; distinct files read before the first write into the port; rereads (reads of a file already read) and the most rereads of one file; Glob and Grep calls per distinct file read; reads after the last write; the class of the first file read; whether the first source file read is the package's entry point; whether the run touched each given suite. No dot means the event never happened.

The hypothesis was that each given suite raises reads of its own tests and reading before the first write. A difference shows the tests changed what the agent did, not that it understood more. Reads the parser cannot recognise are missed; a recursive grep of a directory counts as one read. It matters because reading is the route by which tests could reach the port. [Measure definition](https://github.com/thekevinscott/ports-research/blob/3e610fb80bcc3d51cb93142c5b732e2c08fad64b/analysis/measure-transcript/README.md).

![Files read before the first write into the port](charts/files-read-before-first-write.png)

Distinct files read before the agent first writes into the port.

![Most rereads of one file](charts/max-rereads-of-one-file.png)

Rereads of the single most reread file.

![Reads of the source language's tests](charts/read-source-tests.png)

Reads of files in the source language's shipped test suites.

![Reads of the source code](charts/read-source.png)

Reads of source-language files other than its tests.

![Reads of the target language's tests](charts/read-target-tests.png)

Reads of files in the target language's shipped integration tests.

![Reads after the last write into the port](charts/reads-after-last-write.png)

Reads after the agent's last write into the port.

![Searches per file read](charts/search-calls-per-file-read.png)

Glob and Grep calls over distinct files read.

![Source files read before the first write into the port](charts/source-files-read-before-first-write.png)

Distinct source-language files read before the agent first writes into the port.

Median [25th, 75th percentile] per condition, from the notebook; n counts successful ports.

| Direction | Given tests | n | Source-test reads | Target-test reads | Paths read before first write | Rereads |
| --- | --- | --- | --- | --- | --- | --- |
| python → javascript | none | 12 | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 40.0 [39.75, 40.0] | 0.0 [0.0, 1.25] |
| python → javascript | unit | 12 | 5.0 [3.75, 6.0] | 0.0 [0.0, 0.0] | 61.5 [61.0, 62.25] | 10.5 [7.25, 13.25] |
| python → javascript | source | 12 | 3.5 [3.0, 4.0] | 0.0 [0.0, 0.0] | 44.0 [43.0, 44.0] | 7.0 [5.75, 10.25] |
| python → javascript | target | 12 | 0.0 [0.0, 0.0] | 4.0 [3.0, 4.0] | 47.0 [46.0, 47.25] | 6.0 [5.5, 7.25] |
| python → javascript | unit + source | 12 | 7.0 [6.0, 8.25] | 0.0 [0.0, 0.0] | 67.5 [63.0, 69.0] | 15.0 [10.75, 19.75] |
| python → javascript | unit + target | 12 | 9.0 [7.75, 10.5] | 3.0 [2.0, 4.0] | 57.5 [51.5, 72.0] | 39.5 [31.75, 50.25] |
| python → javascript | source + target | 12 | 1.0 [0.75, 1.0] | 4.0 [3.0, 5.0] | 47.0 [16.75, 48.25] | 9.0 [7.0, 10.25] |
| python → javascript | all | 12 | 9.0 [8.0, 11.0] | 3.5 [3.0, 4.0] | 66.5 [51.75, 70.0] | 40.5 [28.0, 46.25] |
| javascript → python | none | 12 | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 24.0 [8.0, 38.25] | 0.0 [0.0, 0.25] |
| javascript → python | unit | 12 | 4.5 [3.0, 6.0] | 0.0 [0.0, 0.0] | 21.0 [10.0, 31.0] | 7.0 [6.0, 11.25] |
| javascript → python | source | 12 | 4.5 [4.0, 5.0] | 0.0 [0.0, 0.0] | 43.0 [42.0, 44.0] | 10.5 [7.75, 14.25] |
| javascript → python | target | 12 | 0.0 [0.0, 0.0] | 3.0 [3.0, 4.0] | 41.0 [40.75, 42.25] | 9.5 [6.0, 11.0] |
| javascript → python | unit + source | 12 | 11.0 [9.75, 14.0] | 0.0 [0.0, 0.0] | 59.5 [52.0, 67.5] | 20.0 [12.0, 41.0] |
| javascript → python | unit + target | 12 | 9.0 [7.75, 10.25] | 3.5 [3.0, 4.0] | 46.0 [36.5, 54.25] | 29.5 [24.0, 39.5] |
| javascript → python | source + target | 12 | 2.0 [1.0, 2.0] | 3.0 [3.0, 4.0] | 43.0 [42.5, 44.0] | 9.0 [8.0, 14.5] |
| javascript → python | all | 12 | 10.5 [9.0, 12.0] | 3.5 [3.0, 4.25] | 50.5 [45.25, 64.5] | 39.5 [29.5, 54.25] |

## Structure

The port's code against the reference's in the target language, by structure only. Functions pair when their names match (ignoring case and underscores) and they take the same number of parameters. The paired share is the share of the reference's functions with a partner.

Tree distance counts the syntax-tree edits needed to turn one paired function into the other, over the larger tree's size: 0 same shape, 1 nothing shared. Branching distance compares how branch counts (if, loop, catch, and/or) spread across functions on each side: 0 same spread.

Call paths start at each public function both sides export and follow calls inside the package. Edge recall is the share of the reference's caller→callee links the port also has. Trace distance is how far the order of visited functions differs: 0 same, 1 entirely different. Reachable share is the share of a side's functions that some entry point reaches.

"Port minus reference" charts subtract the reference's count from the port's; 0 means equal size, not equal code. Cyclomatic complexity is 1 plus a function's branch count.

The hypothesis was that unit tests, which name internal functions, would raise the paired share and edge recall and lower the distances, and that target tests would keep exported names and entry-point paths. A difference shows drift from the reference's structure, not quality or correctness. Matching calls by name and parameter count can miss or overcount calls. [Measure definition](https://github.com/thekevinscott/ports-research/blob/3e610fb80bcc3d51cb93142c5b732e2c08fad64b/analysis/measure-ast/README.md); [analysis plan](https://github.com/thekevinscott/ports-research/blob/3e610fb80bcc3d51cb93142c5b732e2c08fad64b/notes/ANALYSIS_PLAN_2026-10-12.md).

![Public API entries only the port exports](charts/ast-api-port-only.png)

Count of exported names (with parameter count) the port has and the reference lacks.

![Public API entries only the reference exports](charts/ast-api-reference-only.png)

Count of exported names (with parameter count) the reference has and the port lacks.

![Public API entries both export](charts/ast-api-shared.png)

Count of exported names (with parameter count) present on both sides.

![Difference in branching between port and reference](charts/ast-branching-wasserstein.png)

How far apart the two sides' spreads of per-function branch counts are (Wasserstein distance; 0 same spread).

![Functions, port minus reference](charts/ast-delta-function-count.png)

Port's function count minus the reference's; 0 equal count.

![Most branches in one function, port minus reference](charts/ast-delta-max-cyclomatic.png)

Highest cyclomatic complexity (1 plus a function's branch count) in the port minus that in the reference.

![Deepest nesting, port minus reference](charts/ast-delta-max-depth.png)

Deepest syntax-tree nesting in the port minus that in the reference.

![Longest function in lines, port minus reference](charts/ast-delta-max-function-lines.png)

Lines of the port's longest function minus lines of the reference's longest.

![Mean branches per function, port minus reference](charts/ast-delta-mean-cyclomatic.png)

Mean cyclomatic complexity (1 plus a function's branch count) in the port minus that in the reference.

![Mean function length in lines, port minus reference](charts/ast-delta-mean-function-lines.png)

Mean lines per function in the port minus that in the reference.

![Syntax-tree size, port minus reference](charts/ast-delta-node-count.png)

Syntax-tree nodes in the port minus nodes in the reference; a size measure.

![Public functions both sides export (call-path starting points)](charts/ast-entry-point-count.png)

Count of shared public functions and class methods from which call paths are traced.

![Port functions paired with a reference function](charts/ast-matched-count.png)

Count of functions paired across sides by name and parameter count.

![Share of the reference's call links the port also makes](charts/ast-mean-edge-recall.png)

Per entry point, the share of the reference's caller→callee links present in the port, averaged over entry points; 1 all present.

![Length difference of paired functions in lines](charts/ast-median-line-drift.png)

Median over paired functions of port lines minus reference lines; 0 same length.

![Difference in call order from each entry point](charts/ast-median-trace-normalised.png)

Edit distance between the orders in which each side visits functions from an entry point, over the longer order, median over entry points; 0 same order, 1 entirely different.

![Port functions with no reference counterpart](charts/ast-port-only-count.png)

Count of port functions no reference function pairs with.

![Share of the port's functions reachable from an entry point](charts/ast-reachable-fraction-port.png)

Port functions some shared entry point calls, directly or indirectly, over all port functions.

![Share of the reference's functions reachable from an entry point](charts/ast-reachable-fraction-reference.png)

Reference functions some shared entry point calls, directly or indirectly, over all reference functions.

![Reference functions with no port counterpart](charts/ast-reference-only-count.png)

Count of reference functions no port function pairs with.

![Shape difference of paired functions (mean)](charts/ast-tree-edit-mean.png)

Tree edit distance over the larger tree's size, mean over paired functions; 0 same shape, 1 nothing shared.

![Port functions no entry point reaches](charts/ast-unreachable-port-only.png)

Count of port functions no shared entry point calls, directly or indirectly.

Median [25th, 75th percentile] per condition, from the notebook; n counts successful ports.

| Direction | Given tests | n | Reference call edges retained (mean share) | Call-trace distance (median) |
| --- | --- | --- | --- | --- |
| python → javascript | none | 12 | 0.46 [0.46, 0.48] | 0.36 [0.33, 0.38] |
| python → javascript | unit | 12 | 0.47 [0.46, 0.51] | 0.4 [0.39, 0.42] |
| python → javascript | source | 12 | 0.46 [0.46, 0.49] | 0.33 [0.33, 0.37] |
| python → javascript | target | 12 | 0.47 [0.45, 0.49] | 0.33 [0.33, 0.34] |
| python → javascript | unit + source | 12 | 0.47 [0.46, 0.47] | 0.42 [0.4, 0.44] |
| python → javascript | unit + target | 12 | 0.47 [0.46, 0.52] | 0.33 [0.33, 0.37] |
| python → javascript | source + target | 12 | 0.52 [0.47, 0.55] | 0.33 [0.33, 0.33] |
| python → javascript | all | 12 | 0.47 [0.46, 0.52] | 0.34 [0.33, 0.39] |
| javascript → python | none | 12 | 0.68 [0.67, 0.73] | 0.41 [0.33, 0.5] |
| javascript → python | unit | 12 | 0.7 [0.67, 0.73] | 0.45 [0.43, 0.48] |
| javascript → python | source | 12 | 0.72 [0.67, 0.72] | 0.41 [0.39, 0.49] |
| javascript → python | target | 12 | 0.65 [0.65, 0.7] | 0.25 [0.18, 0.33] |
| javascript → python | unit + source | 12 | 0.72 [0.66, 0.73] | 0.44 [0.43, 0.48] |
| javascript → python | unit + target | 12 | 0.74 [0.73, 0.74] | 0.38 [0.33, 0.41] |
| javascript → python | source + target | 12 | 0.73 [0.67, 0.74] | 0.29 [0.23, 0.33] |
| javascript → python | all | 12 | 0.73 [0.71, 0.73] | 0.39 [0.37, 0.43] |

## Statistics

For each lead measure and each flag, the runs with the flag on are compared with the runs with it off, pooled over both directions and within each. The gap is the on median minus the off median.

p is the share of 10,000 random reshuffles of the on/off labels (seed 0) that give a gap at least as far from zero. The 95% interval is a bootstrap range on the gap (10,000 resamples, seed 0); wide means imprecise. The smallest detectable gap is the smallest gap the reshuffles could call p < 0.05 at this n; a row with p ≥ 0.05 means a gap too small to see at this n, not no effect.

The study runs many tests without correction, so these are screening numbers, not confirmations. Values are the notebook's, with its rounding; only the labels are renamed.

### Held-out behaviour agreement with the reference (%)

| Flag | Direction | n on | n off | Median on | Median off | Gap | 95% low | 95% high | p | Smallest detectable gap |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| unit tests | pooled | 96 | 96 | 97.5 | 97.5 | 0 | -1.88 | 0 | 1 | 0 |
| unit tests | python → javascript | 48 | 48 | 97.5 | 97.5 | 0 | 0 | 0.63 | 1 | 0 |
| unit tests | javascript → python | 48 | 48 | 99.37 | 99.37 | 0 | -59.57 | 0 | 1 | 1.25 |
| source tests | pooled | 96 | 96 | 97.5 | 97.5 | 0 | -11.39 | 0 | 1 | 0 |
| source tests | python → javascript | 48 | 48 | 97.5 | 97.5 | 0 | -0.63 | 0 | 1 | 0 |
| source tests | javascript → python | 48 | 48 | 99.37 | 99.37 | 0 | -59.57 | 0 | 1 | 1.25 |
| target tests | pooled | 96 | 96 | 97.5 | 39.8 | 57.7 | 28.22 | 59.57 | 0.0001 | 0 |
| target tests | python → javascript | 48 | 48 | 97.5 | 76.53 | 20.96 | 0 | 41.3 | 0.0005 | 0 |
| target tests | javascript → python | 48 | 48 | 99.37 | 39.8 | 59.57 | 59.57 | 99.37 | 0.0033 | 1.25 |

### Held-out API agreement with the reference (%)

| Flag | Direction | n on | n off | Median on | Median off | Gap | 95% low | 95% high | p | Smallest detectable gap |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| unit tests | pooled | 96 | 96 | 87.79 | 87.79 | 0 | -7.11 | 0 | 1 | 0 |
| unit tests | python → javascript | 48 | 48 | 87.79 | 87.79 | 0 | 0 | 2.2 | 1 | 0 |
| unit tests | javascript → python | 48 | 48 | 94.89 | 94.89 | 0 | -85.89 | 0 | 1 | 5.41 |
| source tests | pooled | 96 | 96 | 87.79 | 87.79 | 0 | -40.49 | 0 | 1 | 0 |
| source tests | python → javascript | 48 | 48 | 87.79 | 87.79 | 0 | -2.2 | 0.75 | 1 | 0 |
| source tests | javascript → python | 48 | 48 | 94.89 | 94.89 | 0 | -85.89 | 0 | 1 | 5.41 |
| target tests | pooled | 96 | 96 | 91.34 | 9.01 | 82.33 | 78.23 | 85.89 | 0.0001 | 0 |
| target tests | python → javascript | 48 | 48 | 87.79 | 48.05 | 39.74 | 0 | 77.28 | 0.0005 | 0 |
| target tests | javascript → python | 48 | 48 | 94.89 | 9.01 | 85.89 | 85.89 | 85.89 | 0.0119 | 5.41 |

### Share of the reference's functions the port has a counterpart for

| Flag | Direction | n on | n off | Median on | Median off | Gap | 95% low | 95% high | p | Smallest detectable gap |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| unit tests | pooled | 96 | 96 | 0.78 | 0.75 | 0.03 | 0.02 | 0.04 | 0.0001 | 0.01 |
| unit tests | python → javascript | 48 | 48 | 0.79 | 0.77 | 0.02 | 0.02 | 0.04 | 0.0334 | 0.01 |
| unit tests | javascript → python | 48 | 48 | 0.76 | 0.73 | 0.03 | 0.01 | 0.04 | 0.0001 | 0.01 |
| source tests | pooled | 96 | 96 | 0.76 | 0.77 | -0.01 | -0.02 | 0.01 | 0.7745 | 0.01 |
| source tests | python → javascript | 48 | 48 | 0.77 | 0.79 | -0.01 | -0.02 | 0 | 0.0796 | 0.01 |
| source tests | javascript → python | 48 | 48 | 0.75 | 0.75 | -0.01 | -0.02 | 0.01 | 0.6851 | 0.01 |
| target tests | pooled | 96 | 96 | 0.76 | 0.77 | -0.01 | -0.02 | 0.01 | 0.7755 | 0.01 |
| target tests | python → javascript | 48 | 48 | 0.77 | 0.79 | -0.02 | -0.03 | 0 | 0.0331 | 0.01 |
| target tests | javascript → python | 48 | 48 | 0.76 | 0.75 | 0.01 | 0 | 0.02 | 0.0523 | 0.01 |

### Shape difference of paired functions (median)

| Flag | Direction | n on | n off | Median on | Median off | Gap | 95% low | 95% high | p | Smallest detectable gap |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| unit tests | pooled | 96 | 96 | 0.28 | 0.29 | -0.01 | -0.03 | 0.01 | 0.1813 | 0.02 |
| unit tests | python → javascript | 48 | 48 | 0.26 | 0.26 | 0 | -0.01 | 0.01 | 0.8939 | 0.01 |
| unit tests | javascript → python | 48 | 48 | 0.31 | 0.33 | -0.02 | -0.04 | 0 | 0.0518 | 0.02 |
| source tests | pooled | 96 | 96 | 0.29 | 0.29 | 0 | -0.02 | 0.01 | 0.6752 | 0.02 |
| source tests | python → javascript | 48 | 48 | 0.26 | 0.26 | 0 | -0.01 | 0.01 | 0.8434 | 0.01 |
| source tests | javascript → python | 48 | 48 | 0.32 | 0.33 | -0.01 | -0.03 | 0 | 0.1397 | 0.02 |
| target tests | pooled | 96 | 96 | 0.28 | 0.3 | -0.01 | -0.04 | 0 | 0.0598 | 0.02 |
| target tests | python → javascript | 48 | 48 | 0.25 | 0.27 | -0.02 | -0.02 | -0.01 | 0.0021 | 0.01 |
| target tests | javascript → python | 48 | 48 | 0.3 | 0.34 | -0.04 | -0.04 | -0.02 | 0.0001 | 0.02 |

### Difference in branching between port and reference

| Flag | Direction | n on | n off | Median on | Median off | Gap | 95% low | 95% high | p | Smallest detectable gap |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| unit tests | pooled | 96 | 96 | 0.28 | 0.26 | 0.01 | -0.02 | 0.04 | 0.3559 | 0.03 |
| unit tests | python → javascript | 48 | 48 | 0.32 | 0.31 | 0.01 | -0.05 | 0.04 | 0.792 | 0.03 |
| unit tests | javascript → python | 48 | 48 | 0.24 | 0.22 | 0.01 | -0.01 | 0.03 | 0.0854 | 0.02 |
| source tests | pooled | 96 | 96 | 0.27 | 0.27 | -0.01 | -0.04 | 0.02 | 0.7854 | 0.03 |
| source tests | python → javascript | 48 | 48 | 0.32 | 0.31 | 0.01 | -0.03 | 0.04 | 0.8617 | 0.03 |
| source tests | javascript → python | 48 | 48 | 0.23 | 0.23 | 0 | -0.03 | 0.02 | 0.8974 | 0.02 |
| target tests | pooled | 96 | 96 | 0.29 | 0.26 | 0.03 | 0 | 0.07 | 0.0146 | 0.03 |
| target tests | python → javascript | 48 | 48 | 0.36 | 0.28 | 0.07 | 0.05 | 0.1 | 0.0001 | 0.03 |
| target tests | javascript → python | 48 | 48 | 0.23 | 0.23 | 0 | -0.02 | 0.02 | 0.7338 | 0.02 |

### Share of the reference's call links the port also makes

| Flag | Direction | n on | n off | Median on | Median off | Gap | 95% low | 95% high | p | Smallest detectable gap |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| unit tests | pooled | 96 | 96 | 0.61 | 0.57 | 0.04 | -0.11 | 0.11 | 0.6448 | 0.12 |
| unit tests | python → javascript | 48 | 48 | 0.47 | 0.47 | 0 | -0.01 | 0 | 1 | 0 |
| unit tests | javascript → python | 48 | 48 | 0.73 | 0.68 | 0.05 | 0 | 0.06 | 0.0271 | 0.04 |
| source tests | pooled | 96 | 96 | 0.57 | 0.57 | 0 | -0.11 | 0.12 | 0.9988 | 0.12 |
| source tests | python → javascript | 48 | 48 | 0.47 | 0.47 | 0 | 0 | 0.01 | 1 | 0 |
| source tests | javascript → python | 48 | 48 | 0.72 | 0.7 | 0.03 | -0.01 | 0.05 | 0.1251 | 0.04 |
| target tests | pooled | 96 | 96 | 0.57 | 0.57 | 0 | -0.11 | 0.12 | 0.9979 | 0.12 |
| target tests | python → javascript | 48 | 48 | 0.47 | 0.47 | 0 | 0 | 0.05 | 1 | 0 |
| target tests | javascript → python | 48 | 48 | 0.73 | 0.72 | 0.01 | -0.02 | 0.06 | 0.372 | 0.04 |

### Difference in call order from each entry point

| Flag | Direction | n on | n off | Median on | Median off | Gap | 95% low | 95% high | p | Smallest detectable gap |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| unit tests | pooled | 96 | 96 | 0.4 | 0.33 | 0.07 | 0.06 | 0.09 | 0.0005 | 0.04 |
| unit tests | python → javascript | 48 | 48 | 0.4 | 0.33 | 0.06 | 0.03 | 0.08 | 0.0002 | 0.04 |
| unit tests | javascript → python | 48 | 48 | 0.43 | 0.33 | 0.1 | 0.03 | 0.13 | 0.0001 | 0.04 |
| source tests | pooled | 96 | 96 | 0.38 | 0.37 | 0.01 | -0.03 | 0.05 | 0.5754 | 0.04 |
| source tests | python → javascript | 48 | 48 | 0.34 | 0.36 | -0.01 | -0.05 | 0.04 | 0.6858 | 0.04 |
| source tests | javascript → python | 48 | 48 | 0.4 | 0.39 | 0.01 | -0.02 | 0.08 | 0.3256 | 0.04 |
| target tests | pooled | 96 | 96 | 0.33 | 0.41 | -0.07 | -0.09 | -0.07 | 0.0001 | 0.04 |
| target tests | python → javascript | 48 | 48 | 0.33 | 0.39 | -0.06 | -0.07 | -0.04 | 0.0021 | 0.04 |
| target tests | javascript → python | 48 | 48 | 0.33 | 0.43 | -0.1 | -0.16 | -0.05 | 0.0001 | 0.04 |

### Total tokens

| Flag | Direction | n on | n off | Median on | Median off | Gap | 95% low | 95% high | p | Smallest detectable gap |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| unit tests | pooled | 96 | 96 | 2944917.5 | 1236706 | 1708211.5 | 1576081 | 1843637.45 | 0.0001 | 884390 |
| unit tests | python → javascript | 48 | 48 | 2908043 | 1131662 | 1776381 | 1603192.16 | 1887206 | 0.0001 | 1196819 |
| unit tests | javascript → python | 48 | 48 | 2995255.5 | 1403736 | 1591519.5 | 1340403.5 | 1853011 | 0.0001 | 859816.5 |
| source tests | pooled | 96 | 96 | 2295962 | 1818696 | 477266 | -615016.3 | 1106226.08 | 0.4838 | 878610.5 |
| source tests | python → javascript | 48 | 48 | 1991383 | 1859621 | 131762 | -1150085.82 | 1313721 | 0.9124 | 1196256 |
| source tests | javascript → python | 48 | 48 | 2512115.5 | 1818696 | 693419.5 | -493707.67 | 1286513 | 0.171 | 861394.5 |
| target tests | pooled | 96 | 96 | 2190526 | 2016821.5 | 173704.5 | -955289 | 843075.12 | 0.8204 | 892343.5 |
| target tests | python → javascript | 48 | 48 | 1860776 | 1960712 | -99936 | -1456272.04 | 1079213.22 | 0.9336 | 1200375 |
| target tests | javascript → python | 48 | 48 | 2296659 | 2016821.5 | 279837.5 | -929054 | 1045305 | 0.6957 | 866518 |

### Lines of code in the port

| Flag | Direction | n on | n off | Median on | Median off | Gap | 95% low | 95% high | p | Smallest detectable gap |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| unit tests | pooled | 96 | 96 | 996.5 | 966 | 30.5 | 12 | 63.5 | 0.0012 | 16 |
| unit tests | python → javascript | 48 | 48 | 1000 | 967.5 | 32.5 | 10 | 69.01 | 0.0007 | 16.5 |
| unit tests | javascript → python | 48 | 48 | 994 | 962 | 32 | -13 | 78 | 0.1441 | 40 |
| source tests | pooled | 96 | 96 | 982.5 | 978 | 4.5 | -15 | 21.5 | 0.7108 | 16 |
| source tests | python → javascript | 48 | 48 | 983 | 984 | -1 | -20.5 | 18 | 0.8603 | 16.5 |
| source tests | javascript → python | 48 | 48 | 978 | 971 | 7 | -30.5 | 53 | 0.7613 | 39.5 |
| target tests | pooled | 96 | 96 | 997 | 971 | 26 | 8.5 | 55 | 0.0023 | 16.5 |
| target tests | python → javascript | 48 | 48 | 984 | 980 | 4 | -18.5 | 22 | 0.5024 | 16.5 |
| target tests | javascript → python | 48 | 48 | 1017.5 | 941.5 | 76 | 41 | 102 | 0.0001 | 40 |

### Reads of the source language's tests

| Flag | Direction | n on | n off | Median on | Median off | Gap | 95% low | 95% high | p | Smallest detectable gap |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| unit tests | pooled | 96 | 96 | 8 | 0 | 8 | 6.5 | 9 | 0.0001 | 2 |
| unit tests | python → javascript | 48 | 48 | 7.5 | 0 | 7.5 | 6 | 9 | 0.0001 | 2.5 |
| unit tests | javascript → python | 48 | 48 | 9 | 0.5 | 8.5 | 6.5 | 10 | 0.0001 | 3 |
| source tests | pooled | 96 | 96 | 5 | 0.5 | 4.5 | 1 | 7 | 0.0001 | 2 |
| source tests | python → javascript | 48 | 48 | 4.5 | 1 | 3.5 | -0.5 | 6 | 0.011 | 2.5 |
| source tests | javascript → python | 48 | 48 | 6.5 | 0.5 | 6 | 1.5 | 9 | 0.0001 | 3 |
| target tests | pooled | 96 | 96 | 3 | 4 | -1 | -3 | 3.5 | 0.3274 | 2 |
| target tests | python → javascript | 48 | 48 | 3 | 4 | -1 | -3.5 | 4 | 0.4638 | 2.5 |
| target tests | javascript → python | 48 | 48 | 3 | 4.5 | -1.5 | -3.5 | 4 | 0.4677 | 3 |

### Reads of the target language's tests

| Flag | Direction | n on | n off | Median on | Median off | Gap | 95% low | 95% high | p | Smallest detectable gap |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| unit tests | pooled | 96 | 96 | 1 | 1 | 0 | -3 | 3 | 1 | 3 |
| unit tests | python → javascript | 48 | 48 | 1 | 1 | 0 | -3 | 2.5 | 1 | 3 |
| unit tests | javascript → python | 48 | 48 | 1 | 1 | 0 | -3 | 3 | 1 | 3 |
| source tests | pooled | 96 | 96 | 1 | 1 | 0 | -3 | 3 | 1 | 3 |
| source tests | python → javascript | 48 | 48 | 1 | 1 | 0 | -3 | 3 | 1 | 3 |
| source tests | javascript → python | 48 | 48 | 1 | 1 | 0 | -3 | 3 | 1 | 3 |
| target tests | pooled | 96 | 96 | 3 | 0 | 3 | 3 | 4 | 0.1096 | 3 |
| target tests | python → javascript | 48 | 48 | 4 | 0 | 4 | 3 | 4 | 0.0001 | 3 |
| target tests | javascript → python | 48 | 48 | 3 | 0 | 3 | 3 | 4 | 0.3095 | 3 |

### Test-suite runs

| Flag | Direction | n on | n off | Median on | Median off | Gap | 95% low | 95% high | p | Smallest detectable gap |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| unit tests | pooled | 96 | 96 | 9.5 | 4 | 5.5 | 5 | 7 | 0.0001 | 2 |
| unit tests | python → javascript | 48 | 48 | 10 | 4 | 6 | 5 | 7 | 0.0001 | 3 |
| unit tests | javascript → python | 48 | 48 | 9 | 3 | 6 | 4 | 7 | 0.0001 | 2.5 |
| source tests | pooled | 96 | 96 | 6 | 6 | 0 | -3 | 2 | 1 | 2 |
| source tests | python → javascript | 48 | 48 | 6 | 6.5 | -0.5 | -3.5 | 2.5 | 1 | 3 |
| source tests | javascript → python | 48 | 48 | 5.5 | 6 | -0.5 | -3.5 | 2.5 | 0.9954 | 2.5 |
| target tests | pooled | 96 | 96 | 7 | 6 | 1 | -2 | 3 | 0.3534 | 2 |
| target tests | python → javascript | 48 | 48 | 7 | 6 | 1 | -4 | 3 | 0.7134 | 3 |
| target tests | javascript → python | 48 | 48 | 6 | 6 | 0 | -2.5 | 4 | 1 | 2.5 |

### Test files the agent wrote itself

| Flag | Direction | n on | n off | Median on | Median off | Gap | 95% low | 95% high | p | Smallest detectable gap |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| unit tests | pooled | 96 | 96 | 22.5 | 1 | 21.5 | 21 | 22 | 0.0001 | 9 |
| unit tests | python → javascript | 48 | 48 | 22 | 1 | 21 | 21 | 22 | 0.0002 | 19 |
| unit tests | javascript → python | 48 | 48 | 23 | 1 | 22 | 21 | 23 | 0.0001 | 6 |
| source tests | pooled | 96 | 96 | 7 | 4.5 | 2.5 | -5 | 19 | 0.2933 | 9 |
| source tests | python → javascript | 48 | 48 | 14 | 12 | 2 | -19 | 19 | 0.8378 | 19 |
| source tests | javascript → python | 48 | 48 | 7 | 4 | 3 | -3.5 | 19.5 | 0.3659 | 6 |
| target tests | pooled | 96 | 96 | 4.5 | 6 | -1.5 | -6 | 16 | 0.4865 | 9.5 |
| target tests | python → javascript | 48 | 48 | 11 | 13.5 | -2.5 | -21 | 17 | 0.8437 | 19 |
| target tests | javascript → python | 48 | 48 | 4.5 | 6 | -1.5 | -6 | 18.5 | 0.6399 | 6 |

### Files read before the first write into the port

| Flag | Direction | n on | n off | Median on | Median off | Gap | 95% low | 95% high | p | Smallest detectable gap |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| unit tests | pooled | 96 | 96 | 55 | 42.5 | 12.5 | 8.5 | 20 | 0.0001 | 2.5 |
| unit tests | python → javascript | 48 | 48 | 62.5 | 44 | 18.5 | 16 | 24 | 0.0001 | 5 |
| unit tests | javascript → python | 48 | 48 | 46 | 41 | 5 | -4 | 11 | 0.0012 | 3 |
| source tests | pooled | 96 | 96 | 46 | 41 | 5 | 0 | 9 | 0.0008 | 2.5 |
| source tests | python → javascript | 48 | 48 | 48.5 | 48.5 | 0 | -8 | 5.5 | 1 | 5 |
| source tests | javascript → python | 48 | 48 | 44 | 38 | 6 | 3 | 21 | 0.0002 | 3 |
| target tests | pooled | 96 | 96 | 47 | 43 | 4 | 1.5 | 6.5 | 0.0079 | 2.5 |
| target tests | python → javascript | 48 | 48 | 49 | 45 | 4 | -12.5 | 7.5 | 0.2695 | 5 |
| target tests | javascript → python | 48 | 48 | 44 | 39.5 | 4.5 | 0.5 | 12 | 0.0016 | 3 |

### Rereads

| Flag | Direction | n on | n off | Median on | Median off | Gap | 95% low | 95% high | p | Smallest detectable gap |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| unit tests | pooled | 96 | 96 | 24.5 | 7 | 17.5 | 11 | 24 | 0.0001 | 3.5 |
| unit tests | python → javascript | 48 | 48 | 24.5 | 6 | 18.5 | 10 | 27 | 0.0001 | 5 |
| unit tests | javascript → python | 48 | 48 | 24.5 | 8 | 16.5 | 7.5 | 22.5 | 0.0001 | 4.5 |
| source tests | pooled | 96 | 96 | 14 | 8 | 6 | 3 | 10 | 0.0006 | 3.5 |
| source tests | python → javascript | 48 | 48 | 13.5 | 7.5 | 6 | 0.5 | 10 | 0.023 | 5 |
| source tests | javascript → python | 48 | 48 | 16 | 9.5 | 6.5 | 2 | 16 | 0.0083 | 4.5 |
| target tests | pooled | 96 | 96 | 17 | 9 | 8 | 3 | 17.5 | 0.0001 | 3.5 |
| target tests | python → javascript | 48 | 48 | 16 | 8.5 | 7.5 | -1 | 22.5 | 0.003 | 5 |
| target tests | javascript → python | 48 | 48 | 17 | 10 | 7 | 1 | 18 | 0.0044 | 4.5 |

### Rank correlation with held-out behaviour

Spearman ρ between each measure and held-out behaviour agreement, over the n runs with both values; the notebook's three-decimal rounding.

| Measure | Spearman ρ | n |
| --- | --- | --- |
| Held-out API agreement (%) (`api_agreement_pct`) | 0.977 | 192 |
| Pairs the reference accepts, the port accepts (`reference_accept_port_accept`) | 0.959 | 192 |
| Pairs the reference errors, the port errors (`reference_error_port_error`) | 0.622 | 192 |
| Pairs the reference accepts, the port crashes (`reference_accept_port_crash`) | -0.621 | 192 |
| Pairs the reference rejects, the port crashes (`reference_reject_port_crash`) | -0.621 | 192 |
| Pairs the reference errors, the port crashes (`reference_error_port_crash`) | -0.621 | 192 |
| Pairs the reference errors, the port rejects (`reference_error_port_reject`) | 0.617 | 192 |
| Reads of target-language tests (`read_target_tests`) | 0.458 | 192 |
| Pairs the reference rejects, the port errors (`reference_reject_port_error`) | -0.447 | 192 |
| Pairs the reference rejects, the port rejects (`reference_reject_port_reject`) | 0.442 | 192 |
| Pairs the reference accepts, the port errors (`reference_accept_port_error`) | -0.427 | 192 |
| Lines of code in the port (`loc`) | 0.403 | 192 |
| Call-order difference from entry points (`ast_median_trace_normalised`) | -0.316 | 192 |
| Share of reference call links kept (`ast_mean_edge_recall`) | 0.303 | 192 |
| Wall time (`duration_ms`) | -0.292 | 192 |
| Test-suite runs (`suite_run_count`) | 0.153 | 192 |
| Pairs the reference accepts, the port rejects (`reference_accept_port_reject`) | -0.152 | 192 |
| Shape difference of paired functions (median) (`ast_tree_edit_median`) | 0.132 | 192 |
| Rereads (`reread_count`) | 0.108 | 192 |
| Reads of source-language tests (`read_source_tests`) | -0.087 | 192 |
| Model calls (`api_calls`) | 0.081 | 192 |
| Files in the port (`file_count`) | -0.078 | 192 |
| Pairs the reference rejects, the port accepts (`reference_reject_port_accept`) | 0.058 | 192 |
| Total tokens (`total_tokens`) | -0.048 | 192 |
| Own test files written (`own_tests_written`) | 0.028 | 192 |
| Files read before first write (`files_read_before_first_write`) | -0.026 | 192 |
| Branching difference (`ast_branching_wasserstein`) | 0 | 192 |
| Share of reference functions paired (`ast_matched_fraction`) | 0 | 192 |

![How per-run measures rank against each other on V2 runs (Spearman)](charts/spearman-matrix.png)

Spearman rank correlation between every pair of per-run measures over the 192 successful ports; each square's colour (red −1, white 0, blue +1) and printed number give ρ. Axis labels are notebook column names; the table above gives plain names for those paired with behaviour agreement.

## Not yet measured

**Embeddings.** Each code file is embedded as a vector. For two codebases, each file's distance to its nearest file on the other side is averaged, longer files weighted more. Low distance means the code reads alike to the embedding model. The hypothesis was that tests constrain implementation choices and lower the distance between ports given the same suites. A difference would concern this model's representation only, not behaviour or correctness. No V2 embedding charts exist: the notebook's embedding charts select V1 runs only, and the V1 pair export failed with `ValueError: cached file selection differs from source` for the Python reference.

**Judge.** An LLM judge scores each port under two rubrics. The code rubric rates API parity, structure, semantic divergences and idiom against the reference, plus a fidelity score. The transcript rubric rates cheating, structure decisions and reading strategy. The human-written reference pair is judged blind as a baseline. The hypothesis was that source tests raise judged semantic parity, unit tests judged structural fidelity, and target tests judged API parity. A difference would show what this judge rates, not correctness. In progress. [Rubric design](https://github.com/thekevinscott/ports-research/blob/3e610fb80bcc3d51cb93142c5b732e2c08fad64b/notes/ANALYSIS_PLAN_2026-10-12.md).

**Walkthroughs.** An LLM writes a step-by-step walkthrough of each implementation's public entry points, normal paths, error paths and invariants. Steps are matched across port and reference by embedding similarity. Coverage is the share of the reference's steps with a matching port step. Repeated walkthroughs of the reference give the spread expected from explanation alone. The hypothesis was that source tests raise coverage of behaviour and error paths, and target tests coverage of interface steps. A difference would show agreement between generated explanations, not code equivalence. In progress.
