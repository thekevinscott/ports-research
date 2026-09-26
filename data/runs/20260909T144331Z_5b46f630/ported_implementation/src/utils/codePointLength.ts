// Python strings are sequences of code points, JavaScript strings are sequences of UTF-16
// code units. Positions reported by the parser are code point offsets, so anywhere the
// reference implementation uses `len(str)` for a position we count code points instead of
// using `String.prototype.length`.
export const codePointLength = (src: string): number => {
  let length = 0;
  for (const _ of src) {
    length += 1;
  }
  return length;
};
