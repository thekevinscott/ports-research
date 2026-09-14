const HEX_DIGITS = '0123456789abcdefABCDEF';

/**
 * Parse the leading run of hex digits of `src`, or `undefined` if there is none.
 *
 * Deliberately stricter than `parseInt(src, 16)`, which also accepts a leading
 * sign and leading whitespace: `\u+0042` is not a valid escape.
 */
export const parseHex = (src: string): number | undefined => {
  let end = 0;
  while (end < src.length && HEX_DIGITS.includes(src[end])) {
    end += 1;
  }
  if (end === 0) {
    return undefined;
  }
  return parseInt(src.slice(0, end), 16);
};
