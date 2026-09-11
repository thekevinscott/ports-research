import assert from 'node:assert/strict';
import { describe, test } from 'node:test';
import { PARSE_NAME_ERROR, parseName } from '../../../src/rules-builder/parse-name.ts';
import { GrammarParseError } from '../../../src/utils/errors/index.ts';

describe('parse name', () => {
  test('should return correct name when encountering a valid name', () => {
    const src = 'validName';
    assert.equal(parseName(src, 0), src);
  });

  test('should return correct name when encountering a valid name starting at a non zero position', () => {
    assert.equal(parseName('123validName', 3), 'validName');
  });

  test('should throw error when encountering an invalid name', () => {
    const src = '123';
    assert.throws(
      () => parseName(src, 0),
      (err: unknown) => {
        assert.ok(err instanceof GrammarParseError);
        assert.equal(String(err), String(new GrammarParseError(src, 0, PARSE_NAME_ERROR)));
        return true;
      },
    );
  });
});
