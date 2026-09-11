import { Color, Colorize, colorize as defaultColorize } from './colorize';
import { getParentStackId } from './get-parent-stack-id';
import type { GraphNode } from './graph-node';
import type { GraphPointer } from './graph-pointer';
import { isRange, isRuleChar, isRuleRef } from './type-guards';

import type { Pointers } from './types';

export interface PrintOpts {
  pointers?: Pointers;
  showPosition?: boolean;
  colorize?: Colorize;
}

export const printGraphPointer =
  (pointer: GraphPointer) =>
  ({ colorize = defaultColorize }: PrintOpts = {}): string =>
    colorize(`*${getParentStackId(pointer, colorize)}`, Color.RED);

export const printGraphNode =
  (node: GraphNode) =>
  ({ pointers, showPosition = false, colorize: col = defaultColorize }: PrintOpts = {}): string => {
    const rule = node.rule;

    const parts: string[] = [];
    if (showPosition) {
      parts.push(col('{', Color.BLUE), col(node.id, Color.GRAY), col('}', Color.BLUE));
    }

    if (isRuleChar(rule)) {
      const values: string[] = [];
      for (const value of rule.value) {
        if (isRange(value)) {
          values.push(value.map((val) => col(String.fromCharCode(val), Color.YELLOW)).join(','));
        } else {
          values.push(getChar(value));
        }
      }
      parts.push(
        col('[', Color.GRAY),
        col(values.join(''), Color.YELLOW),
        col(']', Color.GRAY)
      );
    } else if (isRuleRef(rule)) {
      parts.push(
        col('Ref(', Color.GRAY) + col(`${rule.value}`, Color.GREEN) + col(')', Color.GRAY)
      );
    } else {
      parts.push(col(rule.type, Color.YELLOW));
    }

    if (pointers !== undefined) {
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

    const nextView =
      node.next !== undefined
        ? node.next.print({ pointers, colorize: col, showPosition })
        : undefined;

    return [parts.join(''), nextView]
      .filter((part): part is string => Boolean(part))
      .join(col('-> ', Color.GRAY));
  };

export const getChar = (charCode: number): string => {
  const char = String.fromCharCode(charCode);
  if (char === '\n') {
    return '\\n';
  }
  return char;
};
