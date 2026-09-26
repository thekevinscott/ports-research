import { Color } from './colorize';
import type { Colorize } from './colorize';
import { getParentStackId } from './getParentStackId';
import type { GraphNode } from './graphNode';
import type { GraphPointer } from './graphPointer';
import { isRange, isRuleChar, isRuleRef } from './typeGuards';

export const printGraphPointer = (
  pointer: GraphPointer,
  colorizeFn: Colorize,
): string =>
  colorizeFn(`*${getParentStackId(pointer, colorizeFn)}`, Color.RED);

export const printGraphNode = (
  node: GraphNode,
  col: Colorize,
  pointers?: Iterable<GraphPointer>,
  showPosition = false,
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
    const rendered = rule.value
      .map((v) =>
        isRange(v)
          ? v.map((val) => col(String.fromCodePoint(val), Color.YELLOW)).join('')
          : getChar(v),
      )
      .join('');
    parts.push(
      col('[', Color.GRAY),
      col(rendered, Color.YELLOW),
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
        pointerParts.push(printGraphPointer(pointer, col));
      }
      if (pointerParts.length) {
        parts.push(col('[', Color.GRAY), ...pointerParts, col(']', Color.GRAY));
      }
    }
  }

  const renderedNext = node.next
    ? node.next.print(col, pointers, showPosition)
    : '';
  return [parts.join(''), renderedNext]
    .filter((part) => !!part)
    .join(col('-> ', Color.GRAY));
};

const getChar = (charCode: number): string => {
  const char = String.fromCodePoint(charCode);
  if (char === '\n') {
    return '\\n';
  }
  return char;
};
