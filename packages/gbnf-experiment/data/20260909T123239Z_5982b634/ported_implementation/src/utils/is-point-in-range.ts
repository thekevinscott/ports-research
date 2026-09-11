import type { Range } from '../grammar-graph/types.js';

export const isPointInRange = (point: number, [start, end]: Range): boolean => {
  if (!Number.isInteger(point)) {
    throw new Error('point must be an integer');
  }
  return point >= start && point <= end;
};
