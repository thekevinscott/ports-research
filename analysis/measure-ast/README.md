# measure-ast

Tree-sitter AST metrics over one python or typescript source tree, alone or relative to a reference tree.

## Usage

```
measure-ast --language python|typescript --target <dir> [--exclude PATTERN ...]
measure-ast compare --language python|typescript --port <dir> --reference <dir> [--exclude PATTERN ...]
```

Walks each directory recursively. `python` parses `*.py`; `typescript` parses `*.ts` with the typescript grammar and `*.tsx` with the tsx grammar. Each `--exclude` is an fnmatch pattern applied to the path relative to the directory and to each of its path parts; a file is skipped when any candidate matches any pattern. `compare` applies the same patterns to both sides.

Prints one JSON object to stdout and exits 0. Exits non-zero with a message on stderr when a directory does not exist or no file was parsed. A file tree-sitter cannot parse cleanly still counts: tree-sitter always returns a tree.

`just reference-measures` clones the pinned gbnf commit, applies the gbnf-prepare patches, and prints the one-tree measures of `packages/gbnf/python` and `packages/gbnf/javascript` under the notebook's exclude lists, one JSON line each.

## Fields

- `language`, `target`: as given; `target` resolved to an absolute path.
- `parsed_file_count`: files parsed.
- `node_count`: named nodes across all parsed files.
- `max_depth`: deepest named-node depth across files, root = 0.
- `function_count`: function-like nodes, nested ones included. python: `function_definition`. typescript: `function_declaration`, `method_definition`, `arrow_function`, `function_expression`, `generator_function_declaration`.
- `mean_function_lines`, `max_function_lines`: per function, end row minus start row plus 1.
- `mean_cyclomatic`, `max_cyclomatic`: per function, 1 plus the branch nodes in its subtree, excluding the subtrees of nested functions. python branches: `if_statement`, `elif_clause`, `for_statement`, `while_statement`, `except_clause`, `case_clause`, `conditional_expression`, `boolean_operator`, comprehension `if_clause`. typescript branches: `if_statement`, `for_statement`, `for_in_statement`, `while_statement`, `do_statement`, `switch_case`, `catch_clause`, `ternary_expression`, and `binary_expression` whose operator is `&&`, `||` or `??`.

Means are over functions. With no functions, the means and maxes are 0.

## Compare fields

Every `compare` number measures structural drift from the reference, not fidelity.

- `language`, `port`, `reference`: as given; both directories resolved to absolute paths.
- `delta`: per one-tree field above, `{delta, port, reference}`, `delta` being port minus reference.
- `functions`: named functions paired across sides by normalised name and arity. A name normalises by dropping leading `_` and `#`, dropping every other `_`, and lowercasing, so `parse_rule`, `_parseRule` and `#parseRule` agree. A function's name is its own, else the variable, field, object key or assigned property it is bound to; callbacks have none and are not paired. Arity counts declared parameters, `self` included, separators and comments not. Functions sharing a key pair in source order.
  - `matched_count`, `port_only_count`, `reference_only_count`.
  - `matched`: per pair, `port` and `reference` as `name/arity`, `port_lines`, `reference_lines`, `tree_edit_distance`, and `normalised` = distance over the larger tree's node count.
  - `port_only`, `reference_only`: sorted `name/arity`.
  - `matched_fraction`: matched over the reference's named functions; null when it has none.
  - `median_line_drift`: median over pairs of port lines minus reference lines; null with no pairs.
