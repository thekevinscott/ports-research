const WORD_CHAR = /[a-zA-Z]/;

// A missing character is coerced to the string "undefined" before being tested.
export const isWordChar = (c?: string): boolean =>
  WORD_CHAR.test(c === undefined ? 'undefined' : c);
