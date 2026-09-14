import type { Range } from '../grammar-graph/types.js';

export const isPointInRange = (point: number, [start, end]: Range): boolean =>
  start <= point && point <= end;
