import type { ValidInput } from './errors_types.ts';

export const getInputAsString = (src: ValidInput): string => {
  if (typeof src === 'string') {
    return src;
  }
  if (typeof src === 'number') {
    return String.fromCodePoint(src);
  }
  return src.map((codePoint) => String.fromCodePoint(codePoint)).join('');
};

export const get_input_as_string = getInputAsString;
