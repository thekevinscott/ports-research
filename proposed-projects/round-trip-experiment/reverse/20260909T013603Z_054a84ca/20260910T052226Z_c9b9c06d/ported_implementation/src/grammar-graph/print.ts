import { Color, type Colorize } from './colorize.js';
import { getParentStackId } from './get-parent-stack-id.js';
import type { GraphNode } from './graph-node.js';
import type { GraphPointer } from './graph-pointer.js';
import type { Pointers } from './types-pointers.js';
import { isRange, isRuleChar, isRuleRef } from './type-guards.js';

export const printGraphPointer = (pointer: GraphPointer, colorize: Colorize): string =>
  colorize(`*${getParentStackId(pointer, colorize)}`, Color.RED);

export const printGraphNode = (
  node: GraphNode,
  colorize: Colorize,
  pointers?: Pointers,
  showPosition = false,
): string => {
  const col = colorize;
  const rule = node.rule;

  const parts: (string | number)[] = [];
  if (showPosition) {
    parts.push(col('{', Color.BLUE), col(node.id, Color.GRAY), col('}', Color.BLUE));
  }
  if (isRuleChar(rule)) {
    parts.push(
      col('[', Color.GRAY),
      col(
        rule.value
          .map(v =>
            // A range stringifies as its comma-joined members, matching the
            // array-to-string coercion of the original implementation.
            isRange(v)
              ? v.map(val => col(String.fromCodePoint(val), Color.YELLOW)).join(',')
              : getChar(v),
          )
          .join(''),
        Color.YELLOW,
      ),
      col(']', Color.GRAY),
    );
  } else if (isRuleRef(rule)) {
    parts.push(
      col('Ref(', Color.GRAY) + col(`${rule.value}`, Color.GREEN) + col(')', Color.GRAY),
    );
  } else {
    parts.push(col(rule.type, Color.YELLOW));
  }

  if (pointers !== undefined && pointers.size > 0) {
    for (const pointer of pointers) {
      const pointerParts: string[] = [];
      if (pointer.node === node) {
        pointerParts.push(pointer.print(col));
      }
      if (pointerParts.length > 0) {
        parts.push(col('[', Color.GRAY), ...pointerParts, col(']', Color.GRAY));
      }
    }
  }

  const nextPrinted =
    node.next !== undefined ? node.next.print(col, pointers, showPosition) : undefined;

  return [parts.map(part => `${part}`).join(''), nextPrinted]
    .filter((part): part is string => Boolean(part))
    .join(col('-> ', Color.GRAY));
};

export const getChar = (charCode: number): string => {
  const char = String.fromCodePoint(charCode);
  if (char === '\n') {
    return '\\n';
  }
  return char;
};
