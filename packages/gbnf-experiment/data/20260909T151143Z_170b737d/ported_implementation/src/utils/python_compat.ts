/**
 * Small helpers that reproduce Python runtime behaviour the reference
 * implementation relies on. They exist so that the port raises in the same
 * places the Python original does, instead of silently producing `undefined`
 * (or, worse, looping forever on an out-of-bounds character comparison).
 */

/** Mirrors Python's `KeyError`; `str(KeyError("root"))` is `"'root'"`. */
export class KeyError extends Error {
  constructor(key: string | number) {
    super(typeof key === "string" ? `'${key}'` : `${key}`);
    this.name = "KeyError";
  }
}

/** Mirrors Python's `IndexError` for string subscripting. */
export class IndexError extends Error {
  constructor(message: string = "string index out of range") {
    super(message);
    this.name = "IndexError";
  }
}

/** Mirrors Python's `AttributeError`. */
export class AttributeError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "AttributeError";
  }
}

/** `src[pos]` with Python's bounds checking. */
export const at = (src: string, pos: number): string => {
  const char = src[pos];
  if (char === undefined) {
    throw new IndexError();
  }
  return char;
};

/**
 * `json.dumps` for the plain data the reference serializes (numbers, strings,
 * arrays and string-keyed objects). Python separates items with ", " and
 * key/value pairs with ": ", where `JSON.stringify` uses no whitespace at all;
 * the difference is visible in the rule keys this is used to build.
 */
export const json_dumps = (value: unknown): string => {
  if (Array.isArray(value)) {
    return `[${value.map(json_dumps).join(", ")}]`;
  }
  if (value !== null && typeof value === "object") {
    const entries = Object.entries(value as Record<string, unknown>);
    return `{${entries.map(([k, v]) => `${JSON.stringify(k)}: ${json_dumps(v)}`).join(", ")}}`;
  }
  return JSON.stringify(value) ?? "null";
};
