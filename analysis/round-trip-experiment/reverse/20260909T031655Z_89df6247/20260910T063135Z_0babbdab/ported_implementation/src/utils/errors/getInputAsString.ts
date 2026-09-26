export type InputSource = string | number | number[];

/** `src` is a string, a code point, or a list of code points. */
export const getInputAsString = (src: InputSource): string => {
  if (typeof src === 'string') {
    return src;
  }
  const codePoints = Array.isArray(src) ? src : [src];
  return codePoints.map((cp) => String.fromCodePoint(cp)).join('');
};
