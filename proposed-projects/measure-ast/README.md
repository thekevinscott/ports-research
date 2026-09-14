# measure-ast

Tree-sitter AST metrics over one python or typescript source tree.

## Usage

```
measure-ast --language python|typescript --target <dir> [--exclude PATTERN ...]
```

Walks `<dir>` recursively. `python` parses `*.py`; `typescript` parses `*.ts`
with the typescript grammar and `*.tsx` with the tsx grammar. Each `--exclude`
is an fnmatch pattern applied to the path relative to `<dir>` and to each of
its path parts; a file is skipped when any candidate matches any pattern.

Prints one JSON object to stdout and exits 0. Exits non-zero with a message on
stderr when `<dir>` does not exist or no file was parsed. A file tree-sitter
cannot parse cleanly still counts: tree-sitter always returns a tree.

## Fields

- `language`, `target`: as given; `target` resolved to an absolute path.
- `parsed_file_count`: files parsed.
- `node_count`: named nodes across all parsed files.
- `max_depth`: deepest named-node depth across files, root = 0.
- `function_count`: function-like nodes, nested ones included. python:
  `function_definition`. typescript: `function_declaration`,
  `method_definition`, `arrow_function`, `function_expression`,
  `generator_function_declaration`.
- `mean_function_lines`, `max_function_lines`: per function, end row minus
  start row plus 1.
- `mean_cyclomatic`, `max_cyclomatic`: per function, 1 plus the branch nodes
  in its subtree, excluding the subtrees of nested functions. python branches:
  `if_statement`, `elif_clause`, `for_statement`, `while_statement`,
  `except_clause`, `case_clause`, `conditional_expression`,
  `boolean_operator`, comprehension `if_clause`. typescript branches:
  `if_statement`, `for_statement`, `for_in_statement`, `while_statement`,
  `do_statement`, `switch_case`, `catch_clause`, `ternary_expression`, and
  `binary_expression` whose operator is `&&`, `||` or `??`.

Means are over functions. With no functions, the means and maxes are 0.
