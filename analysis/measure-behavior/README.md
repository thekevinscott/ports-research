# measure-behavior

Runs a held-out corpus of gbnf grammar × input pairs through the reference and through a port, and reports how often their outcomes agree.

## Usage

```
measure-behavior generate --out <dir> --seed <int> --count <n>
measure-behavior run --corpus <dir> --implementation <dir> --language python|typescript --out <file>
measure-behavior compare --reference <file> --port <file> --out <file>
just reference
```

`generate` writes `<count>` grammars to `grammars/<id>.gbnf`, their inputs to `inputs/<id>.json`, and `manifest.json` with the seed, count and generator version. The same seed writes the same bytes. Grammars draw on literals, escapes (`\x \u \U \t \r \n \" \\ \[ \]`), character classes with ranges and negation, rule references, guarded recursion, grouping, alternation, `* + ?`, comments, multi-line rules and CRLF line endings. About one in five is malformed. Inputs are the empty string, strings drawn from the grammar, and mutations of them.

`run` writes one JSON line per pair: `grammar`, `input` (index into the input list), `outcome`, `error`. Each pair runs in its own subprocess with a 10 s timeout. Python imports `gbnf` with `PYTHONPATH=<implementation>`; typescript imports the default export of `<implementation>/src/index.ts` through tsx. The call is `GBNF(grammar, input)`.

- `accept`: the call returns and the state holds an end rule (`RuleEnd` in python, `type: "end"` in typescript).
- `reject`: the call returns with no end rule, or raises `InputParseError`.
- `error`: the call raises anything else.
- `crash`: the subprocess times out, exits non-zero, or prints no outcome.

`error` holds the exception's class and message, or the subprocess's stderr for a crash.

`compare` writes `pairs`, `agreements`, `agreement_rate` and `confusion`, a table of reference outcome × port outcome. It fails when the two files cover different pairs.

`just reference` clones gbnf at the pin, applies `packages/gbnf_experiment/docker/gbnf-prepare/patches/`, and writes `corpus/reference-python.jsonl` and `corpus/reference-typescript.jsonl`.

## Corpus

`corpus/` is seed 0, 100 grammars, 799 inputs. It is never mounted into an agent's container.
