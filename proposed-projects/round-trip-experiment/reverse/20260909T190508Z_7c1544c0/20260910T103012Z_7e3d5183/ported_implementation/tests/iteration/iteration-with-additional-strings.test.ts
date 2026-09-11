import { describe, test, expect } from 'vitest';
import GBNF, { RuleType, InputParseError } from 'gbnf';

describe('Iteration', () => {
  test.for([
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
  ] as [string, string, string][])(
    '(%#) It throws if encountering a grammar `%s` with starting `%s` and additional `%s`',
    ([grammar, starting, additional]) => {
      const graph = GBNF(grammar, starting);
      expect(() => {
        graph.add(additional);
      }).toThrow();
    }
  );

  test.for([
    ['root ::= "foo"', '', 'f', [{ type: 'char', value: [111] }]],
    ['root ::= "foo"', 'f', 'o', [{ type: 'char', value: [111] }]],
    ['root ::= "foo"', 'fo', 'o', [{ type: 'end' }]],
    ['root ::= "foo" | "bar" ', '', 'f', [{ type: 'char', value: [111] }]],
    ['root ::= "foo" | "bar" ', 'f', 'o', [{ type: 'char', value: [111] }]],
    ['root ::= "foo" | "bar" ', 'fo', 'o', [{ type: 'end' }]],
    ['root ::= "foo" | "bar" ', '', 'b', [{ type: 'char', value: [97] }]],
    ['root ::= "foo" | "bar" ', 'b', 'a', [{ type: 'char', value: [114] }]],
    ['root ::= "foo" | "bar" ', 'ba', 'r', [{ type: 'end' }]],
    [
      'root ::= "foo" | "bar" | "baz"',
      'b',
      'a',
      [
        { type: 'char', value: [114] },
        { type: 'char', value: [122] },
      ],
    ],
    ['root ::= [^f] "o"', 'g', 'o', [{ type: 'end' }]],
    ['root ::= [^A-Z]', '', 'a', [{ type: 'end' }]],
    ['root ::= [^A-Z0-9]', '', 'a', [{ type: 'end' }]],
    ['root ::= [^A-Z0-9_-]', '', 'a', [{ type: 'end' }]],
    ['root ::= foo\nfoo ::= "foo"', '', 'f', [{ type: 'char', value: [111] }]],
    ['root ::= foo\nfoo ::= "foo"', 'f', 'o', [{ type: 'char', value: [111] }]],
    ['root ::= foo\nfoo ::= "foo"', 'fo', 'o', [{ type: 'end' }]],
    [
      'root ::= foo | "bar"\nfoo ::= "foo"',
      '',
      'f',
      [{ type: 'char', value: [111] }],
    ],
    [
      'root ::= foo | "bar"\nfoo ::= "foo"',
      'f',
      'o',
      [{ type: 'char', value: [111] }],
    ],
    ['root ::= foo | "bar"\nfoo ::= "foo"', 'fo', 'o', [{ type: 'end' }]],
    [
      'root ::= foo | "bar"\nfoo ::= "foo"',
      '',
      'b',
      [{ type: 'char', value: [97] }],
    ],
    [
      'root ::= foo | "bar"\nfoo ::= "foo"',
      'b',
      'a',
      [{ type: 'char', value: [114] }],
    ],
    ['root ::= foo | "bar"\nfoo ::= "foo"', 'ba', 'r', [{ type: 'end' }]],
    [
      'root ::= foo | bar\nfoo ::= "foo"\nbar ::= "bar"',
      '',
      'f',
      [{ type: 'char', value: [111] }],
    ],
    [
      '\nroot ::= foo | bar\nfoo ::= "foo"\nbar ::= "bar"',
      'f',
      'o',
      [{ type: 'char', value: [111] }],
    ],
    [
      '\nroot ::= foo | bar\nfoo ::= "foo"\nbar ::= "bar"',
      'fo',
      'o',
      [{ type: 'end' }],
    ],
    [
      'root ::= foo | bar\nfoo ::= "foo"\nbar ::= "bar"',
      '',
      'b',
      [{ type: 'char', value: [97] }],
    ],
    [
      'root ::= foo | bar\nfoo ::= "foo"\nbar ::= "bar"',
      'b',
      'a',
      [{ type: 'char', value: [114] }],
    ],
    [
      'root ::= foo | bar\nfoo ::= "foo"\nbar ::= "bar"',
      'ba',
      'r',
      [{ type: 'end' }],
    ],
    [
      '\nroot ::= f | b\nf ::= fo\nb ::= ba\nfo ::= foo\nba ::= bar | baz\nfoo ::= "foo"\nbar ::= "bar"\nbaz ::= "baz"',
      '',
      'f',
      [{ type: 'char', value: [111] }],
    ],
    [
      'root ::= f | b\nf ::= fo\nb ::= ba\nfo ::= foo\nba ::= bar | baz\nfoo ::= "foo"\nbar ::= "bar"\nbaz ::= "baz"',
      'f',
      'o',
      [{ type: 'char', value: [111] }],
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
      [{ type: 'char', value: [97] }],
    ],
    [
      '\nroot ::= f | b\nf ::= fo\nb ::= ba\nfo ::= foo\nba ::= bar | baz\nfoo ::= "foo"\nbar ::= "bar"\nbaz ::= "baz"',
      'b',
      'a',
      [
        { type: 'char', value: [114] },
        { type: 'char', value: [122] },
      ],
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
      [{ type: 'char', value: [[97, 122]] }, { type: 'end' }],
    ],
    [
      'root ::= [a-zA-Z]+',
      '',
      'Z',
      [
        {
          type: 'char',
          value: [
            [97, 122],
            [65, 90],
          ],
        },
        { type: 'end' },
      ],
    ],
    [
      'root ::= [a-zA-Z]+',
      'azA',
      'Z',
      [
        {
          type: 'char',
          value: [
            [97, 122],
            [65, 90],
          ],
        },
        { type: 'end' },
      ],
    ],
    [
      'root ::= [a-z]*',
      '',
      'a',
      [{ type: 'char', value: [[97, 122]] }, { type: 'end' }],
    ],
    [
      'root ::= [a-zA-Z]+',
      '',
      'Z',
      [
        {
          type: 'char',
          value: [
            [97, 122],
            [65, 90],
          ],
        },
        { type: 'end' },
      ],
    ],
    [
      'root ::= [a-zA-Z]+',
      'acczABC',
      'Z',
      [
        {
          type: 'char',
          value: [
            [97, 122],
            [65, 90],
          ],
        },
        { type: 'end' },
      ],
    ],
    [
      'root ::= "foo" | "bar" | "baz" | "bazaar" | "barrington" ',
      'baza',
      'a',
      [{ type: 'char', value: [114] }],
    ],
    [
      'root ::= [^f]+ "o"',
      'aaa',
      'a',
      [
        { type: 'char_exclude', value: [102] },
        { type: 'char', value: [111] },
      ],
    ],
    [
      'root ::= [^A-Z]+',
      'abc',
      'd',
      [{ type: 'char_exclude', value: [[65, 90]] }, { type: 'end' }],
    ],
    [
      'root ::= [^A-Z0-9]*',
      'abc',
      'd',
      [
        {
          type: 'char_exclude',
          value: [
            [65, 90],
            [48, 57],
          ],
        },
        { type: 'end' },
      ],
    ],
    [
      'root ::= [^A-Z0-9_-]*',
      'abc',
      'd',
      [
        { type: 'char_exclude', value: [[65, 90], [48, 57], 95, 45] },
        { type: 'end' },
      ],
    ],
  ] as [string, string, string, { type: string; value: number[] }[]][])(
    '(%#) It parses a grammar `%s` with starting `%s` and additional `%s`',
    async ([grammar, starting, additional, expected]) => {
      let state = GBNF(grammar, starting);
      state = state.add(additional);
      expect([...state]).toEqual(expected);
    }
  );

  test.for([false, true] as boolean[])(
    '(%#) It throws a particular error',
    async (errorForMostRecentInput) => {
      const grammar = 'root ::= "bar"';
      let state = GBNF(grammar);
      state = state.add('b');
      state = state.add('a');
      try {
        state.add('z');
        throw new Error('Expected an error to be thrown');
      } catch (err) {
        if (!(err instanceof InputParseError)) {
          throw new Error(
            'Expected an error of type InputParseError to be thrown'
          );
        }
        const expectedErr = new InputParseError('z', 0, 'ba');
        if (errorForMostRecentInput) {
          expect(err.errorForMostRecentInput).toEqual(
            expectedErr.errorForMostRecentInput
          );
        } else {
          expect(err.message).toEqual(expectedErr.message);
        }
      }
    }
  );
});
