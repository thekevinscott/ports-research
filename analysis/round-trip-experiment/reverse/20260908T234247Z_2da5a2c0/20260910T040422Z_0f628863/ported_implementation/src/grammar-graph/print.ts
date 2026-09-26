import { Color, type Colorize } from './colorize.ts';
import { getParentStackId } from './get-parent-stack-id.ts';
import type { GraphNode } from './graph-node.ts';
import type { GraphPointer } from './graph-pointer.ts';
import { isRange, isRuleChar, isRuleRef } from './type-guards.ts';

export const printGraphPointer = (pointer: GraphPointer, colorize: Colorize): string =>
  colorize(`*${getParentStackId(pointer, colorize)}`, Color.RED);

export const printGraphNode = (
  node: GraphNode,
  {
    pointers,
    showPosition = false,
    colorize: col,
  }: {
    pointers?: Iterable<GraphPointer>;
    showPosition?: boolean;
    colorize: Colorize;
  }
): string => {
  const rule = node.rule;

  const parts: string[] = [];
  if (showPosition) {
    parts.push(col('{', Color.BLUE));
    parts.push(col(node.id, Color.GRAY));
    parts.push(col('}', Color.BLUE));
  }
  if (isRuleChar(rule)) {
    const values: string[] = [];
    for (const value of rule.value) {
      if (isRange(value)) {
        // The inner array stringifies with commas between its entries.
        values.push(value.map((val) => col(String.fromCodePoint(val), Color.YELLOW)).join(','));
      } else {
        values.push(getChar(value));
      }
    }
    parts.push(col('[', Color.GRAY));
    parts.push(col(values.join(''), Color.YELLOW));
    parts.push(col(']', Color.GRAY));
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
        parts.push(col('[', Color.GRAY));
        parts.push(...pointerParts);
        parts.push(col(']', Color.GRAY));
      }
    }
  }

  const nextPrinted =
    node.next !== undefined
      ? printGraphNode(node.next, { pointers, colorize: col, showPosition })
      : undefined;

  return [parts.join(''), nextPrinted].filter(Boolean).join(col('-> ', Color.GRAY));
};

const getChar = (charCode: number): string => {
  const char = String.fromCodePoint(charCode);
  if (char === '\n') {
    return '\\n';
  }
  return char;
};
