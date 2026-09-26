import type { ValidInput } from './types.js';

/**
 * Turn input into the UTF-16 code units the graph is walked with.
 */
export const getInputAsCodePoints = (src: ValidInput): number[] => {
  if (typeof src !== 'string') {
    return Array.isArray(src) ? [...src] : [src];
  }

  const codePoints: number[] = [];
  for (let i = 0; i < src.length; i++) {
    codePoints.push(src.charCodeAt(i));
  }
  return codePoints;
};
