import type { Range } from '../grammar_graph/grammar_graph_types.ts';

export const isPointInRange = (point: number, givenRange: Range): boolean => {
  if (!Number.isInteger(point)) {
    throw new Error('point must be an integer');
  }
  return point >= givenRange[0] && point <= givenRange[1];
};

export const is_point_in_range = isPointInRange;
