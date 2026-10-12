# walkthroughs

Asks an LLM to walk through one implementation on its own, then compares two walkthroughs step by step.

Kevin, 2026-10-12: "In particular I wonder about asking an LLM to write explainers or walk through of the code- then compare those derivations".

## Usage

```
walkthroughs write --implementation <dir> --language python|typescript --out <dir> [--model M] [--effort E] [--tag T]
walkthroughs compare --reference <json> --port <json> (--embeddings-url <url> | --no-embeddings) [--threshold X]
walkthroughs reference-lines --out <dir> (--embeddings-url <url> | --no-embeddings) [--threshold X] [--model M] [--effort E]
just test-e2e <out> [<embeddings url>]
```

## write

One `claude` call: `prompts/walkthrough.md`, `---`, then each source file of the language under its relative path. Files are chosen by the judge's `source_files` (tests, dependencies, build configuration, `builder/` and `dev/` left out); python keeps `.py`, typescript keeps `.ts`, `.tsx`, `.mts`, `.cts`, `.js`, `.mjs`, `.cjs`.

The prompt follows [Sean Goedecke on reading code](https://www.seangoedecke.com/how-to-read-code/): public entry points; per entry point the happy path as ordered one-sentence steps naming what is called, then error paths, then invariants. It names neither a language nor a port. Output is held to `prompts/walkthrough.schema.json`: `{entry_points: [{name, happy_path, error_paths, invariants}]}`, each a list of strings.

The call is the judge's `judge_item`, imported: `claude -p --output-format json --json-schema <schema> --tools "" --safe-mode --no-session-persistence`, from an empty temporary directory, `ANTHROPIC_API_KEY` removed so the subscription pays.

Default model `claude-opus-5-5` at effort `high`: cheaper than the judge's `max`.

Output `<out>/<hash>.json`: `implementation`, `language`, `tag`, `model`, `effort`, `files`, `prompt_chars`, `walkthrough`, `raw`, `usage`, `wall_seconds`. The hash is over the prompt, model, effort and tag; an existing file skips the call. `--tag` asks for a repeat of the same implementation and never reaches the model. Prints the path.

## compare

Entry points pair by name with `_` dropped and case lowered; unpaired names are listed as `entry_points_reference_only` and `entry_points_port_only`.

Within a pair each section (happy path, error paths, invariants) is aligned on its own. Steps match one-to-one, most similar pair first, ties to the pair nearest in relative position; a pair below the threshold never matches. Per section: `coverage` (matched reference steps over reference steps), `order_agreement` (longest increasing run of matched port positions in reference order, over the matches), `extra_steps` (unmatched port steps), `missing_steps` (unmatched reference steps), `matches` (indices and similarity).

Aggregates: `mean_coverage` and `mean_order_agreement` over the pairs' happy paths, the same two under `error_paths` and `invariants`, `entry_points_matched`. A section with no reference steps has no coverage and one with no matches no order; both are left out of the means.

`sweep` repeats the aggregates at the threshold moved by -0.1, -0.05, 0, +0.05 and +0.1: `threshold`, `mean_coverage`, `mean_order_agreement`, `error_paths`, `invariants`. Each distinct step is still embedded once. `reference-lines` carries the same `sweep` in every comparison, so the noise floor and baseline can be read at each threshold.

Similarity is the cosine of embeddings from the server at `--embeddings-url`, threshold 0.8, each distinct step embedded once through `analysis/generate-embedding`'s CLI with the notebook's model `qwen3-embedding-0.6b-q8_0`. `--no-embeddings` uses word-set Jaccard on lowercased words instead, threshold 0.5. The output records `similarity`, `threshold` and `embeddings`: the url, the requested model and the server's `GET <url>/models` entry for it (a single-model server's only entry), null under `--no-embeddings`. A llama.cpp router's entry lists the model file and `--pooling` under `status.args`; a single-model server's does not report pooling.

## reference-lines

Clones gbnf at the pin with the experiment's patches (the judge's `clone_reference`), writes `packages/gbnf/python` and `packages/gbnf/javascript` twice each with tags `a` and `b`, four calls at once, and writes `<out>/reference-lines.json`: `walkthroughs` (file per reference and tag), `noise_floor` (`python` a vs b, `javascript` a vs b) and `baseline` (`python_to_javascript`, python a as reference against javascript a, and `javascript_to_python`), each a `compare` output. Prints the same.
