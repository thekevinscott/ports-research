import type { Range } from '../grammar-graph/types';

export const isPointInRange = (point: number, range: Range): boolean => {
  const [start, end] = range;
  return start <= point && point <= end;
};
