# measure-api

Steps a held-out corpus of gbnf grammar × input cases through the public API of the reference and of a port, and reports per case whether every step's output agrees.

## Usage

```
measure-api generate --out <dir> --seed <int> --count <n>
measure-api run --corpus <dir> --implementation <dir> --language python|typescript --out <file>
measure-api compare --reference <file> --port <file> --out <file>
just reference
```

`generate` runs `measure-behavior generate` with the same seed and count, keeps its grammars and inputs (the empty string, strings drawn from the grammar, and their truncations, over-runs and edits), appends two random strings per grammar, and writes `manifest.json`. The same seed writes the same bytes.

`run` writes one JSON line per case: `grammar`, `input` (index into the input list), `steps`, `crash`. Each case runs in its own subprocess with a 10 s timeout. Python's driver takes `<implementation>` as its argument, puts it on `sys.path` and imports `gbnf`; typescript imports the default export of `<implementation>/src/index.ts` through tsx.

A case's steps, in order: `construct` is `GBNF(grammar)`; `whole` is `add(input)` on that state; `prefix 1` to `prefix k` add the input one code point at a time, each to the previous state, for the first 16 code points. A step that returns records the state's rules as `{type, value}` (python: the rule's class name and `value`; typescript: the rule's `type` and `value`). A step that raises records `{class, pos}`, `pos` being the exception's integer `pos` or null. A raise at `construct` ends the case; a raise in the prefix steps ends them; a raise at `whole` does not stop the prefix steps. `crash` is null, or the timeout, or the subprocess's stderr when it exits non-zero or prints no steps.

`compare` matches cases by `(grammar, input)` and compares them step by step. Two steps are equal when both return the same set of rules, or both raise the same class at the same `pos`; when the reference's `pos` is null only the class is compared.

- `match`: every step is equal and none raised.
- `mismatch`: the first unequal step returned rules on both sides.
- `error_match`: every step is equal and at least one raised.
- `error_mismatch`: the first unequal step raised on at least one side, or is missing on one side.
- `crash`: either side crashed.

`compare` writes `cases`, `agreements` (`match` + `error_match`), `agreement_rate`, `outcomes` (a count per outcome), `confusion` (a table of reference status × port status, status being `crash`, `error` when any step raised, else `ok`), and `disagreements`, one `{grammar, input, outcome, step, reference, port}` per `mismatch` or `error_mismatch` with the index of the first unequal step and both sides' record of it. It fails when the two files cover different cases.

`just reference` clones gbnf at the pin, applies `packages/gbnf_experiment/docker/gbnf-prepare/patches/`, and writes `corpus/reference-python.jsonl` and `corpus/reference-typescript.jsonl`.

## Corpus

`corpus/` is seed 0, 100 grammars, 999 cases. It is never mounted into an agent's container.
