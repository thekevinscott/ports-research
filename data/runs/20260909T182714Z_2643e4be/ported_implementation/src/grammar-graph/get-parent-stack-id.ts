import { Color } from "./colorize.js";
import type { GraphPointer } from "./graph-pointer.js";

export const getParentStackId = (
  pointer: GraphPointer,
  col: (text: string | number, color: string) => string,
): string => {
  const stackIds: string[] = [];
  let parent: GraphPointer | null = pointer.parent;
  while (parent) {
    stackIds.push(
      `${parent.node.meta.stackId},${parent.node.meta.pathId},${parent.node.meta.stepId}`,
    );
    parent = parent.parent;
  }
  const arrow = col("<-", Color.GRAY);
  return stackIds.map((stackId) => col(stackId, Color.RED)).join(arrow);
};
