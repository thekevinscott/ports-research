import type { Range } from '../grammarGraph/types.js';

export const isPointInRange = (point: number, range: Range): boolean => {
  const [start, end] = range;
  return start <= point && point <= end;
};