- `tree_edit_distance`: `mean_normalised`, `median_normalised` over pairs; null with no pairs. The distance is Zhang-Shasha with unit insert, delete and relabel costs, over each function's named-node subtree labelled by node type alone: identifiers and literals abstracted to their type, a literal collapsed to one leaf, comments dropped. Renaming is free; structure is what counts.
- `branching`: `port` and `reference`, every function's cyclomatic number sorted, callbacks included; `wasserstein`, the Wasserstein-1 distance between the two distributions, null when a side has no functions.
- `api_surface`: `shared`, `port_only`, `reference_only`, sorted entries `name/arity`, or a bare `name` when the arity is unknown. python: top-level `def` and `class` not starting with `_` in every file, plus every name in a top-level `__all__`; a class's arity is its `__init__`'s without `self`, else a dataclass's annotated fields, else 0. typescript: every `export` declaration in every file (functions and function-valued constants with arity, classes with constructor arity, other constants, types, interfaces and enums bare), `export { a as b }` under `b` with `a`'s arity resolved by name across files, and the default export as `default` plus, for an object literal or class, its public members as `default.<member>`. `export *` is not followed.
- `call_paths`: each side's call graph walked from the shared public API, after Sean Goedecke's [How to read code](https://www.seangoedecke.com/how-to-read-code/): start at an entry point, follow the calls, treat everything outside the package as a black box.
  - Graph: one node per named function (as in `functions`; callbacks are not nodes). A method is named `Class.method` after the class whose body declares it, and its key is both parts normalised. An edge runs from f to g when f contains a call whose callee resolves to g; calls inside f's anonymous callbacks count as f's, calls inside a named function nested in f count as that function's.
  - What resolves: a bare call `g(...)` to every non-method function whose normalised name is `g`, and to the constructor (`__init__`, `constructor`) of a class named `g`; a call through any object `x.g(...)`, `self.g(...)`, `this.g(...)` to every function or method normalised `g` and every class constructor named `g`, by name only, whatever `x` is; `new G(...)` to `G`'s constructor. The argument count must fit: at least the required parameters, at most the declared ones (unbounded with `*args`, `**kwargs` or `...rest`), a python method's `self` or `cls` not counted, a `@staticmethod`'s first parameter counted. A call with a spread, splat or keyword argument fits any arity.
  - What does not resolve: names defined outside the package (dropped), calls through `super`, a function passed as a value (`map(g, xs)`), a class with no constructor, property reads, operators and other implicit protocol calls (`__eq__`, `__iter__`, `[Symbol.iterator]`), and a call whose callee is itself an expression (`f(a)(b)`). A method call on a builtin (`seen.add(x)`) resolves to every package function named `add` that fits.
  - Entry points: each `api_surface.shared` entry that names, on a side, a non-method function of that name and arity (the entry point is the function) or a class (the entry points are its constructor and its public methods, as `Class.method`; python: not starting with `_`; typescript: not `#` and not `private` or `protected`). Constants, types, `default` and `default.<member>` are not entry points. Entry points are unioned over both sides by key, named as on the reference; a side lacking one has an empty trace for it.
  - Trace order: depth-first preorder from the entry point, the entry point first; a function's callees in the order their call sites start in its source, a call resolving to several functions in definition order; each function visited once.
  - `entry_points`, one per entry point: `entry_point`; `reference_trace`, `port_trace`, the traced functions' names; `trace_edit_distance`, Levenshtein over the two traces' keys; `trace_normalised`, that over the longer trace's length; `reference_edges`, `port_edges`, distinct edges out of the traced functions, by keys; `edge_recall`, shared over reference edges, null with none; `edge_precision`, shared over port edges, null with none; `missing_edges`, reference edges absent from the port, and `extra_edges`, port edges absent from the reference, as `caller->callee` in trace order; `reachable_reference`, `reachable_port`, the trace lengths.
  - `entry_point_count`; `mean_edge_recall` over entry points with a recall, null with none; `median_trace_normalised`, null with no entry points; `reachable_fraction_reference`, `reachable_fraction_port`, functions reachable from any entry point over all functions on that side, null with none; `unreachable_port_only`, sorted `name/arity` of port functions reachable from no entry point.
  - `explainer`: one sentence per entry point, fixed template: `parse: reference trace of 5 (a, b, c, d, e); port 4, missing c->d, extra b->x`, `none` when a list is empty.
