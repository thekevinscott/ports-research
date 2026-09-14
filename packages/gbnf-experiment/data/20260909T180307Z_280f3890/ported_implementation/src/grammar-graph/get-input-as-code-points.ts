import type { ValidInput } from './grammar-graph-types.js';

export const getCodePoint = (char: string): number => {
  const codePoint = char.codePointAt(0);
  if (codePoint === undefined) {
    throw new Error(`Could not get code point for character: ${char}`);
  }
  if (!Number.isInteger(codePoint)) {
    throw new Error('code_point must be an integer!');
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
    // Iterating a string with `Array.from` walks code points, matching Python's
    // per-character iteration rather than JS's UTF-16 code unit indexing.
    return Array.from(src).map(getCodePoint);
  }

  throw new Error(`Invalid input type: ${typeof src}`);
};
