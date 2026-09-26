// Ported from the generated Python suite at tests/python.
import { describe, expect, it } from 'vitest';

import { GBNF, InputParseError } from '../../src/index.js';
import { type ExpectedRule, ord, sortRules, toRules } from '../helpers.js';

describe('iteration with additional strings', () => {
  const raisingCases: [grammar: string, starting: string, additional: string][] = [
    ['root ::= "foo"', 'f', '1'],
    ['root ::= "foo"', 'f', 'b'],
    ['root ::= "foo"', 'f', 'o1'],
    ['root ::= "foo"', 'f', 'ooo'],
    ['root ::= "foo"', 'f', 'ooooooo'],
    ['root ::= "foo" | "bar"', 'f', '1'],
    ['root ::= "foo" | "bar"', 'b', '1'],
    ['root ::= "foo" | "bar"', 'f', 'o1'],
    ['root ::= "foo" | "bar"', 'b', 'a1'],
    ['root ::= "foo" | "bar"', 'f', 'ooo'],
    ['root ::= "foo" | "bar"', 'b', 'arrr'],
    ['root ::= "foo" | "bar" | "baz"', 'f', '1'],
    ['root ::= "foo" | "bar" | "baz"', 'f', 'z'],
    ['root ::= "foo" | "bar" | "baz"', 'b', 'b1'],
    ['root ::= "foo" | "bar" | "baz"', 'f', 'o1'],
    ['root ::= "foo" | "bar" | "baz"', 'b', 'al'],
    ['root ::= "foo" | "bar" | "baz"', 'f', 'ooo'],
    ['root ::= "foo" | "bar" | "baz"', 'b', 'azrr'],
    ['root ::= foo\nfoo ::="foo"', 'f', '1'],
    ['root ::= foo\nfoo ::="foo"', 'f', 'b'],
    ['root ::= foo\nfoo ::="foo"', 'f', 'o1'],
    ['root ::= foo\nfoo ::="foo"', 'f', 'ooo'],
    ['root::=foo|"bar"\nfoo::="foo"', 'f', '1'],
    ['root::=foo|"bar"\nfoo::="foo"', 'f', 'z'],
    ['root::=foo|"bar"\nfoo::="foo"', 'b', 'b1'],
    ['root::=foo|"bar"\nfoo::="foo"', 'f', 'o1'],
    ['root::=foo|"bar"\nfoo::="foo"', 'f', 'ooo'],
    ['root::=foo|"bar"\nfoo::="foo"', 'b', 'arr'],
    ['root::= foo | bar\n foo::="foo"\n bar::="bar"', 'f', '1'],
    ['root::= foo | bar\n foo::="foo"\n bar::="bar"', 'f', 'z'],
    ['root::= foo | bar\n foo::="foo"\n bar::="bar"', 'b', '1'],
    ['root::= foo | bar\n foo::="foo"\n bar::="bar"', 'f', 'o1'],
    ['root::= foo | bar\n foo::="foo"\n bar::="bar"', 'f', 'ooo'],
    ['root::= foo | bar\n foo::="foo"\n bar::="bar"', 'b', 'arr'],
    [
      'root ::= f | b\nf ::= fo\nb ::= ba\nfo ::= foo\nba ::= bar | baz\nfoo ::= "foo"\nbar ::= "bar"\nbaz ::= "baz"',
      'f',
      '1',
    ],
    [
      'root ::= f | b\nf ::= fo\nb ::= ba\nfo ::= foo\nba ::= bar | baz\nfoo ::= "foo"\nbar ::= "bar"\nbaz ::= "baz"',
      'f',
      'z',
    ],
    [
      'root ::= f | b\nf ::= fo\nb ::= ba\nfo ::= foo\nba ::= bar | baz\nfoo ::= "foo"\nbar ::= "bar"\nbaz ::= "baz"',
      'b',
      '1',
    ],
    [
      'root ::= f | b\nf ::= fo\nb ::= ba\nfo ::= foo\nba ::= bar | baz\nfoo ::= "foo"\nbar ::= "bar"\nbaz ::= "baz"',
      'f',
      'o1',
    ],
    [
      'root ::= f | b\nf ::= fo\nb ::= ba\nfo ::= foo\nba ::= bar | baz\nfoo ::= "foo"\nbar ::= "bar"\nbaz ::= "baz"',
      'f',
      'ooo',
    ],
    [
      'root ::= f | b\nf ::= fo\nb ::= ba\nfo ::= foo\nba ::= bar | baz\nfoo ::= "foo"\nbar ::= "bar"\nbaz ::= "baz"',
      'b',
      'arr',
    ],
    [
      'root ::= f | b\nf ::= fo\nb ::= ba\nfo ::= foo\nba ::= bar | baz\nfoo ::= "foo"\nbar ::= "bar"\nbaz ::= "baz"',
      'b',
      'azr',
    ],
    ['root ::= [a-z]', 'a', 'A'],
    ['root ::= [a-z]', 'a', '0'],
    ['root ::= [a-z]', 'a', 'az'],
    ['root ::= [a-z]?', 'a', 'A'],
    ['root ::= [a-z]?', 'a', '0'],
    ['root ::= [a-z]?', 'a', 'az'],
    ['root ::= [a-z]+', 'a', 'A'],
    ['root ::= [a-z]+', 'a', '0'],
    ['root ::= [a-z]+', 'a', 'z0'],
    ['root ::= [a-z]*', 'a', 'A'],
    ['root ::= [a-z]*', 'a', '0'],
    ['root ::= [a-z]*', 'a', 'z0'],
  ];

  it.each(raisingCases)(
    'raises when encountering an invalid additional string (case %#)',
    (grammar, starting, additional) => {
      const state = GBNF(grammar, starting);
      expect(() => state.add(additional)).toThrow(InputParseError);
    },
  );

  const parsingCases: [
    grammar: string,
    starting: string,
    additional: string,
    expected: ExpectedRule[],
  ][] = [
    ['root ::= "foo"', '', 'f', [{ type: 'char', value: [ord('o')] }]],
    ['root ::= "foo"', 'f', 'o', [{ type: 'char', value: [ord('o')] }]],
    ['root ::= "foo"', 'fo', 'o', [{ type: 'end' }]],
    ['root ::= "foo" | "bar" ', '', 'f', [{ type: 'char', value: [ord('o')] }]],
    ['root ::= "foo" | "bar" ', 'f', 'o', [{ type: 'char', value: [ord('o')] }]],
    ['root ::= "foo" | "bar" ', 'fo', 'o', [{ type: 'end' }]],
    ['root ::= "foo" | "bar" ', '', 'b', [{ type: 'char', value: [ord('a')] }]],
    ['root ::= "foo" | "bar" ', 'b', 'a', [{ type: 'char', value: [ord('r')] }]],
    ['root ::= "foo" | "bar" ', 'ba', 'r', [{ type: 'end' }]],
    [
      'root ::= "foo" | "bar" | "baz"',
      'b',
      'a',
      [{ type: 'char', value: [ord('r')] }, { type: 'char', value: [ord('z')] }],
    ],
    ['root ::= [^f] "o"', 'g', 'o', [{ type: 'end' }]],
    ['root ::= [^A-Z]', '', 'a', [{ type: 'end' }]],
    ['root ::= [^A-Z0-9]', '', 'a', [{ type: 'end' }]],
    ['root ::= [^A-Z0-9_-]', '', 'a', [{ type: 'end' }]],
    ['root ::= foo\nfoo ::= "foo"', '', 'f', [{ type: 'char', value: [ord('o')] }]],
    ['root ::= foo\nfoo ::= "foo"', 'f', 'o', [{ type: 'char', value: [ord('o')] }]],
    ['root ::= foo\nfoo ::= "foo"', 'fo', 'o', [{ type: 'end' }]],
    ['root ::= foo | "bar"\nfoo ::= "foo"', '', 'f', [{ type: 'char', value: [ord('o')] }]],
    ['root ::= foo | "bar"\nfoo ::= "foo"', 'f', 'o', [{ type: 'char', value: [ord('o')] }]],
    ['root ::= foo | "bar"\nfoo ::= "foo"', 'fo', 'o', [{ type: 'end' }]],
    ['root ::= foo | "bar"\nfoo ::= "foo"', '', 'b', [{ type: 'char', value: [ord('a')] }]],
    ['root ::= foo | "bar"\nfoo ::= "foo"', 'b', 'a', [{ type: 'char', value: [ord('r')] }]],
    ['root ::= foo | "bar"\nfoo ::= "foo"', 'ba', 'r', [{ type: 'end' }]],
    [
      'root ::= foo | bar\nfoo ::= "foo"\nbar ::= "bar"',
      '',
      'f',
      [{ type: 'char', value: [ord('o')] }],
    ],
    [
      '\nroot ::= foo | bar\nfoo ::= "foo"\nbar ::= "bar"',
      'f',
      'o',
      [{ type: 'char', value: [ord('o')] }],
    ],
    ['\nroot ::= foo | bar\nfoo ::= "foo"\nbar ::= "bar"', 'fo', 'o', [{ type: 'end' }]],
    [
      'root ::= foo | bar\nfoo ::= "foo"\nbar ::= "bar"',
      '',
      'b',
      [{ type: 'char', value: [ord('a')] }],
    ],
    [
      'root ::= foo | bar\nfoo ::= "foo"\nbar ::= "bar"',
      'b',
      'a',
      [{ type: 'char', value: [ord('r')] }],
    ],
    ['root ::= foo | bar\nfoo ::= "foo"\nbar ::= "bar"', 'ba', 'r', [{ type: 'end' }]],
    [
      '\nroot ::= f | b\nf ::= fo\nb ::= ba\nfo ::= foo\nba ::= bar | baz\nfoo ::= "foo"\nbar ::= "bar"\nbaz ::= "baz"',
      '',
      'f',
      [{ type: 'char', value: [ord('o')] }],
    ],
    [
      'root ::= f | b\nf ::= fo\nb ::= ba\nfo ::= foo\nba ::= bar | baz\nfoo ::= "foo"\nbar ::= "bar"\nbaz ::= "baz"',
      'f',
      'o',
      [{ type: 'char', value: [ord('o')] }],
    ],
    [
      'root ::= f | b\nf ::= fo\nb ::= ba\nfo ::= foo\nba ::= bar | baz\nfoo ::= "foo"\nbar ::= "bar"\nbaz ::= "baz"',
      'fo',
      'o',
      [{ type: 'end' }],
    ],
    [
      'root ::= f | b\nf ::= fo\nb ::= ba\nfo ::= foo\nba ::= bar | baz\nfoo ::= "foo"\nbar ::= "bar"\nbaz ::= "baz"',
      '',
      'b',
      [{ type: 'char', value: [ord('a')] }],
    ],
    [
      '\nroot ::= f | b\nf ::= fo\nb ::= ba\nfo ::= foo\nba ::= bar | baz\nfoo ::= "foo"\nbar ::= "bar"\nbaz ::= "baz"',
      'b',
      'a',
      [{ type: 'char', value: [ord('r')] }, { type: 'char', value: [ord('z')] }],
    ],
    [
      '\nroot ::= f | b\nf ::= fo\nb ::= ba\nfo ::= foo\nba ::= bar | baz\nfoo ::= "foo"\nbar ::= "bar"\nbaz ::= "baz"',
      'ba',
      'r',
      [{ type: 'end' }],
    ],
    [
      '\nroot ::= f | b\nf ::= fo\nb ::= ba\nfo ::= foo\nba ::= bar | baz\nfoo ::= "foo"\nbar ::= "bar"\nbaz ::= "baz"',
      'ba',
      'z',
      [{ type: 'end' }],
    ],
    ['root ::= [a-z]', '', 'a', [{ type: 'end' }]],
    ['root ::= [a-z]', '', 'm', [{ type: 'end' }]],
    ['root ::= [a-z]', '', 'z', [{ type: 'end' }]],
    ['root ::= [a-zA-Z]', '', 'a', [{ type: 'end' }]],
    ['root ::= [a-zA-Z]', '', 'Z', [{ type: 'end' }]],
    ['root ::= [a-zA-Z0-9]', '', 'Z', [{ type: 'end' }]],
    ['root ::= [a-zA-Z0-9]', '', '0', [{ type: 'end' }]],
    ['root ::= [a-zA-Z0-9]', '', '9', [{ type: 'end' }]],
    ['root ::= [a-z]?', '', 'a', [{ type: 'end' }]],
    ['root ::= [a-zA-Z]?', '', 'Z', [{ type: 'end' }]],
    ['root ::= [a-zA-Z0-9]?', '', '0', [{ type: 'end' }]],
    [
      'root ::= [a-z]+',
      '',
      'a',
      [{ type: 'char', value: [[ord('a'), ord('z')]] }, { type: 'end' }],
    ],
    [
      'root ::= [a-zA-Z]+',
      '',
      'Z',
      [
        { type: 'char', value: [[ord('a'), ord('z')], [ord('A'), ord('Z')]] },
        { type: 'end' },
      ],
    ],
    [
      'root ::= [a-zA-Z]+',
      'azA',
      'Z',
      [
        { type: 'char', value: [[ord('a'), ord('z')], [ord('A'), ord('Z')]] },
        { type: 'end' },
      ],
    ],
    [
      'root ::= [a-z]*',
      '',
      'a',
      [{ type: 'char', value: [[ord('a'), ord('z')]] }, { type: 'end' }],
    ],
    [
      'root ::= [a-zA-Z]+',
      '',
      'Z',
      [
        { type: 'char', value: [[ord('a'), ord('z')], [ord('A'), ord('Z')]] },
        { type: 'end' },
      ],
    ],
    [
      'root ::= [a-zA-Z]+',
      'acczABC',
      'Z',
      [
        { type: 'char', value: [[ord('a'), ord('z')], [ord('A'), ord('Z')]] },
        { type: 'end' },
      ],
    ],
    [
      'root ::= "foo" | "bar" | "baz" | "bazaar" | "barrington" ',
      'baza',
      'a',
      [{ type: 'char', value: [ord('r')] }],
    ],
    [
      'root ::= [^f]+ "o"',
      'aaa',
      'a',
      [{ type: 'char_exclude', value: [ord('f')] }, { type: 'char', value: [ord('o')] }],
    ],
    [
      'root ::= [^A-Z]+',
      'abc',
      'd',
      [{ type: 'char_exclude', value: [[ord('A'), ord('Z')]] }, { type: 'end' }],
    ],
    [
      'root ::= [^A-Z0-9]*',
      'abc',
      'd',
      [
        { type: 'char_exclude', value: [[ord('A'), ord('Z')], [ord('0'), ord('9')]] },
        { type: 'end' },
      ],
    ],
    [
      'root ::= [^A-Z0-9_-]*',
      'abc',
      'd',
      [
        { type: 'char_exclude', value: [[ord('A'), ord('Z')], [ord('0'), ord('9')], ord('_'), ord('-')] },
        { type: 'end' },
      ],
    ],
  ];

  it.each(parsingCases)(
    'parses a grammar with starting and additional strings (case %#)',
    (grammar, starting, additional, expected) => {
      const state = GBNF(grammar, starting).add(additional);
      expect(sortRules(state)).toStrictEqual(sortRules(toRules(expected)));
    },
  );

  it.each([[false], [true]])(
    'raises a particular error (errorForMostRecentInput: %s)',
    errorForMostRecentInput => {
      const grammar = 'root ::= "bar"';
      const state = GBNF(grammar).add('b').add('a');
      const expectedError = new InputParseError('z', 0, 'ba');
      try {
        state.add('z');
        expect.unreachable('expected add to throw');
      } catch (err) {
        expect(err).toBeInstanceOf(InputParseError);
        if (errorForMostRecentInput) {
          expect((err as InputParseError).errorForMostRecentInput).toBe(
            expectedError.errorForMostRecentInput,
          );
        } else {
          expect((err as InputParseError).message).toBe(expectedError.message);
        }
      }
    },
  );
});
