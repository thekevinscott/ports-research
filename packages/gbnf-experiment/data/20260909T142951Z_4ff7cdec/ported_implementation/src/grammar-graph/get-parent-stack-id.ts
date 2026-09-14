import { Color } from './colorize.ts';
import type { GraphPointer } from './graph-pointer.ts';

export const getParentStackId = (
  pointer: GraphPointer,
  col: (value: string | number, color: string) => string
): string => {
  const stackIds: string[] = [];
  let parent = pointer.parent;
  while (parent) {
    const { stackId, pathId, stepId } = parent.node.meta;
    stackIds.push(`${stackId},${pathId},${stepId}`);
    parent = parent.parent;
  }
  const arrow = col('<-', Color.GRAY);
  return stackIds.map(stackId => col(stackId, Color.RED)).join(arrow);
};
