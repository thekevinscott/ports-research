import { Color } from './colorize';
import type { GraphPointer } from './graph-pointer';

export const getParentStackId = (
  pointer: GraphPointer,
  col: (value: string | number, color: string) => string,
): string => {
  const stackIds: string[] = [];
  let parent: GraphPointer | undefined = pointer.parent;
  while (parent) {
    stackIds.push(
      `${parent.node.meta.stackId},${parent.node.meta.pathId},${parent.node.meta.stepId}`,
    );
    parent = parent.parent;
  }
  const arrow = col('<-', Color.GRAY);
  return stackIds.map(stackId => col(stackId, Color.RED)).join(arrow);
};
