import { Color, type Colorize } from './colorize.js';
import type { GraphPointer } from './graph-pointer.js';

export const getParentStackId = (pointer: GraphPointer, col: Colorize): string => {
  const stackIds: string[] = [];
  let parent = pointer.parent;
  while (parent) {
    const { stackId, pathId, stepId } = parent.node.meta;
    stackIds.push(`${stackId},${pathId},${stepId}`);
    parent = parent.parent;
  }
  return stackIds
    .map((stackId) => col(stackId, Color.RED))
    .join(col('<-', Color.GRAY));
};
