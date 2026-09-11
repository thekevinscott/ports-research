import { AttributeError } from "../utils/python_compat.ts";
import { Color } from "./colorize.ts";
import { get_parent_stack_id } from "./get_parent_stack_id.ts";
import type { PrintableNode, PrintablePointer, PrintOpts, Range } from "./grammar_graph_types.ts";
import type { GraphPointer } from "./graph_pointer.ts";
import { is_range, is_rule_char, is_rule_ref } from "./type_guards.ts";

export const print_graph_pointer =
  (pointer: GraphPointer) =>
  (opts: PrintOpts): string => {
    const col = opts.colorize;
    return col(`*${get_parent_stack_id(pointer, col)}`, Color.RED);
  };

export const print_graph_node =
  (node: PrintableNode) =>
  (opts: PrintOpts): string => {
    const pointers = [...(opts.pointers ?? [])] as PrintablePointer[];
    const col = opts.colorize;
    const show_position = opts.show_position ?? false;
    const rule = node.rule;
    const parts: string[] = [];
    if (show_position) {
      parts.push(col("{", Color.BLUE), col(node.id, Color.GRAY), col("}", Color.BLUE));
    }

    if (is_rule_char(rule)) {
      parts.push(
        col("[", Color.GRAY),
        col(
          rule.value
            .map((v) =>
              is_range(v)
                ? (v as Range).map((val) => col(get_char(val), Color.YELLOW)).join("")
                : get_char(v as number),
            )
            .join(""),
          Color.YELLOW,
        ),
        col("]", Color.GRAY),
      );
    } else if (is_rule_ref(rule)) {
      parts.push(col("Ref(", Color.GRAY), col(rule.value, Color.GREEN), col(")", Color.GRAY));
    } else {
      // Faithful to the reference: `Rule` exposes `type` only through its
      // `__dict__` property, so this lookup raises for RuleEnd/RuleCharExclude.
      const type = (rule as { type?: unknown }).type;
      if (type === undefined) {
        throw new AttributeError(
          `'${rule.constructor.name}' object has no attribute 'type'`,
        );
      }
      parts.push(col(String(type), Color.YELLOW));
    }

    if (pointers.length > 0) {
      for (const pointer of pointers) {
        const pointer_parts: string[] = [];
        if (pointer.node === node) {
          pointer_parts.push(pointer.print(opts));
        }

        if (pointer_parts.length > 0) {
          parts.push(
            col("[", Color.GRAY),
            col(pointer_parts.join(""), Color.YELLOW),
            col("]", Color.GRAY),
          );
        }
      }
    }

    const parts_to_return = [parts.join("")];
    if (node.next) {
      parts_to_return.push(node.next.print(opts));
    }

    return parts_to_return.join(col("-> ", Color.GRAY));
  };

export const get_char = (char_code: number): string => {
  const char = String.fromCodePoint(char_code);
  if (char === "\n") {
    return "\\n";
  }
  return char;
};
