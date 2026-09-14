import { Color, type Colorize } from './colorize.js';
import type { GraphPointer } from './graph-pointer.js';

export const getParentStackId = (
  pointer: GraphPointer,
  col: Colorize
): string => {
  const stackIds: string[] = [];
  let parent = pointer.parent;
  while (parent) {
    const meta = parent.node.meta;
    stackIds.push(`${meta.stackId},${meta.pathId},${meta.stepId}`);
    parent = parent.parent;
  }
  return stackIds
    .map((id) => col(id, Color.RED))
    .join(col('<-', Color.GRAY));
};
