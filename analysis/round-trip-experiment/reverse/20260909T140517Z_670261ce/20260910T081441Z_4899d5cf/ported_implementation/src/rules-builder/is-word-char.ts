const WORD_CHAR = /[a-zA-Z]/;

export const isWordChar = (c: string): boolean => WORD_CHAR.test(c);
