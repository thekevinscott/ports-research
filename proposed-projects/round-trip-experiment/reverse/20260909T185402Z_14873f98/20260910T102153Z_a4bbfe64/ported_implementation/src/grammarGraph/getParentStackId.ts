import { Color } from './colorize';
import type { Colorize } from './colorize';
import type { GraphPointer } from './graphPointer';

export const getParentStackId = (
  pointer: GraphPointer,
  col: Colorize,
): string => {
  const stackIds: string[] = [];
  let parent = pointer.parent;
  while (parent !== undefined) {
    const { stackId, pathId, stepId } = parent.node.meta;
    stackIds.push(`${stackId},${pathId},${stepId}`);
    parent = parent.parent;
  }
  return stackIds.map((i) => col(i, Color.RED)).join(col('<-', Color.GRAY));
};
