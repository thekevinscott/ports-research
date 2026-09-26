// Ported from the generated Python suite at tests/python.
import { describe, expect, it } from 'vitest';

import { GBNF, GrammarParseError } from '../../src/index.js';

describe('validate grammar', () => {
  const validGrammars: [grammar: string][] = [
    ['root ::= "foo"'],
    ['root ::= "foo" | "bar"'],
    ['root ::= ("foo" | "bar")'],
    ['root ::= ("foo" | "bar")?'],
    ['root ::= ("foo" | "bar")*'],
    ['root ::= ("foo" | "bar")+'],
    ['root ::= [a-z]'],
    ['root ::= [a-zA-Z]'],
    ['root ::= [a-zA-Z0-9]'],
    ['root ::= [a-zA-Z0-9]*'],
    ['root ::= [a-zA-Z0-9]?'],
    ['root ::= [a-z]+'],
    ['root ::= [a-zA-Z0-9]+'],
    ['root ::= ([a-zA-Z0-9])*'],
    ['root ::= ([a-zA-Z0-9])?'],
    ['root ::= ([a-zA-Z0-9])+'],
    ['\n  root ::= foo\n  foo ::= "foo"'],
    ['\n  root ::= foo\n  foo ::= "foo" | "bar" | ([a-z])?\n  '],
  ];

  it.each(validGrammars)('parses a grammar (case %#)', grammar => {
    expect(() => GBNF(grammar)).not.toThrow();
  });

  const invalidGrammars: [grammar: string, errorPos: number, errorReason: string][] = [
    ['', 0, 'No rules were found'],
    ['root = "foo"', 5, 'Expecting ::= at 5'],
    ['root ::= foo\nfoo := "foo"\n  ', 17, 'Expecting ::= at 17'],
    ['root ::= foo', 9, 'Undefined rule identifier "foo"'],
    ['root ::= foo\nbar ::= "bar"\n  ', 9, 'Undefined rule identifier "foo"'],
    ['root ::= foo\nfoo ::= baz\nbar ::= "bar"\n  ', 21, 'Undefined rule identifier "baz"'],
    ['root ::= foo ::= bar', 13, 'Expecting newline or end at 13'],
    ['root ::= ([a-z]\nfoo ::= "foo"\n  ', 20, 'Expecting \')\' at 20'],
  ];

  it.each(invalidGrammars)(
    'reports an error for an invalid grammar (case %#)',
    (grammar, errorPos, errorReason) => {
      const expected = new GrammarParseError(grammar, errorPos, errorReason);
      expect(() => GBNF(grammar)).toThrow(GrammarParseError);
      try {
        GBNF(grammar);
        expect.unreachable('expected GBNF to throw');
      } catch (err) {
        expect((err as GrammarParseError).message).toBe(expected.message);
      }
    },
  );
});
