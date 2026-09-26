/**
 * Helpers that reproduce the two Python stringification formats the reference
 * implementation embeds in its error messages and cache keys:
 *
 *  - `repr()` mirrors Python's `repr()` / f-string interpolation of a value.
 *  - `jsonDumps()` mirrors `json.dumps()`, which separates items with `", "`.
 *
 * Keeping them means the ported error messages are byte-for-byte identical to
 * the ones the reference implementation raises.
 */

/** Objects that want to control how `repr` renders them (Python's `__repr__`). */
export interface Representable {
  toRepr(): string;
}

const isRepresentable = (value: unknown): value is Representable =>
  typeof value === 'object' && value !== null && typeof (value as Representable).toRepr === 'function';

export const repr = (value: unknown): string => {
  if (value === null || value === undefined) {
    return 'None';
  }
  if (typeof value === 'boolean') {
    return value ? 'True' : 'False';
  }
  if (typeof value === 'number') {
    return String(value);
  }
  if (typeof value === 'string') {
    return `'${value.replace(/\\/gu, '\\\\').replace(/'/gu, "\\'")}'`;
  }
  if (Array.isArray(value)) {
    return `[${value.map(repr).join(', ')}]`;
  }
  if (isRepresentable(value)) {
    return value.toRepr();
  }
  const entries = Object.entries(value as Record<string, unknown>);
  return `{${entries.map(([key, val]) => `${repr(key)}: ${repr(val)}`).join(', ')}}`;
};

export const jsonDumps = (value: unknown): string => {
  if (Array.isArray(value)) {
    return `[${value.map(jsonDumps).join(', ')}]`;
  }
  if (typeof value === 'object' && value !== null) {
    const entries = Object.entries(value as Record<string, unknown>);
    return `{${entries.map(([key, val]) => `${JSON.stringify(key)}: ${jsonDumps(val)}`).join(', ')}}`;
  }
  return JSON.stringify(value) ?? 'null';
};
