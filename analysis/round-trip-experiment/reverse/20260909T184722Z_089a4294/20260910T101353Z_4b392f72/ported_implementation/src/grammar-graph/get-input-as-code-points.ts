import type { ValidInput } from './types';

export const getInputAsCodePoints = (src: ValidInput): number[] => {
  if (typeof src !== 'string') {
    return Array.isArray(src) ? [...src] : [src];
  }

  // iterate by code point, not by UTF-16 unit, so astral characters stay whole
  return Array.from(src, char => char.codePointAt(0) as number);
};
