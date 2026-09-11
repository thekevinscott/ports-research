import type { ValidInput } from './grammarGraphTypes.ts';

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
    for (const c of src) {
      if (!Number.isInteger(c)) {
        throw new Error(`code_point must be an integer for ${c} if src is a list`);
      }
    }
    return src;
  }

  if (typeof src === 'string') {
    // Iterating a string yields code points, matching Python's `for s in src`.
    return [...src].map(getCodePoint);
  }

  throw new Error(`Invalid input type: ${typeof src}`);
};
