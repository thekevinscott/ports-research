import { Color } from './colorize.ts';
import type { Colorize } from './grammarGraphTypes.ts';
import type { GraphPointer } from './graphPointer.ts';

export const getParentStackId = (pointer: GraphPointer, col: Colorize): string => {
  const stackIds: string[] = [];
  let parent: GraphPointer | null = pointer.parent;
  while (parent) {
    stackIds.push(
      `${parent.node.meta.stackId},${parent.node.meta.pathId},${parent.node.meta.stepId}`,
    );
    parent = parent.parent;
  }
  const arrow = col('<-', Color.GRAY);
  return stackIds.map((stackId) => col(stackId, Color.RED)).join(arrow);
};
