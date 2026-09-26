const WORD_CHAR = /[a-zA-Z]/;

export const isWordChar = (char: string): boolean => !!char && WORD_CHAR.test(char);
