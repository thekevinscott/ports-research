import { Color } from './colorize.js';
import type { Colorize } from './grammar-graph-types.js';
import type { GraphPointer } from './graph-pointer.js';

export const getParentStackId = (pointer: GraphPointer, col: Colorize): string => {
  const stackIds: string[] = [];
  let parent: GraphPointer | undefined = pointer.parent;
  while (parent) {
    const { stackId, pathId, stepId } = parent.node.meta;
    stackIds.push(`${stackId},${pathId},${stepId}`);
    parent = parent.parent;
  }
  const arrow = col('<-', Color.GRAY);
  return stackIds.map(stackId => col(stackId, Color.RED)).join(arrow);
};
