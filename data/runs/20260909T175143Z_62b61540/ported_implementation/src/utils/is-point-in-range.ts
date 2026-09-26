import { Range } from '../grammar-graph/grammar-graph-types';

export const isPointInRange = (point: number, range: Range): boolean => {
  if (typeof point !== 'number') {
    throw new Error('point must be an integer');
  }
  return point >= range[0] && point <= range[1];
};
