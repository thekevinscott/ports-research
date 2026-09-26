import { describe, expect, test } from 'vitest';

import GBNF, {
  GrammarParseError,
  InputParseError,
  ParseState,
  RuleChar,
  RuleCharExclude,
  RuleEnd,
  RuleType,
} from '../index.ts';

const codePoints = (text: string): number[] =>
  Array.from(text).map((c) => c.codePointAt(0) as number);

/** The rules a parse state will accept next, in a comparable form. */
const rules = (state: ParseState): string[] =>
  Array.from(state)
    .map((rule) => JSON.stringify(rule.toJSON()))
    .sort();

describe('GBNF', () => {
  test('parses a grammar and reports the first acceptable rule', () => {
    const state = GBNF('root ::= "foo"');
    expect(state).toBeInstanceOf(ParseState);
    expect(rules(state)).toEqual([JSON.stringify({ type: 'char', value: codePoints('f') })]);
    expect(state.size).toBe(1);
    expect(state.grammar).toBe('root ::= "foo"');
  });

  test('accepts an initial string', () => {
    const state = GBNF('root ::= "foo"', 'fo');
    expect(rules(state)).toEqual([JSON.stringify({ type: 'char', value: codePoints('o') })]);
  });

  test('walks the grammar one chunk at a time', () => {
    let state = GBNF('root ::= "foo"');
    state = state.add('f');
    state = state.add('o');
    state = state.add('o');
    const [rule] = Array.from(state);
    expect(rule).toBeInstanceOf(RuleEnd);
    expect(rule.type).toBe(RuleType.END);
  });

  test('returns a new parse state rather than mutating the current one', () => {
    const state = GBNF('root ::= "foo"');
    const next = state.add('f');
    expect(next).not.toBe(state);
    expect(rules(state)).toEqual([JSON.stringify({ type: 'char', value: codePoints('f') })]);
    expect(rules(next)).toEqual([JSON.stringify({ type: 'char', value: codePoints('o') })]);
  });

  test('is iterable', () => {
    const state = GBNF('root ::= "a" | "b"');
    const found = [...state].flatMap((rule) => (rule as RuleChar).value as number[]);
    expect(found.sort()).toEqual(codePoints('ab'));
  });

  test('collapses character classes into ranges', () => {
    const [rule] = Array.from(GBNF('root ::= [a-z]'));
    expect(rule).toBeInstanceOf(RuleChar);
    expect((rule as RuleChar).value).toEqual([[97, 122]]);
  });

  test('supports excluded character classes', () => {
    const [rule] = Array.from(GBNF('root ::= [^a-z]'));
    expect(rule).toBeInstanceOf(RuleCharExclude);
    expect(rule.type).toBe(RuleType.CHAR_EXCLUDE);
    expect((rule as RuleCharExclude).value).toEqual([[97, 122]]);
    expect(() => GBNF('root ::= [^a-z]', 'q')).toThrowError(InputParseError);
    expect(() => GBNF('root ::= [^a-z]', 'Q')).not.toThrow();
  });

  test('handles characters outside the basic multilingual plane', () => {
    expect(() => GBNF('root ::= [^a-z]', '😀')).not.toThrow();
    expect(GBNF('root ::= [^a-z]', '😀').size).toBe(1);
  });

  test('follows rule references', () => {
    const state = GBNF('root ::= foo\nfoo ::= "bar"');
    expect(rules(state)).toEqual([JSON.stringify({ type: 'char', value: codePoints('b') })]);
  });

  test('parses a JSON grammar', () => {
    const grammar = `
      root   ::= object
      value  ::= object | array | string | number | ("true" | "false" | "null") ws
      object ::=
        "{" ws (
                  string ":" ws value
          ("," ws string ":" ws value)*
        )? "}" ws
      array  ::=
        "[" ws (
                  value
          ("," ws value)*
        )? "]" ws
      string  ::=
        "\\"" (
          [^"\\\\] |
          "\\\\" (["\\\\/bfnrt] | "u" [0-9a-fA-F] [0-9a-fA-F] [0-9a-fA-F] [0-9a-fA-F])
        )* "\\"" ws
      number  ::= ("-"? ([0-9] | [1-9] [0-9]*)) ("." [0-9]+)? ([eE] [-+]? [0-9]+)? ws
      ws ::= ([ \\t\\n] ws)?
      `;
    let state = GBNF(grammar);
    for (const char of '{"key": [1, 2.5, true, null]}') {
      state = state.add(char);
    }
    expect(state.size).toBeGreaterThan(0);
    expect(() => GBNF(grammar, '{]')).toThrowError(InputParseError);
  });

  test('ignores comments and blank lines', () => {
    const state = GBNF('# a comment\nroot ::= "foo" # another comment\n');
    expect(rules(state)).toEqual([JSON.stringify({ type: 'char', value: codePoints('f') })]);
  });

  test('prints the graph', () => {
    const graph = GBNF('root ::= "ab"').graph;
    expect(graph.print()).toBe('{0,0,0}[a]-> {0,0,1}[b]-> {0,0,2}end');
    expect(graph.print(undefined, true)).toContain('\x1b[');
  });
});

describe('errors', () => {
  test('rejects a grammar with no rules', () => {
    expect(() => GBNF('')).toThrowError(GrammarParseError);
    expect(() => GBNF('')).toThrowError(/No rules were found/);
  });

  test('rejects a grammar with no root rule', () => {
    expect(() => GBNF('foo ::= "bar"')).toThrowError(/does not contain a 'root' symbol/);
  });

  test('reports undefined rule identifiers with their position', () => {
    try {
      GBNF('root ::= foo');
      throw new Error('expected GBNF to throw');
    } catch (err) {
      expect(err).toBeInstanceOf(GrammarParseError);
      const error = err as GrammarParseError;
      expect(error.reason).toBe('Undefined rule identifier "foo"');
      expect(error.message).toBe(
        [
          'Failed to parse grammar: Undefined rule identifier "foo"',
          '',
          'root ::= foo',
          '         ^',
        ].join('\n'),
      );
    }
  });

  test('reports where the input stopped matching', () => {
    try {
      GBNF('root ::= "foo"', 'fob');
      throw new Error('expected GBNF to throw');
    } catch (err) {
      expect(err).toBeInstanceOf(InputParseError);
      const error = err as InputParseError;
      expect(error.pos).toBe(2);
      expect(error.src).toBe('fob');
      expect(error.message).toBe(['Failed to parse input string:', '', 'fob', '  ^'].join('\n'));
    }
  });

  test('reports the position within the most recent input', () => {
    const state = GBNF('root ::= "foo"', 'f');
    try {
      state.add('a');
      throw new Error('expected add to throw');
    } catch (err) {
      expect(err).toBeInstanceOf(InputParseError);
      const error = err as InputParseError;
      expect(error.errorForMostRecentInput).toBe(
        ['Failed to parse input string:', '', 'a', '^'].join('\n'),
      );
      expect(error.message).toBe(['Failed to parse input string:', '', 'fa', ' ^'].join('\n'));
    }
  });

  test('rejects non-string arguments', () => {
    expect(() => GBNF(42 as unknown as string)).toThrowError('grammar must be a string');
    expect(() => GBNF('root ::= "foo"', 42 as unknown as string)).toThrowError(
      'input must be a string',
    );
    expect(() => GBNF('root ::= "foo"').add(42 as unknown as string)).toThrowError(
      'input text must be of type string',
    );
  });
});
