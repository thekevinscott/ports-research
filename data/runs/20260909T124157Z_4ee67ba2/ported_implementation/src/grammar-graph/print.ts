import { Color } from './colorize.ts';
import type { PrintOpts } from './grammar-graph-types.ts';
import { getParentStackId } from './get-parent-stack-id.ts';
import { isRange, isRuleChar, isRuleRef } from './type-guards.ts';

/**
 * The printers are structural: they accept anything node- or pointer-shaped, which
 * keeps them usable with test doubles, as in the reference implementation.
 */
export interface PrintableNode {
  id: string | number;
  rule: unknown;
  next?: PrintableNode | null;
  print?: (opts: PrintOpts) => string;
}

export interface PrintablePointer {
  node: PrintableNode;
  parent?: unknown;
  print: (opts: PrintOpts) => string;
}

export const printGraphPointer =
  (pointer: PrintablePointer) =>
  (opts: PrintOpts): string => {
    const col = opts.colorize;
    return col(`*${getParentStackId(pointer as never, col)}`, Color.RED);
  };

export const printGraphNode =
  (node: PrintableNode) =>
  (opts: PrintOpts): string => {
    const pointers = opts.pointers;
    const col = opts.colorize;
    const showPosition = opts.show_position ?? false;
    const rule = node.rule;
    const parts: string[] = [];
    if (showPosition) {
      parts.push(col('{', Color.BLUE), col(node.id, Color.GRAY), col('}', Color.BLUE));
    }

    if (isRuleChar(rule)) {
      parts.push(
        col('[', Color.GRAY),
        col(
          rule.value
            .map(v =>
              isRange(v)
                ? v.map(val => col(getChar(val), Color.YELLOW)).join('')
                : getChar(v as number),
            )
            .join(''),
          Color.YELLOW,
        ),
        col(']', Color.GRAY),
      );
    } else if (isRuleRef(rule)) {
      parts.push(col('Ref(', Color.GRAY), col(rule.value, Color.GREEN), col(')', Color.GRAY));
    } else {
      parts.push(col((rule as { type: string }).type, Color.YELLOW));
    }

    if (pointers && pointers.size > 0) {
      for (const pointer of pointers) {
        const pointerParts: string[] = [];
        if ((pointer.node as unknown) === (node as unknown)) {
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

    const partsToReturn: string[] = [parts.join('')];
    if (node.next) {
      partsToReturn.push(node.next.print!(opts));
    }

    return partsToReturn.join(col('-> ', Color.GRAY));
  };

export const getChar = (charCode: number): string => {
  const char = String.fromCodePoint(charCode);
  if (char === '\n') {
    return '\\n';
  }
  return char;
};
