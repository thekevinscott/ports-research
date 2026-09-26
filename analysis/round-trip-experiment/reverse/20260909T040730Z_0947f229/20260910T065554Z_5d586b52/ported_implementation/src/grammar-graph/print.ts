/** Port of `gbnf/grammar_graph/print.py`. */

import { Color, Colorize } from './colorize.js';
import { getParentStackId } from './get-parent-stack-id.js';
import { isRange, isRuleChar, isRuleRef } from './type-guards.js';
import type { GenericSet } from './generic-set.js';
import type { GraphNode } from './graph-node.js';
import type { GraphPointer } from './graph-pointer.js';

export type Pointers = GenericSet<GraphPointer, string>;

export const printGraphPointer = (pointer: GraphPointer, colorize: Colorize): string =>
  colorize(`*${getParentStackId(pointer, colorize)}`, Color.RED);

const getChar = (charCode: number): string => {
  const char = String.fromCodePoint(charCode);
  return char === '\n' ? '\\n' : char;
};

export const printGraphNode = (
  node: GraphNode,
  colorize: Colorize,
  pointers?: Pointers,
  showPosition = false,
): string => {
  const col = colorize;
  const rule = node.rule;

  const parts: string[] = [];
  if (showPosition) {
    parts.push(col('{', Color.BLUE), col(node.id, Color.GRAY), col('}', Color.BLUE));
  }
  if (isRuleChar(rule)) {
    const rendered = rule.value
      .map((v) =>
        isRange(v)
          ? v.map((val) => col(String.fromCodePoint(val), Color.YELLOW)).join('')
          : getChar(v),
      )
      .join('');
    parts.push(col('[', Color.GRAY), col(rendered, Color.YELLOW), col(']', Color.GRAY));
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
        parts.push(col('[', Color.GRAY));
        parts.push(...pointerParts);
        parts.push(col(']', Color.GRAY));
      }
    }
  }

  const rest =
    node.next !== undefined
      ? printGraphNode(node.next, col, pointers, showPosition)
      : undefined;
  return [parts.join(''), rest].filter(Boolean).join(col('-> ', Color.GRAY));
};
