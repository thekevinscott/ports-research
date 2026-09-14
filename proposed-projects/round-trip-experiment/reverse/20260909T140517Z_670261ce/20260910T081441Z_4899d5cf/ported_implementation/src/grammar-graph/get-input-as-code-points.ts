import type { ValidInput } from './types.js';

export const getInputAsCodePoints = (src: ValidInput): number[] => {
  if (typeof src !== 'string') {
    return Array.isArray(src) ? [...src] : [src];
  }

  return Array.from(src, (char) => char.codePointAt(0) as number);
};
