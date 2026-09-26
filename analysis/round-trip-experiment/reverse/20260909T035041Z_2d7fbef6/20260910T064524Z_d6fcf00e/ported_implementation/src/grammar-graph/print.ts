import { Color, Colorize } from './colorize.js';
import { getParentStackId } from './get-parent-stack-id.js';
import type { GenericSet } from './generic-set.js';
import type { GraphNode } from './graph-node.js';
import type { GraphPointer } from './graph-pointer.js';
import { isRange, isRuleChar, isRuleRef } from './type-guards.js';

export const printGraphPointer = (pointer: GraphPointer, colorize: Colorize): string =>
  colorize(`*${getParentStackId(pointer, colorize)}`, Color.RED);

export const printGraphNode = (
  node: GraphNode,
  colorize: Colorize,
  pointers?: GenericSet<GraphPointer, string>,
  showPosition = false,
): string => {
  const col = colorize;
  const { rule } = node;

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
            // a range renders as an array in JS, which `join` stringifies with commas
            isRange(v)
              ? v.map((val) => col(String.fromCharCode(val), Color.YELLOW)).join(',')
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

  if (pointers) {
    for (const pointer of pointers) {
      const pointerParts: string[] = [];
      if (pointer.node === node) {
        pointerParts.push(pointer.print(col));
      }
      if (pointerParts.length) {
        parts.push(col('[', Color.GRAY), ...pointerParts, col(']', Color.GRAY));
      }
    }
  }

  const rest = node.next ? node.next.print(col, pointers, showPosition) : undefined;
  return [parts.join(''), rest].filter(Boolean).join(col('-> ', Color.GRAY));
};

const getChar = (charCode: number): string => {
  const char = String.fromCharCode(charCode);
  if (char === '\n') {
    return '\\n';
  }
  return char;
};
