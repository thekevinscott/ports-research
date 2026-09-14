import type { ValidInput } from './errorsTypes.js';

export const getInputAsString = (src: ValidInput): string => {
  if (typeof src === 'string') {
    return src;
  }
  if (typeof src === 'number') {
    return String.fromCodePoint(src);
  }
  return src.map((codePoint) => String.fromCodePoint(codePoint)).join('');
};
