import { Color, type Colorize } from './colorize.js';
import { getParentStackId } from './get-parent-stack-id.js';
import type { GraphNode } from './graph-node.js';
import type { GraphPointer } from './graph-pointer.js';
import { isRange, isRuleChar, isRuleRef } from './type-guards.js';

export interface PrintNodeOpts {
  colorize: Colorize;
  pointers?: Iterable<GraphPointer>;
  showPosition?: boolean;
}

export const printGraphPointer =
  (pointer: GraphPointer) =>
  ({ colorize }: { colorize: Colorize }): string =>
    colorize(`*${getParentStackId(pointer, colorize)}`, Color.RED);

export const printGraphNode =
  (node: GraphNode) =>
  ({ colorize: col, pointers, showPosition = false }: PrintNodeOpts): string => {
    const rule = node.rule;

    const parts: (string | number)[] = [];
    if (showPosition) {
      parts.push(
        col('{', Color.BLUE),
        col(node.id, Color.GRAY),
        col('}', Color.BLUE)
      );
    }
    if (isRuleChar(rule)) {
      const values: string[] = [];
      for (const v of rule.value) {
        if (isRange(v)) {
          values.push(
            v.map((val) => col(String.fromCodePoint(val), Color.YELLOW)).join('')
          );
        } else {
          values.push(getChar(v as number));
        }
      }
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
          pointerParts.push(pointer.print({ colorize: col }));
        }
        if (pointerParts.length) {
          parts.push(col('[', Color.GRAY));
          parts.push(...pointerParts);
          parts.push(col(']', Color.GRAY));
        }
      }
    }

    const rendered = [parts.map((part) => `${part}`).join('')];
    if (node.next !== undefined) {
      rendered.push(
        node.next.print({ colorize: col, pointers, showPosition })
      );
    }
    return rendered.filter((part) => part).join(col('-> ', Color.GRAY));
  };

const getChar = (charCode: number): string => {
  const char = String.fromCodePoint(charCode);
  if (char === '\n') {
    return '\\n';
  }
  return char;
};
