import { Color } from "./colorize.ts";
import type { GraphPointer } from "./graph_pointer.ts";

export const get_parent_stack_id = (
  pointer: GraphPointer,
  col: (text: string | number, color: string) => string,
): string => {
  const stack_ids: string[] = [];
  let parent: GraphPointer | null = pointer.parent;
  while (parent) {
    stack_ids.push(
      `${parent.node.meta.stackId},${parent.node.meta.pathId},${parent.node.meta.stepId}`,
    );
    parent = parent.parent;
  }
  const arrow = col("<-", Color.GRAY);
  return stack_ids.map((stack_id) => col(stack_id, Color.RED)).join(arrow);
};
