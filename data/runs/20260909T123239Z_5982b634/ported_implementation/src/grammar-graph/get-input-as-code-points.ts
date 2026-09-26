import type { ValidInput } from './types.js';

export const getCodePoint = (char: string): number => {
  const codePoint = char.codePointAt(0);
  if (codePoint === undefined) {
    throw new Error(`Could not get code point for character: ${char}`);
  }
  return codePoint;
};

export const getInputAsCodePoints = (src: ValidInput): number[] => {
  if (typeof src === 'number') {
    return [src];
  }

  if (Array.isArray(src)) {
    for (const codePoint of src) {
      if (!Number.isInteger(codePoint)) {
        throw new Error(`code_point must be an integer for ${codePoint} if src is a list`);
      }
    }
    return src;
  }

  if (typeof src === 'string') {
    return [...src].map(getCodePoint);
  }

  throw new Error(`Invalid input type: ${typeof src}`);
};
