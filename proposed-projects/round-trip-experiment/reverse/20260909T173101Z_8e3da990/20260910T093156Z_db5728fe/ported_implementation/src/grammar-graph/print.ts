import { Color, Colorize, colorize as defaultColorize } from './colorize.js';
import { getParentStackId } from './get-parent-stack-id.js';
import type { GraphNode } from './graph-node.js';
import type { GraphPointer } from './graph-pointer.js';
import { isRange, isRuleChar, isRuleRef } from './type-guards.js';

export const printGraphPointer = (
  pointer: GraphPointer,
  colorize: Colorize = defaultColorize,
): string => colorize(`*${getParentStackId(pointer, colorize)}`, Color.RED);

export const printGraphNode = (
  node: GraphNode,
  pointers?: Iterable<GraphPointer>,
  showPosition = false,
  colorize: Colorize = defaultColorize,
): string => {
  const col = colorize;
  // the chain of `next` nodes is walked iteratively; it is as long as the rule is.
  return [...iterateNodes(node)]
    .map(current => printSingleGraphNode(current, pointers, showPosition, col))
    .join(col('-> ', Color.GRAY));
};

function* iterateNodes(node: GraphNode | undefined): Generator<GraphNode> {
  while (node) {
    yield node;
    node = node.next;
  }
}

const printSingleGraphNode = (
  node: GraphNode,
  pointers: Iterable<GraphPointer> | undefined,
  showPosition: boolean,
  col: Colorize,
): string => {
  const { rule } = node;

  const parts: string[] = [];
  if (showPosition) {
    parts.push(
      col('{', Color.BLUE),
      col(node.id, Color.GRAY),
      col('}', Color.BLUE),
    );
  }
  if (isRuleChar(rule)) {
    parts.push(
      col('[', Color.GRAY),
      col(rule.value.map(value => (
        // a nested array joins with commas on its way into the string
        isRange(value)
          ? value.map(val => col(fromCharCode(val), Color.YELLOW)).join(',')
          : getChar(value)
      )).join(''), Color.YELLOW),
      col(']', Color.GRAY),
    );
  } else if (isRuleRef(rule)) {
    parts.push(col('Ref(', Color.GRAY) + col(`${rule.value}`, Color.GREEN) + col(')', Color.GRAY));
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
        parts.push(col('[', Color.GRAY));
        parts.push(...pointerParts);
        parts.push(col(']', Color.GRAY));
      }
    }
  }

  return parts.join('');
};

const fromCharCode = (charCode: number): string => String.fromCharCode(charCode);

const getChar = (charCode: number): string => {
  const char = fromCharCode(charCode);
  if (char === '\n') {
    return '\\n';
  }
  return char;
};
