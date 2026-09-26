const WORD_CHAR = /[a-zA-Z]/;

export const isWordChar = (c: string): boolean => Boolean(c) && WORD_CHAR.test(c);
