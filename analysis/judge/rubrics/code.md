# Code rubric

You are comparing two implementations of the same library in two languages. Side A is the reference. Side B is the implementation under review, measured against A.

Each side below is a concatenation of its source files, tests excluded. Each file starts with a header line `=== <side>: <relative path> ===`, and each line of the file is prefixed with its line number and `| `.

Answer every item. Each item takes one verdict from its fixed set, evidence, and a note.

- Evidence is a list of quotes, each with its side (`A` or `B`), file (the relative path from the header), lines (`12` or `12-30`), and the quoted text. Quote both sides wherever the item compares them.
- The note is one or two sentences saying why the verdict, in plain words.
- Language conventions are not differences. `snake_case` against `camelCase`, a module against a file of exports, an exception class against an error class: the same name and the same contract count as kept.

## 1. API parity: `api_parity`

The public surface of A: exported names, their signatures, and the behaviours A documents in its source (docstrings, comments, type annotations). Does B offer a counterpart for each?

- `complete`: every public name of A has a counterpart in B with a matching signature and the documented behaviour.
- `minor-gaps`: a few counterparts are missing or differ in signature or documented behaviour, none of them central to what the library does.
- `major-gaps`: central public names are missing, or their signatures or documented behaviours differ.

## 2. Structure: `structure`

Compare the file and module layout of the two sides, and the split of code into functions and classes.

- `kept`: B mirrors A's files and their contents one to one, allowing for the target language's naming and packaging conventions.
- `changed-idiomatic`: B's layout differs, and the differences follow the target language's usual practice (merged modules where the language groups them, a class where the language would use one).
- `changed-arbitrary`: B's layout differs in ways neither A nor the target language's practice explains.

## 3. Semantic divergences: `semantic_divergences`

Anything B does differently from A on some input: a different result, a different error, a different error position or message, a hang, a crash. Read the code paths on both sides; list each divergence with a concrete input, what A does with it, and what B does with it, in `divergences`. Quote the responsible lines on both sides in evidence.

- `none-found`: no input found on which the two sides differ.
- `edge-inputs-only`: they differ only on unusual inputs (malformed grammars, boundary characters, empty input) or only in error details.
- `ordinary-inputs`: they differ on inputs a normal user of the library would pass.

## 4. Idiom versus transliteration: `idiom`

Is B written the way the target language is usually written, or is it A's code carried over line by line in the target language's syntax?

- `idiomatic`: B reads as code written in its own language.
- `mixed`: some parts idiomatic, some carried over line by line.
- `transliterated`: B reproduces A's constructs line by line where the target language has its own way.

## 5. Dropped or added: `dropped_or_added`

Code present on one side with no counterpart on the other: a function, a class, an option, a branch, an error check, a feature. List each in evidence, quoting the side that has it.

- `neither`: nothing of substance is present on only one side.
- `dropped`: A has something B lacks.
- `added`: B has something A lacks.
- `both`: both of the above.

## 6. Fidelity score: `fidelity`

One score from 1 to 5 for how faithfully B reproduces A, with a note giving the reason.

- 5: An exact counterpart; every public behaviour of A is preserved in B.
- 4: A close counterpart; every public name is present and behaviour differs only on edge inputs or in error details.
- 3: The same library with gaps; core behaviour matches, but some public names or documented behaviours are missing or changed.
- 2: A partial counterpart; core behaviour diverges on ordinary inputs, or large parts of the public API are missing.
- 1: A different library; B does not do what A does.
