import { Color, Colorize } from './colorize';
import type { GraphPointer } from './graph-pointer';

export const getParentStackId = (pointer: GraphPointer, col: Colorize): string => {
  const stackIds: string[] = [];
  let parent: GraphPointer | undefined = pointer.parent;
  while (parent !== undefined) {
    const { stackId, pathId, stepId } = parent.node.meta;
    stackIds.push(`${stackId},${pathId},${stepId}`);
    parent = parent.parent;
  }
  return stackIds.map((stackId) => col(stackId, Color.RED)).join(col('<-', Color.GRAY));
};
