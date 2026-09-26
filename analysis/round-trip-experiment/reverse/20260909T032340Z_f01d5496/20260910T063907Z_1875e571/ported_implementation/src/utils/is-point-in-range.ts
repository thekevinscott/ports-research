import type { Range } from '../grammar-graph/types';

export const isPointInRange = (point: number, [start, end]: Range): boolean =>
  start <= point && point <= end;
