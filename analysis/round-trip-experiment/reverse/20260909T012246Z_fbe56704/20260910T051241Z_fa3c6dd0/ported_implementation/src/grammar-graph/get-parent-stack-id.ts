import { Color } from './colorize.ts';
import type { Colorize } from './colorize.ts';
import type { GraphPointer } from './graph-pointer.ts';

export const getParentStackId = (pointer: GraphPointer, col: Colorize): string => {
  const stackIds: string[] = [];
  let parent = pointer.parent;
  while (parent) {
    const { stackId, pathId, stepId } = parent.node.meta;
    stackIds.push(`${stackId},${pathId},${stepId}`);
    parent = parent.parent;
  }
  return stackIds.map((id) => col(id, Color.RED)).join(col('<-', Color.GRAY));
};
