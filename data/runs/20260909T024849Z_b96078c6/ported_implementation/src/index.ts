export { GBNF, default } from "./gbnf.ts";

// errors
export {
  GrammarParseError,
  GRAMMAR_PARSER_ERROR_HEADER_MESSAGE,
} from "./utils/errors/grammar-parse-error.ts";
export {
  InputParseError,
  INPUT_PARSER_ERROR_HEADER_MESSAGE,
} from "./utils/errors/input-parse-error.ts";
export {
  buildErrorPosition,
  MAXIMUM_NUMBER_OF_ERROR_LINES_TO_SHOW,
} from "./utils/errors/build-error-position.ts";
export { getInputAsString } from "./utils/errors/get-input-as-string.ts";

// utils
export { isPointInRange } from "./utils/is-point-in-range.ts";
export { validateNonEmpty } from "./utils/validate-non-empty.ts";
export { asCodePoints, codePointLength, toCodePoints } from "./utils/code-points.ts";

// rules builder
export { RulesBuilder, getOutElements } from "./rules-builder/rules-builder.ts";
export { SymbolIds } from "./rules-builder/symbol-ids.ts";
export { isWordChar } from "./rules-builder/is-word-char.ts";
export { parseChar } from "./rules-builder/parse-char.ts";
export { parseName, PARSE_NAME_ERROR, VALID_NAME_SEPARATORS } from "./rules-builder/parse-name.ts";
export { parseSpace } from "./rules-builder/parse-space.ts";
export * from "./rules-builder/rules-builder-types.ts";

// grammar parser
export { buildRuleStack, makeCharRule } from "./grammar-parser/build-rule-stack.ts";

// grammar graph
export { Color, colorize } from "./grammar-graph/colorize.ts";
export { getInputAsCodePoints, getCodePoint } from "./grammar-graph/get-input-as-code-points.ts";
export { getParentStackId } from "./grammar-graph/get-parent-stack-id.ts";
export {
  getSerializedRuleKey,
  KEY_TRANSLATION,
} from "./grammar-graph/get-serialized-rule-key.ts";
export {
  Rule,
  RuleChar,
  RuleCharExclude,
  RuleEnd,
  RuleWithValue,
  RuleWithListOfIntsOrRanges,
} from "./grammar-graph/grammar-graph-types.ts";
export type {
  PrintOpts,
  Range,
  ResolvedGraphPointer,
  ResolvedRule,
  RuleCharValue,
  UnresolvedRule,
  ValidInput,
} from "./grammar-graph/grammar-graph-types.ts";
export { Graph } from "./grammar-graph/graph.ts";
export type { RootNode } from "./grammar-graph/graph.ts";
export { GraphNode } from "./grammar-graph/graph-node.ts";
export type { GraphNodeMeta, GraphNodeRuleRef } from "./grammar-graph/graph-node.ts";
export { GraphPointer } from "./grammar-graph/graph-pointer.ts";
export type { GraphPointerKey } from "./grammar-graph/graph-pointer.ts";
export { ParseState } from "./grammar-graph/parse-state.ts";
export { Pointers } from "./grammar-graph/pointers.ts";
export { getChar, printGraphNode, printGraphPointer } from "./grammar-graph/print.ts";
export { RuleRef } from "./grammar-graph/rule-ref.ts";
export * from "./grammar-graph/type-guards.ts";

// snake_case aliases matching the reference implementation's names
export * from "./compat.ts";
