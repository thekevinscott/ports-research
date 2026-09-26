import type { ValidInput } from './errors-types.js';

export const getInputAsString = (src: ValidInput): string => {
  if (typeof src === 'string') {
    return src;
  }
  if (typeof src === 'number') {
    return String.fromCodePoint(src);
  }
  return src.map((cp) => String.fromCodePoint(cp)).join('');
};
