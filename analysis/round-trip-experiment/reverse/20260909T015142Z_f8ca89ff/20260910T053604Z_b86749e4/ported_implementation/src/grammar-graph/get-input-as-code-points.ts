import type { ValidInput } from './types';

export const getInputAsCodePoints = (src: ValidInput): number[] => {
  if (typeof src !== 'string') {
    return Array.isArray(src) ? [...src] : [src];
  }

  return src.split('').map((char) => char.charCodeAt(0));
};
