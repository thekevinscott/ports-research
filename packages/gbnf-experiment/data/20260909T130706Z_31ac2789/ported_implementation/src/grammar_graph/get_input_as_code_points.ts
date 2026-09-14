import type { ValidInput } from './grammar_graph_types.ts';

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
    return Array.from(src).map((s) => getCodePoint(s));
  }

  throw new Error(`Invalid input type: ${typeof src}`);
};

export const get_code_point = getCodePoint;
export const get_input_as_code_points = getInputAsCodePoints;
