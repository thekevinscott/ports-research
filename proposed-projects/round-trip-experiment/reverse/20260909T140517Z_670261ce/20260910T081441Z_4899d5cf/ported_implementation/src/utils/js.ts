/**
 * Small helpers shared across the port.
 *
 * The reference treats a grammar as a sequence of *code points*, not UTF-16 code
 * units, so grammars are carried around as `Chars` — an array with one entry per
 * code point — rather than as a raw string. Indexing that array keeps the port's
 * character arithmetic identical for astral characters such as `😀`.
 */

const HEX_DIGITS = '0123456789abcdefABCDEF';

/** A source string split into one entry per code point. */
export type Chars = string[];

export const toChars = (src: string): Chars => Array.from(src);

export const fromChars = (src: Chars): string => src.join('');

/** `src[pos]`, or the empty string when out of range (the reference's falsy `undefined`). */
export const charAt = (src: Chars, pos: number): string =>
  pos >= 0 && pos < src.length ? src[pos] : '';

/** `items[items.length - 1]`, `undefined` when empty. */
export const last = <T>(items: readonly T[]): T | undefined =>
  items.length > 0 ? items[items.length - 1] : undefined;

/**
 * `parseInt(src, 16)`: consume the leading run of hex digits.
 *
 * Returns `undefined` where the reference would yield `NaN`.
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
