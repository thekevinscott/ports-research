import type { ValidInput } from './grammar-graph-types';

export const getCodePoint = (char: string): number => {
  const codePoint = char.codePointAt(0);
  if (codePoint === undefined) {
    throw new Error(`Could not get code point for character: ${char}`);
  }
  if (typeof codePoint !== 'number') {
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
      if (typeof c !== 'number') {
        throw new Error(
          `code_point must be an integer for ${c} if src is a list`
        );
      }
    }
    return src;
  }

  if (typeof src === 'string') {
    return src.split('').map(getCodePoint);
  }

  throw new Error(`Invalid input type: ${typeof src}`);
};
