import type { ValidInput } from './types.js';

export const getInputAsCodePoints = (src: ValidInput): number[] => {
  if (typeof src !== 'string') {
    return Array.isArray(src) ? [...src] : [src];
  }

  // iterating a string yields whole code points, so a character outside the
  // Basic Multilingual Plane is a single entry rather than two surrogate halves.
  return [...src].map(char => char.codePointAt(0) as number);
};
