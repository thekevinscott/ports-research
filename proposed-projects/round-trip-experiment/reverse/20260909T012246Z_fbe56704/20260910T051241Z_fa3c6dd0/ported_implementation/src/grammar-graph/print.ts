import { Color } from './colorize.ts';
import type { Colorize } from './colorize.ts';
import type { GenericSet } from './generic-set.ts';
import { getParentStackId } from './get-parent-stack-id.ts';
import type { GraphNode } from './graph-node.ts';
import type { GraphPointer } from './graph-pointer.ts';
import { isRange, isRuleChar, isRuleRef } from './type-guards.ts';

export type Pointers = GenericSet<GraphPointer, string>;

export const printGraphPointer = (pointer: GraphPointer, colorize: Colorize): string =>
  colorize(`*${getParentStackId(pointer, colorize)}`, Color.RED);

export const printGraphNode = (
  node: GraphNode,
  colorize: Colorize,
  pointers?: Pointers,
  showPosition = false
): string => {
  const rule = node.rule;

  const parts: string[] = [];
  if (showPosition) {
    parts.push(
      colorize('{', Color.BLUE),
      colorize(node.id, Color.GRAY),
      colorize('}', Color.BLUE)
    );
  }
  if (isRuleChar(rule)) {
    parts.push(
      colorize('[', Color.GRAY),
      colorize(
        rule.value
          .map((v) =>
            // a range prints its bounds comma separated, matching the way a nested
            // array is stringified
            isRange(v)
              ? v.map((val) => colorize(String.fromCodePoint(val), Color.YELLOW)).join(',')
              : getChar(v)
          )
          .join(''),
        Color.YELLOW
      ),
      colorize(']', Color.GRAY)
    );
  } else if (isRuleRef(rule)) {
    parts.push(
      colorize('Ref(', Color.GRAY) +
        colorize(`${rule.value}`, Color.GREEN) +
        colorize(')', Color.GRAY)
    );
  } else {
    parts.push(colorize(rule.type, Color.YELLOW));
  }

  if (pointers) {
    for (const pointer of pointers) {
      const pointerParts: string[] = [];
      if (pointer.node === node) {
        pointerParts.push(pointer.print(colorize));
      }
      if (pointerParts.length) {
        parts.push(colorize('[', Color.GRAY));
        parts.push(...pointerParts);
        parts.push(colorize(']', Color.GRAY));
      }
    }
  }

  return [
    parts.join(''),
    node.next ? printGraphNode(node.next, colorize, pointers, showPosition) : undefined,
  ]
    .filter((part): part is string => !!part)
    .join(colorize('-> ', Color.GRAY));
};

export const getChar = (charCode: number): string => {
  const char = String.fromCodePoint(charCode);
  if (char === '\n') {
    return '\\n';
  }
  return char;
};
