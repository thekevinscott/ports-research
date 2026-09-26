/**
 * Index a string, returning the empty string for out of range indices.
 *
 * The empty string is falsy, so `if (charAt(src, pos))` reads the same as
 * `if (src[pos])` did before the index guard was made explicit.
 */
export const charAt = (src: string, pos: number): string => {
  if (pos >= 0 && pos < src.length) {
    return src[pos];
  }
  return '';
};
