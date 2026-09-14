/**
 * The number of code points in a string.
 *
 * Python's `len` counts code points, whereas JavaScript's `String.length` counts UTF-16 code
 * units. Positions reported by the parser are code point offsets, so error rendering measures
 * lengths the same way.
 */
export const codePointLength = (value: string): number => Array.from(value).length;
