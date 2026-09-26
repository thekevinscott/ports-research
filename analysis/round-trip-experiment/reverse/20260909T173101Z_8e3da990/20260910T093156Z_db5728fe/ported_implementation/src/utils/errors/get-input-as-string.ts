import type { ValidInput } from '../../grammar-graph/types.js';

export const getInputAsString = (src: ValidInput): string => {
  if (typeof src === 'string') {
    return src;
  }
  const codePoints = Array.isArray(src) ? src : [src];
  return codePoints.map(codePoint => String.fromCodePoint(codePoint)).join('');
};
