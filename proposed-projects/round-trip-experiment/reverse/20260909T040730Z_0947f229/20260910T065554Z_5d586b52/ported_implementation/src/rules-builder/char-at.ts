/**
 * Indexing helper.
 *
 * Out-of-range string indexing yields `undefined`, and the parser leans on that
 * heavily (`src[pos] === '"'`, `if (src[pos])`). This helper narrows that to the
 * empty string — falsy, and equal to no character — so the comparisons stay
 * total.
 */

export const charAt = (src: string, pos: number): string =>
  pos >= 0 && pos < src.length ? src[pos] : '';
