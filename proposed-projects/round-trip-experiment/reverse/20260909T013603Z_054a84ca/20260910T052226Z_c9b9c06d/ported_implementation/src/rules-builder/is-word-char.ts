const WORD_CHAR = /[a-zA-Z]/;

export const isWordChar = (c: string | undefined): boolean =>
  c !== undefined && WORD_CHAR.test(c);
