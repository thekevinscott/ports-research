import type { ValidInput } from './errors-types.js';

export const getInputAsString = (src: ValidInput): string => {
  if (typeof src === 'string') {
    return src;
  }
  if (typeof src === 'number') {
    return String.fromCodePoint(src);
  }
  return src.map((codePoint) => String.fromCodePoint(codePoint)).join('');
};

// Lengths and positions are counted in code points, matching how the parser
// walks its input.
export const getLengthInCodePoints = (src: string): number =>
  Array.from(src).length;
