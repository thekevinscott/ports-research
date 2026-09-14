const WORD_CHAR = /[a-zA-Z]/;

export const isWordChar = (c: string): boolean => !!c && WORD_CHAR.test(c);
