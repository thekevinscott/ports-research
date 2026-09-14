const WORD_CHAR = /[a-zA-Z]/;

export const isWordChar = (char: string): boolean => WORD_CHAR.test(char);
