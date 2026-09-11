import type { Range } from '../grammarGraph/grammarGraphTypes.ts';

export const isPointInRange = (point: number, givenRange: Range): boolean => {
  if (typeof point !== 'number' || !Number.isInteger(point)) {
    throw new Error('point must be an integer');
  }
  return point >= givenRange[0] && point <= givenRange[1];
};
