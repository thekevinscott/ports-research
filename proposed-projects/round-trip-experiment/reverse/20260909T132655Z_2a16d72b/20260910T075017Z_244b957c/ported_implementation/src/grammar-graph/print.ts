import { Color, Colorize } from './colorize.js';
import { getParentStackId } from './get-parent-stack-id.js';
import { isRange, isRuleChar, isRuleRef } from './type-guards.js';
import type { GenericSet } from './generic-set.js';
import type { GraphNode } from './graph-node.js';
import type { GraphPointer } from './graph-pointer.js';

export const printGraphPointer = (
  pointer: GraphPointer,
  colorize: Colorize
): string => {
  const col = colorize;
  return col(`*${getParentStackId(pointer, col)}`, Color.RED);
};

const getChar = (charCode: number): string => {
  const char = String.fromCodePoint(charCode);
  if (char === '\n') {
    return '\\n';
  }
  return char;
};

export const printGraphNode = (
  node: GraphNode,
  colorize: Colorize,
  pointers?: GenericSet<GraphPointer, string>,
  showPosition = false
): string => {
  const col = colorize;
  const rule = node.rule;

  const parts: string[] = [];
  if (showPosition) {
    parts.push(
      col('{', Color.BLUE),
      col(node.id, Color.GRAY),
      col('}', Color.BLUE)
    );
  }

  if (isRuleChar(rule)) {
    const rendered = rule.value.map((v) =>
      isRange(v)
        ? v.map((val) => col(String.fromCodePoint(val), Color.YELLOW)).join('')
        : getChar(v as number)
    );
    parts.push(
      col('[', Color.GRAY),
      col(rendered.join(''), Color.YELLOW),
      col(']', Color.GRAY)
    );
  } else if (isRuleRef(rule)) {
    parts.push(
      col('Ref(', Color.GRAY) +
        col(`${rule.value}`, Color.GREEN) +
        col(')', Color.GRAY)
    );
  } else {
    parts.push(col(rule.type, Color.YELLOW));
  }

  if (pointers && pointers.size > 0) {
    for (const pointer of pointers) {
      const pointerParts: string[] = [];
      if (pointer.node === node) {
        pointerParts.push(pointer.print(col));
      }
      if (pointerParts.length > 0) {
        parts.push(col('[', Color.GRAY));
        parts.push(...pointerParts);
        parts.push(col(']', Color.GRAY));
      }
    }
  }

  const pieces = [parts.join('')];
  if (node.next !== undefined && node.next !== null) {
    const renderedNext = node.next.print(pointers, showPosition, col);
    if (renderedNext) {
      pieces.push(renderedNext);
    }
  }
  return pieces.join(col('-> ', Color.GRAY));
};
