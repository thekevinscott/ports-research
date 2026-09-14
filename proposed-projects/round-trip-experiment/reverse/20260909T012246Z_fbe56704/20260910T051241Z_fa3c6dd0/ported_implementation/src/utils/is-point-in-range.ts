import type { Range } from '../grammar-graph/types.ts';

export const isPointInRange = (point: number, [start, end]: Range): boolean =>
  point >= start && point <= end;
