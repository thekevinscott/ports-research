import { describe, test, expect } from 'vitest';
import GBNF, { GBNF as named, RuleType, RuleChar, RuleEnd, InputParseError, GrammarParseError } from 'gbnf';
import { Graph } from '../../src/grammar-graph/graph.js';
import { RulesBuilder } from '../../src/rules-builder/rules-builder.js';
import { buildRuleStack } from '../../src/grammar-parser/build-rule-stack.js';

describe('smoke', () => {
  test('exports', () => {
    expect(named).toBe(GBNF);
    expect(RuleType.CHAR).toBe('char');
    expect(new RuleChar([1]).type).toBe('char');
    expect(new RuleEnd().type).toBe('end');
  });

  test('parse state extras', () => {
    const state = GBNF('root ::= "foo" | "bar"');
    expect(state.size).toBe(2);
    expect(state.grammar).toBe('root ::= "foo" | "bar"');
    expect([...state.rules()]).toHaveLength(2);
    expect(() => (state as any).add(1)).toThrowError('input text must be of type string');
  });

  test('graph printing', () => {
    const g = 'root ::= [a-z] "\\n" foo\nfoo ::= "x"?';
    const rb = new RulesBuilder(g);
    const graph = new Graph(g, rb.rules.map(buildRuleStack), rb.symbolIds.get('root')!);
    const plain = graph.print();
    expect(plain).toContain('->');
    expect(plain).toContain('\\n');
    expect(plain).not.toContain('\x1b');
    expect(graph.print(undefined, true)).toContain('\x1b');
    // with live pointers
    const pointers = graph.add('');
    expect(graph.print(pointers)).toContain('*');
  });

  test('escape sequences and comments', () => {
    expect([...GBNF('# a comment\nroot ::= "\\x41" # trailing\n')]).toEqual([{ type: 'char', value: [65] }]);
    expect([...GBNF('root ::= "\\u00e9"')]).toEqual([{ type: 'char', value: [233] }]);
    expect([...GBNF('root ::= "\\U0001F600"')]).toEqual([{ type: 'char', value: [128512] }]);
    expect([...GBNF('root ::= "\\t" | "\\\\" | "\\"" | "["')]).toEqual([
      { type: 'char', value: [9] }, { type: 'char', value: [92] },
      { type: 'char', value: [34] }, { type: 'char', value: [91] },
    ]);
  });

  test('input error accessors', () => {
    let err: InputParseError | undefined;
    try { GBNF('root ::= "bar"', 'b').add('a').add('z'); } catch (e) { err = e as InputParseError; }
    expect(err).toBeInstanceOf(InputParseError);
    expect(err!.src).toBe('baz');
    expect(err!.pos).toBe(0);
    expect(err!.errorForMostRecentInput).toBe('Failed to parse input string:\n\nz\n^');
    expect(err!.message).toBe('Failed to parse input string:\n\nbaz\n  ^');
  });

  test('grammar error accessors', () => {
    const err = new GrammarParseError('root = "foo"', 5, 'Expecting ::= at 5');
    expect(err.reason).toBe('Expecting ::= at 5');
    expect(err.pos).toBe(5);
    expect(err.grammar).toBe('root = "foo"');
    expect(err).toBeInstanceOf(Error);
    expect(new GrammarParseError('', 0, 'No rules were found').message)
      .toBe('Failed to parse grammar: No rules were found\n\nNo input provided');
  });

  test('non-string arguments rejected', () => {
    expect(() => (GBNF as any)(1)).toThrowError('grammar must be a string');
    expect(() => (GBNF as any)('root ::= "a"', 1)).toThrowError('input must be a string');
  });

  test('multi-line error position', () => {
    expect(() => GBNF('root ::= foo\nfoo ::= baz\nbar ::= "bar"\n  ')).toThrowError(
      new GrammarParseError('root ::= foo\nfoo ::= baz\nbar ::= "bar"\n  ', 21, 'Undefined rule identifier "baz"'),
    );
  });
});
