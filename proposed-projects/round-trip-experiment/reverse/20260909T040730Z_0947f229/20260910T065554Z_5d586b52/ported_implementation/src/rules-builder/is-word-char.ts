/** Port of `gbnf/rules_builder/is_word_char.py`. */

const WORD_CHAR = /[a-zA-Z]/;

export const isWordChar = (c: string): boolean => WORD_CHAR.test(c);
