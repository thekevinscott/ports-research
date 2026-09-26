import { describe, test, expect } from 'vitest';
import GBNF, { GrammarParseError } from 'gbnf';

describe('Validate Grammar', () => {
  test.for([
    'root ::= "foo"',
    'root ::= "foo" | "bar"',
    'root ::= ("foo" | "bar")',
    'root ::= ("foo" | "bar")?',
    'root ::= ("foo" | "bar")*',
    'root ::= ("foo" | "bar")+',
    'root ::= [a-z]',
    'root ::= [a-zA-Z]',
    'root ::= [a-zA-Z0-9]',
    'root ::= [a-zA-Z0-9]*',
    'root ::= [a-zA-Z0-9]?',
    'root ::= [a-z]+',
    'root ::= [a-zA-Z0-9]+',
    'root ::= ([a-zA-Z0-9])*',
    'root ::= ([a-zA-Z0-9])?',
    'root ::= ([a-zA-Z0-9])+',
    '\n  root ::= foo\n  foo ::= "foo"',
    '\n  root ::= foo\n  foo ::= "foo" | "bar" | ([a-z])?\n  ',
  ])('It parses a grammar (%#): `%s`', (grammar) => {
    expect(GBNF(grammar)).toBeTruthy();
  });

  test.for([
    ['', 0, 'No rules were found'],
    ['root = "foo"', 5, 'Expecting ::= at 5'],
    ['root ::= foo\nfoo := "foo"\n  ', 17, 'Expecting ::= at 17'],
    ['root ::= foo', 9, 'Undefined rule identifier "foo"'],
    ['root ::= foo\nbar ::= "bar"\n  ', 9, 'Undefined rule identifier "foo"'],
    [
      'root ::= foo\nfoo ::= baz\nbar ::= "bar"\n  ',
      21,
      'Undefined rule identifier "baz"',
    ],
    ['root ::= foo ::= bar', 13, 'Expecting newline or end at 13'],
    ['root ::= ([a-z]\nfoo ::= "foo"\n  ', 20, "Expecting ')' at 20"],
  ] as [string, number, string][])(
    'It reports an error for an invalid grammar (%#): `%s`',
    ([grammar, errorPos, errorReason]) => {
      expect(() => {
        GBNF(grammar);
      }).toThrowError(new GrammarParseError(grammar, errorPos, errorReason));
    }
  );
});
