/** Port of `gbnf/grammar_graph/get_input_as_code_points.py`. */

import type { ValidInput } from './types.js';

export const getInputAsCodePoints = (src: ValidInput): number[] => {
  if (typeof src !== 'string') {
    return Array.isArray(src) ? [...src] : [src];
  }

  // Iterating a string yields code points, so an astral character counts once.
  return [...src].map((char) => char.codePointAt(0) as number);
};
