/**
 * Helpers for treating strings as sequences of unicode code points.
 *
 * Python indexes strings by code point, JavaScript by UTF-16 code unit. Every
 * position/length in this library is a code point index, matching the reference
 * implementation, so anything that walks a string does it through these helpers.
 */

export const toCodePoints = (src: string): string[] => Array.from(src);

export const codePointLength = (src: string): number => toCodePoints(src).length;

/** Accepts either a string or an already-split array of code points. */
export const asCodePoints = (src: string | string[]): string[] =>
  Array.isArray(src) ? src : toCodePoints(src);

export const asString = (src: string | string[]): string =>
  Array.isArray(src) ? src.join("") : src;
