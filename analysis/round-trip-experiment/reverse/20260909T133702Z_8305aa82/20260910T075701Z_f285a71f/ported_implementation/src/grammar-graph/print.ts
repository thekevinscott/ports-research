import { Color, Colorize } from './colorize.js';
import { getParentStackId } from './get-parent-stack-id.js';
import type { GraphNode } from './graph-node.js';
import type { GraphPointer } from './graph-pointer.js';
import { isRange, isRuleChar, isRuleRef } from './type-guards.js';

export const printGraphPointer = (
  pointer: GraphPointer,
  colorize: Colorize,
): string =>
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
  },
): string => {
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
    const rendered: string[] = [];
    for (const v of rule.value) {
      if (isRange(v)) {
        rendered.push(
          v.map((val) => col(String.fromCodePoint(val), Color.YELLOW)).join(','),
        );
      } else {
        rendered.push(getChar(v));
      }
    }
    parts.push(
      col('[', Color.GRAY),
      col(rendered.join(''), Color.YELLOW),
      col(']', Color.GRAY),
    );
  } else if (isRuleRef(rule)) {
    parts.push(
      col('Ref(', Color.GRAY) +
        col(`${rule.value}`, Color.GREEN) +
        col(')', Color.GRAY),
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

  const renderedParts: string[] = [parts.join('')];
  if (node.next !== undefined) {
    renderedParts.push(
      node.next.print({ pointers, colorize: col, showPosition }),
    );
  }
  return renderedParts.filter((part) => part).join(col('-> ', Color.GRAY));
};

const getChar = (charCode: number): string => {
  const char = String.fromCodePoint(charCode);
  if (char === '\n') {
    return '\\n';
  }
  return char;
};
