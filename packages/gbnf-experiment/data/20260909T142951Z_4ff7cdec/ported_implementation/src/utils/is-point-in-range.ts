import type { Range } from '../grammar-graph/grammar-graph-types.ts';

export const isPointInRange = (point: number, range: Range): boolean => {
  if (!Number.isInteger(point)) {
    throw new Error('point must be an integer');
  }
  return point >= range[0] && point <= range[1];
};
