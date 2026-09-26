import { Color, Colorize, colorize as defaultColorize } from './colorize';
import { getParentStackId } from './get-parent-stack-id';
import { isRange, isRuleChar, isRuleRef } from './type-guards';
import type { GraphNode } from './graph-node';
import type { GraphPointer } from './graph-pointer';

export const printGraphPointer = (
  pointer: GraphPointer,
  colorize: Colorize = defaultColorize
): string =>
  colorize(`*${getParentStackId(pointer, colorize)}`, Color.RED);

const getChar = (charCode: number): string => {
  const char = String.fromCodePoint(charCode);
  if (char === '\n') {
    return '\\n';
  }
  return char;
};

export const printGraphNode = (
  node: GraphNode,
  {
    pointers,
    showPosition = false,
    colorize = defaultColorize,
  }: {
    pointers?: Iterable<GraphPointer>;
    showPosition?: boolean;
    colorize?: Colorize;
  } = {}
): string => {
  const col = colorize;
  const { rule } = node;

  const parts: (string | number)[] = [];
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
        pointerParts.push(pointer.print({ colorize: col }));
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
  return [parts.map((p) => `${p}`).join(''), nextPrinted]
    .filter(Boolean)
    .join(col('-> ', Color.GRAY));
};
