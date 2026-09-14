import { Color, type Colorize } from './colorize.js';
import type { GenericSet } from './generic-set.js';
import { getParentStackId } from './get-parent-stack-id.js';
import type { GraphNode } from './graph-node.js';
import type { GraphPointer } from './graph-pointer.js';
import { isRange, isRuleChar, isRuleRef } from './type-guards.js';

export type Pointers = GenericSet<GraphPointer, string>;

export interface PrintNodeOpts {
  colorize: Colorize;
  pointers?: Pointers;
  showPosition?: boolean;
}

export const printGraphPointer =
  (pointer: GraphPointer) =>
  ({ colorize }: { colorize: Colorize }): string =>
    colorize(`*${getParentStackId(pointer, colorize)}`, Color.RED);

export const printGraphNode =
  (node: GraphNode) =>
  ({ colorize: col, pointers, showPosition = false }: PrintNodeOpts): string => {
    const rule = node.rule;

    const parts: string[] = [];
    if (showPosition) {
      parts.push(col('{', Color.BLUE), col(node.id, Color.GRAY), col('}', Color.BLUE));
    }
    if (isRuleChar(rule)) {
      parts.push(
        col('[', Color.GRAY),
        col(
          rule.value
            .map((v) =>
              // A nested array is stringified by `join('')` as its comma
              // separated members.
              isRange(v)
                ? v.map((val) => col(String.fromCodePoint(val), Color.YELLOW)).join(',')
                : getChar(v)
            )
            .join(''),
          Color.YELLOW
        ),
        col(']', Color.GRAY)
      );
    } else if (isRuleRef(rule)) {
      parts.push(
        col('Ref(', Color.GRAY) + col(`${rule.value}`, Color.GREEN) + col(')', Color.GRAY)
      );
    } else {
      parts.push(col(rule.type, Color.YELLOW));
    }

    if (pointers) {
      for (const pointer of pointers) {
        const pointerParts: string[] = [];
        if (pointer.node === node) {
          pointerParts.push(pointer.print({ colorize: col }));
        }
        if (pointerParts.length) {
          parts.push(col('[', Color.GRAY), ...pointerParts, col(']', Color.GRAY));
        }
      }
    }

    const rest = node.next
      ? node.next.print({ pointers, colorize: col, showPosition })
      : undefined;
    return [parts.join(''), rest].filter(Boolean).join(col('-> ', Color.GRAY));
  };

export const getChar = (charCode: number): string => {
  const char = String.fromCodePoint(charCode);
  if (char === '\n') {
    return '\\n';
  }
  return char;
};
