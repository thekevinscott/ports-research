/**
 * The number of code points in a string.
 *
 * JavaScript's `String#length` counts UTF-16 code units, so any character
 * outside the BMP (an emoji, for instance) counts as two. Positions in this
 * library are code point based, so lengths must be counted the same way.
 */
export const codePointLength = (src: string): number => Array.from(src).length;
