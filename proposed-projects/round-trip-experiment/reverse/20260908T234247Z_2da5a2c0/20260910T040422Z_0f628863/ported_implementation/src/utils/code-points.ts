/**
 * Helpers for treating a string as a sequence of code points.
 *
 * Every position in this library — grammar offsets, error carets, input offsets —
 * counts code points, not UTF-16 code units. The two agree for the whole Basic
 * Multilingual Plane and differ only for astral characters (emoji and friends),
 * where one character counts as one position and `\U0001F600`-style escapes are
 * able to match real input.
 */

/** Splits `str` into its code points, each as a one-code-point string. */
export const toChars = (str: string): string[] => Array.from(str);

/** The number of code points in `str`. */
export const codePointLength = (str: string): number => Array.from(str).length;

/**
 * Mirrors JS `str[pos]` on an array of code points: an out of bounds position is
 * the empty string, which is falsy in the same places `undefined` would be.
 */
export const at = (chars: string[], pos: number): string =>
  pos >= 0 && pos < chars.length ? chars[pos] : '';
