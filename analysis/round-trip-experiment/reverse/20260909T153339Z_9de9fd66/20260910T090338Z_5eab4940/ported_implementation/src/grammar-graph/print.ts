import { Color, colorize as defaultColorize, type Colorize } from './colorize.js';
import { getParentStackId } from './get-parent-stack-id.js';
import type { GenericSet } from './generic-set.js';
import type { GraphNode } from './graph-node.js';
import type { GraphPointer } from './graph-pointer.js';
import { isRange, isRuleChar, isRuleRef } from './type-guards.js';

export const printGraphPointer = (
  pointer: GraphPointer,
  colorize: Colorize = defaultColorize
): string => colorize(`*${getParentStackId(pointer, colorize)}`, Color.RED);

export const printGraphNode = (
  node: GraphNode,
  {
    pointers,
    showPosition = false,
    colorize: col = defaultColorize,
  }: {
    pointers?: GenericSet<GraphPointer, string>;
    showPosition?: boolean;
    colorize?: Colorize;
  } = {}
): string => {
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
    const values = rule.value.map((v) =>
      isRange(v)
        ? v.map((val) => col(String.fromCodePoint(val), Color.YELLOW)).join('')
        : getChar(v)
    );
    parts.push(
      col('[', Color.GRAY),
      col(values.join(''), Color.YELLOW),
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

  const nextPrinted = node.next
    ? node.next.print({ pointers, colorize: col, showPosition })
    : undefined;
  return [parts.join(''), nextPrinted]
    .filter((part): part is string => !!part)
    .join(col('-> ', Color.GRAY));
};

const getChar = (charCode: number): string => {
  const char = String.fromCodePoint(charCode);
  if (char === '\n') {
    return '\\n';
  }
  return char;
};
