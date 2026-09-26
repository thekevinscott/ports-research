import type { ValidInput } from './types.js';

export const getInputAsCodePoints = (src: ValidInput): number[] => {
  if (typeof src !== 'string') {
    return Array.isArray(src) ? [...src] : [src];
  }

  // Split by code unit, matching how the grammar parser indexes its source: a
  // character outside the BMP is a surrogate pair on both sides of the match.
  return src.split('').map(char => char.charCodeAt(0));
};
