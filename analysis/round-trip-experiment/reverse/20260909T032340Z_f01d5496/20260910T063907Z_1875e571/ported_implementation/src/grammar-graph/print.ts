import { Color, Colorize } from './colorize';
import { getParentStackId } from './get-parent-stack-id';
import { isRange, isRuleChar, isRuleRef } from './type-guards';
import type { GraphNode } from './graph-node';
import type { GraphPointer } from './graph-pointer';

export const printGraphPointer = (pointer: GraphPointer, col: Colorize): string =>
  col(`*${getParentStackId(pointer, col)}`, Color.RED);

export const printGraphNode = (
  node: GraphNode,
  col: Colorize,
  {
    pointers,
    showPosition = false,
  }: { pointers?: Iterable<GraphPointer>; showPosition?: boolean } = {},
): string => {
  const rule = node.rule;

  const parts: (string | number)[] = [];
  if (showPosition) {
    parts.push(col('{', Color.BLUE), col(node.id, Color.GRAY), col('}', Color.BLUE));
  }

  if (isRuleChar(rule)) {
    const rendered = rule.value
      .map((v) =>
        isRange(v)
          ? v.map((val) => col(String.fromCodePoint(val), Color.YELLOW)).join('')
          : getChar(v as number),
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
        pointerParts.push(pointer.print(col));
      }
      if (pointerParts.length) {
        parts.push(col('[', Color.GRAY));
        parts.push(...pointerParts);
        parts.push(col(']', Color.GRAY));
      }
    }
  }

  const renderedNext = node.next
    ? node.next.print({ pointers, colorize: col, showPosition })
    : undefined;

  return [parts.map((p) => `${p}`).join(''), renderedNext]
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
