import { Color } from './colorize';
import { getParentStackId } from './get-parent-stack-id';
import type { PrintOpts } from './grammar-graph-types';
import type { GraphNode } from './graph-node';
import type { GraphPointer } from './graph-pointer';
import { isRange, isRuleChar, isRuleRef } from './type-guards';

export const getChar = (charCode: number): string => {
  const char = String.fromCodePoint(charCode);
  if (char === '\n') {
    return '\\n';
  }
  return char;
};

export const printGraphPointer = (pointer: GraphPointer) => (opts: PrintOpts): string => {
  const col = opts.colorize;
  return col(`*${getParentStackId(pointer, col)}`, Color.RED);
};

export const printGraphNode = (node: GraphNode) => (opts: PrintOpts): string => {
  const { pointers } = opts;
  const col = opts.colorize;
  const showPosition = opts.showPosition ?? false;
  const { rule } = node;
  const parts: string[] = [];
  if (showPosition) {
    parts.push(col('{', Color.BLUE), col(node.id, Color.GRAY), col('}', Color.BLUE));
  }

  if (isRuleChar(rule)) {
    parts.push(
      col('[', Color.GRAY),
      col(
        rule.value.map((v) => (
          isRange(v)
            ? v.map((val) => col(getChar(val), Color.YELLOW)).join('')
            : getChar(v)
        )).join(''),
        Color.YELLOW,
      ),
      col(']', Color.GRAY),
    );
  } else if (isRuleRef(rule)) {
    parts.push(
      col('Ref(', Color.GRAY),
      col(rule.value, Color.GREEN),
      col(')', Color.GRAY),
    );
  } else {
    parts.push(col(rule.type, Color.YELLOW));
  }

  if (pointers?.size) {
    for (const pointer of pointers) {
      const pointerParts: string[] = [];
      if (pointer.node === node) {
        pointerParts.push(pointer.print(opts));
      }

      if (pointerParts.length > 0) {
        parts.push(
          col('[', Color.GRAY),
          col(pointerParts.join(''), Color.YELLOW),
          col(']', Color.GRAY),
        );
      }
    }
  }

  const partsToReturn = [parts.join('')];
  if (node.next) {
    partsToReturn.push(node.next.print(opts));
  }

  return partsToReturn.join(col('-> ', Color.GRAY));
};
