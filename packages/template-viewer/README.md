# template-viewer

Render a Claude session transcript (`.jsonl`) as a self-contained, nicely
formatted HTML page.

## Usage

```
template-viewer path/to/transcript.jsonl
template-viewer path/to/run/transcript/        # a whole transcript tree
template-viewer transcript.jsonl --output page.html
template-viewer transcript.jsonl --output page.html --open
```

PATH is a single `.jsonl` transcript file or a directory containing one or
more of them — for example a gbnf-experiment run's `transcript/` tree at
`packages/gbnf-experiment/data/<run>/transcript/**`. Directory input reads
every `.jsonl` beneath it, in sorted order, and renders the combined
conversation.

The page is printed to stdout unless `--output` is given. `--open` writes to
disk (defaulting to `./transcript.html` when no `--output` is given) and opens
it in the default browser.

## What it renders

A Claude Code session transcript is one JSON object per line. The viewer lays
out each record as a turn:

- **system** records (the `init` banner and others) as a metadata block.
- **user** turns as a prompt bubble, or as a stack of tool results when the
  turn only carries tool outputs.
- **assistant** turns with Markdown text, `tool_use` calls (name + input as
  highlighted JSON), and collapsible `thinking` blocks, plus per-message usage
  chips (model, in/out/cache tokens).
- **result** records as a summary line (cost, duration, turns).

A sticky header pins session metadata and rolling totals — input, cache-write,
cache-read, output tokens, and the count of distinct API calls. Code blocks
are syntax-highlighted with Pygments. The page is one file: inline CSS, no
external assets, so it opens from disk or drops onto a static host.

## Packages

Library entry points:

- `template_viewer.load_records(path)` — parse a file or directory into a
  list of record dicts.
- `template_viewer.render_html(records, *, title=None)` — render records into
  an HTML string.
- `template_viewer.render_transcript(path, *, title=None)` — load and render
  in one step.
