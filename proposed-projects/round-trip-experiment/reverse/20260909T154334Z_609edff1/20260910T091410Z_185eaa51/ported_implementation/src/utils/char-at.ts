/**
 * Forgiving lookups for strings and arrays.
 *
 * Indexing out of bounds yields `undefined` in Javascript; these helpers keep
 * that behaviour explicit, and give strings an empty string instead so callers
 * can compare against characters without a null check.
 */

/** Return the character at `pos`, or '' when out of bounds. */
export const charAt = (src: string, pos: number): string =>
  pos >= 0 && pos < src.length ? src[pos] : '';

/** Return the item at `pos`, or undefined when out of bounds. */
export const itemAt = <T>(items: T[], pos: number): T | undefined =>
  pos >= 0 && pos < items.length ? items[pos] : undefined;
