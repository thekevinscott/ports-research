import type { Range } from '../grammarGraph/types';

export const isPointInRange = (point: number, [start, end]: Range): boolean =>
  point >= start && point <= end;
