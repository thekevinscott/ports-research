/**
 * Compatibility aliases.
 *
 * The port renames the reference implementation's `snake_case` functions to `camelCase`,
 * which is what the rest of this package uses. These aliases let code written against the
 * Python names keep working:
 *
 * ```ts
 * import { is_word_char, isWordChar } from "gbnf"; // the same function
 * ```
 */
export { getInputAsCodePoints as get_input_as_code_points } from "./grammar-graph/get-input-as-code-points.ts";
export { getCodePoint as get_code_point } from "./grammar-graph/get-input-as-code-points.ts";
export { getParentStackId as get_parent_stack_id } from "./grammar-graph/get-parent-stack-id.ts";
export { getSerializedRuleKey as get_serialized_rule_key } from "./grammar-graph/get-serialized-rule-key.ts";
export { getChar as get_char } from "./grammar-graph/print.ts";
export { printGraphNode as print_graph_node } from "./grammar-graph/print.ts";
export { printGraphPointer as print_graph_pointer } from "./grammar-graph/print.ts";
export {
  isGraphPointerRuleChar as is_graph_pointer_rule_char,
  isGraphPointerRuleCharExclude as is_graph_pointer_rule_char_exclude,
  isGraphPointerRuleEnd as is_graph_pointer_rule_end,
  isGraphPointerRuleRef as is_graph_pointer_rule_ref,
  isRange as is_range,
  isRule as is_rule,
  isRuleChar as is_rule_char,
  isRuleCharExclude as is_rule_char_exclude,
  isRuleEnd as is_rule_end,
  isRuleRef as is_rule_ref,
} from "./grammar-graph/type-guards.ts";
export { buildRuleStack as build_rule_stack } from "./grammar-parser/build-rule-stack.ts";
export { makeCharRule as make_char_rule } from "./grammar-parser/build-rule-stack.ts";
export { isWordChar as is_word_char } from "./rules-builder/is-word-char.ts";
export { parseChar as parse_char } from "./rules-builder/parse-char.ts";
export { parseName as parse_name } from "./rules-builder/parse-name.ts";
export { parseSpace as parse_space } from "./rules-builder/parse-space.ts";
export { getOutElements as get_out_elements } from "./rules-builder/rules-builder.ts";
export {
  isRuleDefAlt as is_rule_def_alt,
  isRuleDefChar as is_rule_def_char,
  isRuleDefCharAlt as is_rule_def_char_alt,
  isRuleDefCharNot as is_rule_def_char_not,
  isRuleDefCharRngUpper as is_rule_def_char_rng_upper,
  isRuleDefEnd as is_rule_def_end,
  isRuleDefRef as is_rule_def_ref,
} from "./rules-builder/rules-builder-types.ts";
export { buildErrorPosition as build_error_position } from "./utils/errors/build-error-position.ts";
export { getInputAsString as get_input_as_string } from "./utils/errors/get-input-as-string.ts";
export { isPointInRange as is_point_in_range } from "./utils/is-point-in-range.ts";
export { validateNonEmpty as validate_non_empty } from "./utils/validate-non-empty.ts";
