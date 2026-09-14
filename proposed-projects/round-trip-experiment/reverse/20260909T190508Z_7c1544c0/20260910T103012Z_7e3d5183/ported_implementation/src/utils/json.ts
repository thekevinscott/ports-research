/**
 * `json.dumps(value)` with Python's default separators.
 *
 * `JSON.stringify` packs arrays as `["a","b"]`, where Python renders
 * `["a", "b"]`; error messages quote these verbatim, so the spacing matters.
 */
export const dumps = (value: unknown): string => {
  if (Array.isArray(value)) {
    return `[${value.map(dumps).join(', ')}]`;
  }
  if (typeof value === 'object' && value !== null) {
    const entries = Object.entries(value)
      .filter(([, v]) => v !== undefined)
      .map(([key, v]) => `${JSON.stringify(key)}: ${dumps(v)}`);
    return `{${entries.join(', ')}}`;
  }
  return JSON.stringify(value) ?? 'null';
};
