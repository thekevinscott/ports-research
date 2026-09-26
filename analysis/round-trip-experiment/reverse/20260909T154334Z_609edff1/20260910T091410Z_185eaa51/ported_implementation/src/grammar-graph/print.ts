import { Color, Colorize, colorize as defaultColorize } from './colorize';
import { getParentStackId } from './get-parent-stack-id';
import type { GraphNode } from './graph-node';
import type { GraphPointer } from './graph-pointer';
import { isRange, isRuleChar, isRuleRef } from './type-guards';

export const printGraphPointer = (
  pointer: GraphPointer,
  colorize: Colorize = defaultColorize,
): string => colorize(`*${getParentStackId(pointer, colorize)}`, Color.RED);

export interface PrintOpts {
  pointers?: Iterable<GraphPointer>;
  showPosition?: boolean;
  colorize?: Colorize;
}

export const printGraphNode = (
  node: GraphNode,
  { pointers, showPosition = false, colorize: col = defaultColorize }: PrintOpts = {},
): string => {
  const rule = node.rule;

  const parts: string[] = [];
  if (showPosition) {
    parts.push(col('{', Color.BLUE), col(node.id, Color.GRAY), col('}', Color.BLUE));
  }
  if (isRuleChar(rule)) {
    const printedValues = rule.value.map(v =>
      isRange(v)
        ? v.map(val => col(String.fromCodePoint(val), Color.YELLOW)).join('')
        : getChar(v),
    );
    parts.push(
      col('[', Color.GRAY),
      col(printedValues.join(''), Color.YELLOW),
      col(']', Color.GRAY),
    );
  } else if (isRuleRef(rule)) {
    parts.push(
      col('Ref(', Color.GRAY) + col(`${rule.value}`, Color.GREEN) + col(')', Color.GRAY),
    );
  } else {
    parts.push(col(rule.type, Color.YELLOW));
  }

  if (pointers !== undefined) {
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

  const nextPrinted =
    node.next !== undefined
      ? node.next.print({ pointers, colorize: col, showPosition })
      : undefined;
  return [parts.join(''), nextPrinted]
    .filter((part): part is string => Boolean(part))
    .join(col('-> ', Color.GRAY));
};

const getChar = (charCode: number): string => {
  const char = String.fromCodePoint(charCode);
  if (char === '\n') {
    return '\\n';
  }
  return char;
};
