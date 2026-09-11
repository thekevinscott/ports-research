import assert from 'node:assert/strict';
import { describe, it } from 'node:test';

import { GBNF, GrammarParseError } from '../src/index.ts';
import { validateNonEmpty } from '../src/utils/validateNonEmpty.ts';

describe('GBNF entry point', () => {
  it('rejects a non-string grammar', () => {
    assert.throws(() => GBNF(42 as unknown as string), /grammar must be a string/u);
  });

  it('rejects a non-string initial string', () => {
    assert.throws(
      () => GBNF('root ::= "a"', 42 as unknown as string),
      /input must be a string/u,
    );
  });

  it('accepts an initial string and advances the parse', () => {
    const state = GBNF('root ::= "foo"', 'fo');
    assert.deepStrictEqual(
      [...state].map((rule) => rule.toDict()),
      [{ type: 'RuleChar', value: [111] }],
    );
  });

  it('exposes the grammar on the parse state', () => {
    assert.equal(GBNF('root ::= "a"').grammar, 'root ::= "a"');
  });

  it('throws when no rules were found', () => {
    assert.throws(() => GBNF(''), (err: unknown) => {
      assert.ok(err instanceof GrammarParseError);
      assert.equal(err.reason, 'No rules were found');
      return true;
    });
  });

  // The reference implementation looks this up with `symbol_ids["root"]`, which
  // raises a bare `KeyError` before its own guard can run. The port raises the
  // GrammarParseError that guard was written to raise.
  it("throws when the grammar has no 'root' symbol", () => {
    assert.throws(() => GBNF('nope ::= "a"'), (err: unknown) => {
      assert.ok(err instanceof GrammarParseError);
      assert.equal(err.reason, "Grammar does not contain a 'root' symbol");
      return true;
    });
  });

  // Likewise, the reference indexes past the end of the grammar here and raises
  // a bare `IndexError` instead of the intended parse error.
  it('throws when a group is never closed', () => {
    assert.throws(() => GBNF('root ::= "a" ('), (err: unknown) => {
      assert.ok(err instanceof GrammarParseError);
      assert.match(err.reason, /^Expecting '\)' at/u);
      return true;
    });
  });
});

describe('validateNonEmpty', () => {
  it('returns the value when it is non-empty', () => {
    assert.deepStrictEqual(validateNonEmpty([1, 2]), [1, 2]);
  });

  it('throws when the value is empty', () => {
    assert.throws(() => validateNonEmpty([]), /Value cannot be empty\./u);
  });
});
