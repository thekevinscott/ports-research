import { Color, Colorize } from './colorize.js';
import { getParentStackId } from './get-parent-stack-id.js';
import type { GraphNode } from './graph-node.js';
import type { GraphPointer } from './graph-pointer.js';
import { isRange, isRuleChar, isRuleRef } from './type-guards.js';
import type { Pointers } from './types-internal.js';

export const printGraphPointer = (pointer: GraphPointer, col: Colorize): string =>
  col(`*${getParentStackId(pointer, col)}`, Color.RED);

const getChar = (charCode: number): string => {
  const char = String.fromCodePoint(charCode);
  return char === '\n' ? '\\n' : char;
};

export const printGraphNode = (
  node: GraphNode,
  { pointers, showPosition = false, col }: {
    pointers?: Pointers | GraphPointer[];
    showPosition?: boolean;
    col: Colorize;
  },
): string => {
  const rule = node.rule;

  const parts: (string | number)[] = [];
  if (showPosition) {
    parts.push(col('{', Color.BLUE), col(node.id, Color.GRAY), col('}', Color.BLUE));
  }
  if (isRuleChar(rule)) {
    const rendered = rule.value.map((v) => (
      isRange(v) ? v.map((val) => col(String.fromCodePoint(val), Color.YELLOW)).join('')
        : getChar(v)
    )).join('');
    parts.push(
      col('[', Color.GRAY),
      col(rendered, Color.YELLOW),
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
        pointerParts.push(printGraphPointer(pointer, col));
      }
      if (pointerParts.length) {
        parts.push(col('[', Color.GRAY), ...pointerParts, col(']', Color.GRAY));
      }
    }
  }

  const renderedParts = [parts.map((part) => `${part}`).join('')];
  if (node.next !== undefined) {
    renderedParts.push(printGraphNode(node.next, { pointers, showPosition, col }));
  }
  return renderedParts.filter(Boolean).join(col('-> ', Color.GRAY));
};
