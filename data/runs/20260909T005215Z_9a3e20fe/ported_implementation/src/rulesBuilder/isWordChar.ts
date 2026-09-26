const WORD_CHAR = /[a-zA-Z]/u;

export const isWordChar = (c: string): boolean => WORD_CHAR.test(c);
