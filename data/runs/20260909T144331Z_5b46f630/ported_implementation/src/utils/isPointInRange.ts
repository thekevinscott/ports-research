import type { Range } from '../grammarGraph/grammarGraphTypes.js';

export const isPointInRange = (point: number, givenRange: Range): boolean => {
  if (!Number.isInteger(point)) {
    throw new Error('point must be an integer');
  }
  return point >= givenRange[0] && point <= givenRange[1];
};
