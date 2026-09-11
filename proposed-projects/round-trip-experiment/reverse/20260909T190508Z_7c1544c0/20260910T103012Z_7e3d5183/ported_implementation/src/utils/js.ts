/**
 * Small helpers that let the port index strings by code point.
 *
 * The reference implementation is a Python one, so `src[pos]` walks code
 * points, not the UTF-16 code units a JS string exposes. These helpers split a
 * string once (memoising the most recent split, since a parse works through a
 * single source) and index the resulting array instead.
 *
 * They also stand in for Python's bounds checking: out-of-range indices give
 * the empty string, which is falsy and compares unequal to every character.
 */

let cachedSrc: string | null = null;
let cachedChars: string[] = [];

export const codePoints = (src: string): string[] => {
  if (cachedSrc !== src) {
    cachedSrc = src;
    cachedChars = Array.from(src);
  }
  return cachedChars;
};

/** `src[pos]`: the empty string stands in for an out-of-range index. */
export const charAt = (src: string, pos: number): string => {
  const chars = codePoints(src);
  if (pos < 0 || pos >= chars.length) {
    return '';
  }
  return chars[pos];
};

/** `src.slice(start, end)`: out-of-range indices are clamped, not errors. */
export const slice = (src: string, start: number, end: number): string =>
  codePoints(src)
    .slice(Math.max(start, 0), Math.max(end, 0))
    .join('');

/** `len(src)`: the number of code points, not of UTF-16 code units. */
export const length = (src: string): number => codePoints(src).length;

/** `ord(src[pos])`, for a position known to be in range. */
export const codePointAt = (src: string, pos: number): number =>
  codePoints(src)[pos].codePointAt(0) as number;
