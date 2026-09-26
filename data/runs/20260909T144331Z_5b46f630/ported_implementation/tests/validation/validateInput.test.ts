import { describe, expect, it } from 'vitest';
import { GBNF, InputParseError } from '../../src/index.js';
import { captureError } from '../helpers.js';

const VALID_INPUTS: [grammar: string, input: string][] = [['root ::= "foo"', 'f']];

const INVALID_INPUTS: [grammar: string, inputText: string, errorPos: number][] =
  [
    ['root ::= "foo"', '2', 0],
    ['root ::= "foo"', 'b', 0],
    ['root ::= "foo"', 'f1', 1],
    ['root ::= "foo"', 'fo1', 2],
    ['root ::= "foo"', 'fooo', 3],
    ['root ::= "foo"', 'fooooooo', 3],
    ['root ::= "foo" | "bar"', '1', 0],
    ['root ::= "foo" | "bar"', 'z', 0],
    ['root ::= "foo" | "bar"', 'f1', 1],
    ['root ::= "foo" | "bar"', 'b1', 1],
    ['root ::= "foo" | "bar"', 'fo1', 2],
    ['root ::= "foo" | "bar"', 'ba1', 2],
    ['root ::= "foo" | "bar"', 'fooo', 3],
    ['root ::= "foo" | "bar"', 'barrr', 3],
    ['root ::= "foo" | "bar" | "baz"', '1', 0],
    ['root ::= "foo" | "bar" | "baz"', 'z', 0],
    ['root ::= "foo" | "bar" | "baz"', 'f1', 1],
    ['root ::= "foo" | "bar" | "baz"', 'b1', 1],
    ['root ::= "foo" | "bar" | "baz"', 'fo1', 2],
    ['root ::= "foo" | "bar" | "baz"', 'bal', 2],
    ['root ::= "foo" | "bar" | "baz"', 'fooo', 3],
    ['root ::= "foo" | "bar" | "baz"', 'bazrr', 3],
    ['root ::= [^a]', 'a', 0],
    ['root ::= [^abc]', 'b', 0],
    ['root ::= [^a-z]', 'z', 0],
    ['root ::= [^a-zA-Z]', 'X', 0],
    ['root ::= [^a-zA-Z0-9]', '8', 0],
    ['\n  root ::= foo\n  foo ::= "foo"', '1', 0],
    ['\n  root ::= foo\n  foo ::= "foo"', 'b', 0],
    ['\n  root ::= foo\n  foo ::= "foo"', 'f1', 1],
    ['\n  root ::= foo\n  foo ::= "foo"', 'fo1', 2],
    ['\n  root ::= foo\n  foo ::= "foo"', 'fooo', 3],
    ['\n  root::=foo|"bar"\n  foo::="foo"', '1', 0],
    ['\n  root::=foo|"bar"\n  foo::="foo"', 'z', 0],
    ['\n  root::=foo|"bar"\n  foo::="foo"', 'f1', 1],
    ['\n  root::=foo|"bar"\n  foo::="foo"', 'b1', 1],
    ['\n  root::=foo|"bar"\n  foo::="foo"', 'fo1', 2],
    ['\n  root::=foo|"bar"\n  foo::="foo"', 'fooo', 3],
    ['\n  root::=foo|"bar"\n  foo::="foo"', 'barr', 3],
    ['\n  root::= foo | bar\n  foo::="foo"\n  bar::="bar"', '1', 0],
    ['\n  root::= foo | bar\n  foo::="foo"\n  bar::="bar"', 'z', 0],
    ['\n  root::= foo | bar\n  foo::="foo"\n  bar::="bar"', 'f1', 1],
    ['\n  root::= foo | bar\n  foo::="foo"\n  bar::="bar"', 'b1', 1],
    ['\n  root::= foo | bar\n  foo::="foo"\n  bar::="bar"', 'fo1', 2],
    ['\n  root::= foo | bar\n  foo::="foo"\n  bar::="bar"', 'fooo', 3],
    ['\n  root::= foo | bar\n  foo::="foo"\n  bar::="bar"', 'barr', 3],
    [
      '\n  root ::= f | b\n  f ::= fo\n  b ::= ba\n  fo ::= foo\n  ba ::= bar | baz\n  foo ::= "foo"\n  bar ::= "bar"\n  baz ::= "baz"\n  ',
      '1',
      0
    ],
    [
      '\n  root ::= f | b\n  f ::= fo\n  b ::= ba\n  fo ::= foo\n  ba ::= bar | baz\n  foo ::= "foo"\n  bar ::= "bar"\n  baz ::= "baz"',
      'z',
      0
    ],
    [
      '\n  root ::= f | b\n  f ::= fo\n  b ::= ba\n  fo ::= foo\n  ba ::= bar | baz\n  foo ::= "foo"\n  bar ::= "bar"\n  baz ::= "baz"',
      'f1',
      1
    ],
    [
      '\n  root ::= f | b\n  f ::= fo\n  b ::= ba\n  fo ::= foo\n  ba ::= bar | baz\n  foo ::= "foo"\n  bar ::= "bar"\n  baz ::= "baz"',
      'b1',
      1
    ],
    [
      '\n  root ::= f | b\n  f ::= fo\n  b ::= ba\n  fo ::= foo\n  ba ::= bar | baz\n  foo ::= "foo"\n  bar ::= "bar"\n  baz ::= "baz"',
      'fo1',
      2
    ],
    [
      '\n  root ::= f | b\n  f ::= fo\n  b ::= ba\n  fo ::= foo\n  ba ::= bar | baz\n  foo ::= "foo"\n  bar ::= "bar"\n  baz ::= "baz"',
      'fooo',
      3
    ],
    [
      '\n  root ::= f | b\n  f ::= fo\n  b ::= ba\n  fo ::= foo\n  ba ::= bar | baz\n  foo ::= "foo"\n  bar ::= "bar"\n  baz ::= "baz"',
      'barr',
      3
    ],
    [
      '\n  root ::= f | b\n  f ::= fo\n  b ::= ba\n  fo ::= foo\n  ba ::= bar | baz\n  foo ::= "foo"\n  bar ::= "bar"\n  baz ::= "baz"',
      'bazr',
      3
    ],
    ['root ::= [a-z]', 'A', 0],
    ['root ::= [a-z]', '0', 0],
    ['root ::= [a-z]', 'az', 1],
    ['root ::= [a-z]?', 'A', 0],
    ['root ::= [a-z]?', '0', 0],
    ['root ::= [a-z]?', 'az', 1],
    ['root ::= [a-z]+', 'A', 0],
    ['root ::= [a-z]+', '0', 0],
    ['root ::= [a-z]+', 'az0', 2],
    ['root ::= [a-z]*', 'A', 0],
    ['root ::= [a-z]*', '0', 0],
    ['root ::= [a-z]*', 'az0', 2],
    ['root ::= ( [^abcdefgh] | [b-z])*', 'a', 0]
  ];

describe('validate input', () => {
  it.each(VALID_INPUTS)('parses %j with the input %j', (grammar, input) => {
    const graph = GBNF(grammar, input);
    expect(Boolean(graph)).toBe(true);
  });

  it.each(INVALID_INPUTS)(
    'reports an error for the grammar %j with the invalid input %j',
    (grammar, inputText, errorPos) => {
      const graph = GBNF(grammar);
      const expected = new InputParseError(inputText, errorPos);
      const err = captureError(InputParseError, () => graph.add(inputText));
      expect(err.toString()).toBe(expected.toString());
    },
  );
});
