/**
 * The reference implementation signals programmer/usage errors with Python's
 * builtin exceptions. These classes preserve the distinction (and the exact
 * messages) so callers can tell them apart the same way they can in Python.
 */

export class ValueError extends Error {
  override name = "ValueError";
}

export class KeyError extends Error {
  override name = "KeyError";

  constructor(key: string | number) {
    super(typeof key === "string" ? `'${key}'` : `${key}`);
  }
}

export class IndexError extends Error {
  override name = "IndexError";

  constructor(message = "string index out of range") {
    super(message);
  }
}

/**
 * Equivalent of Python's `src[pos]` on a string: an out of bounds read raises
 * rather than quietly producing `undefined`.
 */
export const charAt = (src: string, pos: number): string => {
  if (pos < 0 || pos >= src.length) {
    throw new IndexError();
  }
  return src[pos];
};
