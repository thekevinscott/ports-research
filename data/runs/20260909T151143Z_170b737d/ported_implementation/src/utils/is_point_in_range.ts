import type { Range } from "../grammar_graph/grammar_graph_types.ts";

export const is_point_in_range = (point: number, given_range: Range): boolean => {
  if (typeof point !== "number" || !Number.isInteger(point)) {
    throw new Error("point must be an integer");
  }
  return point >= given_range[0] && point <= given_range[1];
};
