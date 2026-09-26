import { Color, type Colorize } from './colorize.js';
import { getParentStackId } from './getParentStackId.js';
import { isRange, isRuleChar, isRuleRef } from './typeGuards.js';
import type { GraphNode } from './graphNode.js';
import type { GraphPointer } from './graphPointer.js';

export const printGraphPointer = (
  pointer: GraphPointer,
  colorize: Colorize
): string => colorize(`*${getParentStackId(pointer, colorize)}`, Color.RED);

const getChar = (charCode: number): string => {
  const char = String.fromCodePoint(charCode);
  return char === '\n' ? '\\n' : char;
};

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
    parts.push(
      col('{', Color.BLUE),
      col(node.id, Color.GRAY),
      col('}', Color.BLUE)
    );
  }
  if (isRuleChar(rule)) {
    const rendered = rule.value
      .map((v) =>
        isRange(v)
          ? v.map((val) => col(String.fromCodePoint(val), Color.YELLOW)).join('')
          : getChar(v)
      )
      .join('');
    parts.push(
      col('[', Color.GRAY),
      col(rendered, Color.YELLOW),
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

  const segments = [
    parts.join(''),
    node.next
      ? node.next.print({ pointers, colorize: col, showPosition })
      : undefined,
  ];
  return segments.filter(Boolean).join(col('-> ', Color.GRAY));
};
