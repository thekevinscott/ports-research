import { describe, expect, test } from 'vitest';
import { PARSE_NAME_ERROR, parseName } from '../../../src/rules-builder/parse-name.ts';
import { GrammarParseError } from '../../../src/utils/errors/index.ts';

describe('parse_name', () => {
  test('should return correct name when encountering a valid name', () => {
    const src = 'validName';
    expect(parseName(src, 0)).toBe(src);
  });

  test('should return correct name when encountering a valid name starting at a non zero position', () => {
    const src = '123validName';
    expect(parseName(src, 3)).toBe('validName');
  });

  test('should throw error when encountering an invalid name', () => {
    const src = '123';
    let thrown: unknown;
    try {
      parseName(src, 0);
    } catch (err) {
      thrown = err;
    }
    expect(thrown).toBeInstanceOf(GrammarParseError);
    expect(String(thrown)).toBe(String(new GrammarParseError(src, 0, PARSE_NAME_ERROR)));
  });
});
