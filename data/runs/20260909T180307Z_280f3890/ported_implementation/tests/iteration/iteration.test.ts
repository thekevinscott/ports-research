// Ported from the generated Python suite at tests/python.
import { describe, expect, it } from 'vitest';

import { GBNF } from '../../src/index.js';
import { type ExpectedRule, ord, toRules } from '../helpers.js';

describe('iteration', () => {
  const cases: [grammar: string, expected: ExpectedRule[]][] = [
    ['root ::= "foo"', [{ type: 'char', value: [ord('f')] }]],
    [
      'root ::= "foo" | "bar" ',
      [{ type: 'char', value: [ord('f')] }, { type: 'char', value: [ord('b')] }],
    ],
    [
      'root ::= "foo" | "bar" | "gaz"',
      [
        { type: 'char', value: [ord('f')] },
        { type: 'char', value: [ord('b')] },
        { type: 'char', value: [ord('g')] },
      ],
    ],
    [
      'root ::= "foo" | "bar" | "baz"',
      [{ type: 'char', value: [ord('f')] }, { type: 'char', value: [ord('b')] }],
    ],
    ['root ::= [^x]', [{ type: 'char_exclude', value: [ord('x')] }]],
    ['root ::= [^f] "o"', [{ type: 'char_exclude', value: [ord('f')] }]],
    ['root ::= [^A-Z]', [{ type: 'char_exclude', value: [[ord('A'), ord('Z')]] }]],
    [
      'root ::= [^A-Z0-9]',
      [{ type: 'char_exclude', value: [[ord('A'), ord('Z')], [ord('0'), ord('9')]] }],
    ],
    [
      'root ::= [^A-Z0-9_-]',
      [
        { type: 'char_exclude', value: [[ord('A'), ord('Z')], [ord('0'), ord('9')], ord('_'), ord('-')] },
      ],
    ],
    ['\nroot ::= foo\nfoo ::= "foo"\n  ', [{ type: 'char', value: [ord('f')] }]],
    ['\nroot ::= f\nf ::= foo\nfoo ::= "foo"\n  ', [{ type: 'char', value: [ord('f')] }]],
    [
      '\nroot ::= foo | "bar"\nfoo ::= "foo"',
      [{ type: 'char', value: [ord('f')] }, { type: 'char', value: [ord('b')] }],
    ],
    [
      '\nroot ::= foo | bar\nfoo ::= "foo"\nbar ::= "bar"\n  ',
      [{ type: 'char', value: [ord('f')] }, { type: 'char', value: [ord('b')] }],
    ],
    [
      '\nroot ::= f | b\nf ::= fo\nb ::= ba\nfo ::= foo\nba ::= bar | baz\nfoo ::= "foo"\nbar ::= "bar"\nbaz ::= "baz"\n  ',
      [{ type: 'char', value: [ord('f')] }, { type: 'char', value: [ord('b')] }],
    ],
    ['root ::= [a-z]', [{ type: 'char', value: [[ord('a'), ord('z')]] }]],
    ['root ::= [a-zA-Z]', [{ type: 'char', value: [[ord('a'), ord('z')], [ord('A'), ord('Z')]] }]],
    ['root ::= [a-z]?', [{ type: 'char', value: [[ord('a'), ord('z')]] }, { type: 'end' }]],
    ['root ::= [a-z]+', [{ type: 'char', value: [[ord('a'), ord('z')]] }]],
    ['root ::= [a-z]*', [{ type: 'char', value: [[ord('a'), ord('z')]] }, { type: 'end' }]],
    ['\n  root ::= "foo"\n  foo ::= "foo"', [{ type: 'char', value: [ord('f')] }]],
    [
      '\n  root  ::= (expr "=" term "")+\n  expr  ::= term ([-+*/] term)*\n  term  ::= [0-9]+\n  ',
      [{ type: 'char', value: [[ord('0'), ord('9')]] }],
    ],
  ];

  it.each(cases)('returns parse state for grammar (case %#)', (grammar, expected) => {
    expect([...GBNF(grammar)]).toStrictEqual(toRules(expected));
  });
});
