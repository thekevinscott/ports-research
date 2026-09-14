import type { ValidInput } from '../../grammarGraph/types';

export const getInputAsString = (src: ValidInput): string => {
  if (typeof src === 'string') {
    return src;
  }
  const codePoints = Array.isArray(src) ? src : [src];
  return codePoints.map((cp) => String.fromCodePoint(cp)).join('');
};
