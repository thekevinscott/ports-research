const WORD_CHAR = /[a-zA-Z]/;

export const isWordChar = (c: string | undefined): boolean =>
  typeof c === 'string' && WORD_CHAR.test(c);
