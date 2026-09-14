const WORD_CHAR = /[a-zA-Z]/;

export const isWordChar = (c?: string): boolean =>
  c !== undefined && c !== null && WORD_CHAR.test(c);
