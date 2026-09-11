import { Color, noColor } from './colorize.js';
import type { Colorize } from './colorize.js';
import { getParentStackId } from './getParentStackId.js';
import type { GraphNode } from './graphNode.js';
import type { GraphPointer } from './graphPointer.js';
import { isRange, isRuleChar, isRuleRef } from './typeGuards.js';

export interface PrintOpts {
  pointers?: Iterable<GraphPointer>;
  showPosition?: boolean;
  colorize?: Colorize;
}

export const printGraphPointer = (pointer: GraphPointer, col: Colorize = noColor): string =>
  col(`*${getParentStackId(pointer, col)}`, Color.RED);

export const printGraphNode = (node: GraphNode, {
  pointers,
  showPosition = false,
  colorize: col = noColor,
}: PrintOpts = {}): string => {
  const rule = node.rule;

  const parts: string[] = [];
  if (showPosition) {
    parts.push(
      col('{', Color.BLUE),
      col(node.id, Color.GRAY),
      col('}', Color.BLUE),
    );
  }

  if (isRuleChar(rule)) {
    parts.push(
      col('[', Color.GRAY),
      col(rule.value.map(v => isRange(v)
        ? v.map(val => col(String.fromCodePoint(val), Color.YELLOW)).join('')
        : getChar(v as number)).join(''), Color.YELLOW),
      col(']', Color.GRAY),
    );
  } else if (isRuleRef(rule)) {
    parts.push(
      col('Ref(', Color.GRAY) + col(`${rule.value}`, Color.GREEN) + col(')', Color.GRAY),
    );
  } else {
    parts.push(col(`${rule.type}`, Color.YELLOW));
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
  return [parts.join(''), nextPrinted].filter(part => !!part).join(col('-> ', Color.GRAY));
};

const getChar = (charCode: number): string => {
  const char = String.fromCodePoint(charCode);
  if (char === '\n') {
    return '\\n';
  }
  return char;
};
