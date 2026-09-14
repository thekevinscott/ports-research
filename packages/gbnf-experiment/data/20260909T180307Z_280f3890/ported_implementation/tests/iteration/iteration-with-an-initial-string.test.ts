// Ported from the generated Python suite at tests/python.
import { describe, expect, it } from 'vitest';

import { GBNF } from '../../src/index.js';
import { type ExpectedRule, ord, sortRules, toRules } from '../helpers.js';

describe('iteration with an initial string', () => {
  const cases: [grammar: string, inputString: string, expected: ExpectedRule[]][] = [
    ['root ::= "foo"', '', [{ type: 'char', value: [ord('f')] }]],
    ['root ::= "foo"', 'f', [{ type: 'char', value: [ord('o')] }]],
    ['root ::= "foo"', 'fo', [{ type: 'char', value: [ord('o')] }]],
    ['root ::= "foo"', 'foo', [{ type: 'end' }]],
    [
      'root ::= "foo" | "bar" ',
      '',
      [{ type: 'char', value: [ord('f')] }, { type: 'char', value: [ord('b')] }],
    ],
    ['root ::= "foo" | "bar" ', 'f', [{ type: 'char', value: [ord('o')] }]],
    ['root ::= "foo" | "bar" ', 'fo', [{ type: 'char', value: [ord('o')] }]],
    ['root ::= "foo" | "bar" ', 'foo', [{ type: 'end' }]],
    ['root ::= "foo" | "bar" ', 'b', [{ type: 'char', value: [ord('a')] }]],
    ['root ::= "foo" | "bar" ', 'ba', [{ type: 'char', value: [ord('r')] }]],
    ['root ::= "foo" | "bar" ', 'bar', [{ type: 'end' }]],
    [
      'root ::= "foo" | "bar" | "baz"',
      'ba',
      [{ type: 'char', value: [ord('r')] }, { type: 'char', value: [ord('z')] }],
    ],
    ['root ::= "["', '[', [{ type: 'end' }]],
    ['root ::= "]"', ']', [{ type: 'end' }]],
    ['root ::= "[]"', '[]', [{ type: 'end' }]],
    ['root ::= "{"', '{', [{ type: 'end' }]],
    ['root ::= "}"', '}', [{ type: 'end' }]],
    ['root ::= "{}"', '{}', [{ type: 'end' }]],
    ['root ::= "[{}]"', '[{}]', [{ type: 'end' }]],
    ['root ::= [^f] "o"', '', [{ type: 'char_exclude', value: [ord('f')] }]],
    ['root ::= [^f] "o"', 'a', [{ type: 'char', value: [ord('o')] }]],
    ['root ::= [^A-Z]', '', [{ type: 'char_exclude', value: [[ord('A'), ord('Z')]] }]],
    [
      'root ::= [^A-Z0-9]',
      '',
      [{ type: 'char_exclude', value: [[ord('A'), ord('Z')], [ord('0'), ord('9')]] }],
    ],
    [
      'root ::= [^A-Z0-9_-]',
      '',
      [
        { type: 'char_exclude', value: [[ord('A'), ord('Z')], [ord('0'), ord('9')], ord('_'), ord('-')] },
      ],
    ],
    ['\nroot ::= foo\nfoo ::= "foo"', '', [{ type: 'char', value: [ord('f')] }]],
    ['root ::= foo\nfoo ::= "foo"\n', 'f', [{ type: 'char', value: [ord('o')] }]],
    ['\nroot ::= foo\nfoo ::= "foo"\n', 'fo', [{ type: 'char', value: [ord('o')] }]],
    ['root ::= foo\nfoo ::= "foo"', 'foo', [{ type: 'end' }]],
    ['root ::= f\nf ::= foo\nfoo ::= "foo"', '', [{ type: 'char', value: [ord('f')] }]],
    [
      '\nroot ::= foo | "bar"\nfoo ::= "foo"\n',
      '',
      [{ type: 'char', value: [ord('f')] }, { type: 'char', value: [ord('b')] }],
    ],
    ['\nroot ::= foo | "bar"\nfoo ::= "foo"', 'f', [{ type: 'char', value: [ord('o')] }]],
    ['root ::= foo | "bar"\nfoo ::= "foo"', 'fo', [{ type: 'char', value: [ord('o')] }]],
    ['root ::= foo | "bar"\nfoo ::= "foo"', 'foo', [{ type: 'end' }]],
    ['root ::= foo | "bar"\nfoo ::= "foo"', 'b', [{ type: 'char', value: [ord('a')] }]],
    ['root ::= foo | "bar"\nfoo ::= "foo"', 'ba', [{ type: 'char', value: [ord('r')] }]],
    ['root ::= foo | "bar"\nfoo ::= "foo"', 'bar', [{ type: 'end' }]],
    [
      '\nroot ::= foo | bar\nfoo ::= "foo"\nbar ::= "bar"',
      '',
      [{ type: 'char', value: [ord('f')] }, { type: 'char', value: [ord('b')] }],
    ],
    [
      '\nroot ::= foo | bar\nfoo ::= "foo"\nbar ::= "bar"',
      'f',
      [{ type: 'char', value: [ord('o')] }],
    ],
    [
      '\nroot ::= foo | bar\nfoo ::= "foo"\nbar ::= "bar"',
      'fo',
      [{ type: 'char', value: [ord('o')] }],
    ],
    ['\nroot ::= foo | bar\nfoo ::= "foo"\nbar ::= "bar"', 'foo', [{ type: 'end' }]],
    [
      '\nroot ::= foo | bar\nfoo ::= "foo"\nbar ::= "bar"',
      'b',
      [{ type: 'char', value: [ord('a')] }],
    ],
    [
      '\nroot ::= foo | bar\nfoo ::= "foo"\nbar ::= "bar"',
      'ba',
      [{ type: 'char', value: [ord('r')] }],
    ],
    ['\nroot ::= foo | bar\nfoo ::= "foo"\nbar ::= "bar"', 'bar', [{ type: 'end' }]],
    [
      '\nroot ::= f | b\nf ::= fo\nb ::= ba\nfo ::= foo\nba ::= bar | baz\nfoo ::= "foo"\nbar ::= "bar"\nbaz ::= "baz"',
      '',
      [{ type: 'char', value: [ord('f')] }, { type: 'char', value: [ord('b')] }],
    ],
    [
      '\nroot ::= f | b\nf ::= fo\nb ::= ba\nfo ::= foo\nba ::= bar | baz\nfoo ::= "foo"\nbar ::= "bar"\nbaz ::= "baz"',
      'f',
      [{ type: 'char', value: [ord('o')] }],
    ],
    [
      '\nroot ::= f | b\nf ::= fo\nb ::= ba\nfo ::= foo\nba ::= bar | baz\nfoo ::= "foo"\nbar ::= "bar"\nbaz ::= "baz"',
      'fo',
      [{ type: 'char', value: [ord('o')] }],
    ],
    [
      '\nroot ::= f | b\nf ::= fo\nb ::= ba\nfo ::= foo\nba ::= bar | baz\nfoo ::= "foo"\nbar ::= "bar"\nbaz ::= "baz"',
      'foo',
      [{ type: 'end' }],
    ],
    [
      '\nroot ::= f | b\nf ::= fo\nb ::= ba\nfo ::= foo\nba ::= bar | baz\nfoo ::= "foo"\nbar ::= "bar"\nbaz ::= "baz"',
      'b',
      [{ type: 'char', value: [ord('a')] }],
    ],
    [
      '\nroot ::= f | b\nf ::= fo\nb ::= ba\nfo ::= foo\nba ::= bar | baz\nfoo ::= "foo"\nbar ::= "bar"\nbaz ::= "baz"',
      'ba',
      [{ type: 'char', value: [ord('r')] }, { type: 'char', value: [ord('z')] }],
    ],
    [
      '\nroot ::= f | b\nf ::= fo\nb ::= ba\nfo ::= foo\nba ::= bar | baz\nfoo ::= "foo"\nbar ::= "bar"\nbaz ::= "baz"',
      'bar',
      [{ type: 'end' }],
    ],
    [
      '\nroot ::= f | b\nf ::= fo\nb ::= ba\nfo ::= foo\nba ::= bar | baz\nfoo ::= "foo"\nbar ::= "bar"\nbaz ::= "baz"',
      'baz',
      [{ type: 'end' }],
    ],
    ['root ::= [a-z]', '', [{ type: 'char', value: [[ord('a'), ord('z')]] }]],
    [
      'root ::= [a-zA-Z]',
      '',
      [{ type: 'char', value: [[ord('a'), ord('z')], [ord('A'), ord('Z')]] }],
    ],
    ['root ::= [a-z]', 'a', [{ type: 'end' }]],
    ['root ::= [a-z]', 'm', [{ type: 'end' }]],
    ['root ::= [a-z]', 'z', [{ type: 'end' }]],
    ['root ::= [a-zA-Z]', 'a', [{ type: 'end' }]],
    ['root ::= [a-zA-Z]', 'Z', [{ type: 'end' }]],
    ['root ::= [a-zA-Z0-9]', 'Z', [{ type: 'end' }]],
    ['root ::= [a-zA-Z0-9]', '0', [{ type: 'end' }]],
    ['root ::= [a-zA-Z0-9]', '9', [{ type: 'end' }]],
    ['root ::= [a-z]?', '', [{ type: 'char', value: [[ord('a'), ord('z')]] }, { type: 'end' }]],
    ['root ::= [a-z]?', 'a', [{ type: 'end' }]],
    ['root ::= [a-zA-Z]?', 'Z', [{ type: 'end' }]],
    ['root ::= [a-zA-Z0-9]?', '0', [{ type: 'end' }]],
    ['root ::= [a-z]+', '', [{ type: 'char', value: [[ord('a'), ord('z')]] }]],
    ['root ::= [a-z]+', 'l', [{ type: 'char', value: [[ord('a'), ord('z')]] }, { type: 'end' }]],
    [
      'root ::= [a-zA-Z]+',
      'Z',
      [
        { type: 'char', value: [[ord('a'), ord('z')], [ord('A'), ord('Z')]] },
        { type: 'end' },
      ],
    ],
    [
      'root ::= [a-zA-Z]+',
      'aZ',
      [
        { type: 'char', value: [[ord('a'), ord('z')], [ord('A'), ord('Z')]] },
        { type: 'end' },
      ],
    ],
    [
      'root ::= [a-zA-Z]+',
      'azAZ',
      [
        { type: 'char', value: [[ord('a'), ord('z')], [ord('A'), ord('Z')]] },
        { type: 'end' },
      ],
    ],
    ['root ::= [a-z]*', '', [{ type: 'char', value: [[ord('a'), ord('z')]] }, { type: 'end' }]],
    ['root ::= [a-z]*', 'a', [{ type: 'char', value: [[ord('a'), ord('z')]] }, { type: 'end' }]],
    [
      'root ::= [a-zA-Z]+',
      'Z',
      [
        { type: 'char', value: [[ord('a'), ord('z')], [ord('A'), ord('Z')]] },
        { type: 'end' },
      ],
    ],
    [
      'root ::= [a-zA-Z]+',
      'abczABCZ',
      [
        { type: 'char', value: [[ord('a'), ord('z')], [ord('A'), ord('Z')]] },
        { type: 'end' },
      ],
    ],
    [
      'root ::= [^f]+ "o"',
      'aaa',
      [{ type: 'char_exclude', value: [ord('f')] }, { type: 'char', value: [ord('o')] }],
    ],
    [
      'root ::= [^A-Z]+',
      'abc',
      [{ type: 'char_exclude', value: [[ord('A'), ord('Z')]] }, { type: 'end' }],
    ],
    [
      'root ::= [^A-Z0-9]*',
      'abc',
      [
        { type: 'char_exclude', value: [[ord('A'), ord('Z')], [ord('0'), ord('9')]] },
        { type: 'end' },
      ],
    ],
    [
      'root ::= [^A-Z0-9_-]*',
      'abc',
      [
        { type: 'char_exclude', value: [[ord('A'), ord('Z')], [ord('0'), ord('9')], ord('_'), ord('-')] },
        { type: 'end' },
      ],
    ],
    [
      '\nroot ::= [a-z] | xyx\nxyx ::= "foo"',
      'f',
      [{ type: 'end' }, { type: 'char', value: [ord('o')] }],
    ],
    [
      'root ::= "foo" | "bar" | "baz" | "bazaar" | "barrington" ',
      'bazaa',
      [{ type: 'char', value: [ord('r')] }],
    ],
    ['root ::= ("bar" | "foo") "zyx"', 'bar', [{ type: 'char', value: [ord('z')] }]],
    [
      'root ::= "z" ("bar" | "foo") "zzzz"',
      'z',
      [{ type: 'char', value: [ord('b')] }, { type: 'char', value: [ord('f')] }],
    ],
    ['root ::= "z" ("bar" | "foo") "zzz"', 'zbar', [{ type: 'char', value: [ord('z')] }]],
    [
      '\nroot  ::= termz ([-+*/] termz)* \ntermz  ::= [0-9]+',
      '1',
      [
        { type: 'char', value: [[ord('0'), ord('9')]] },
        { type: 'char', value: [ord('-'), ord('+'), ord('*'), ord('/')] },
        { type: 'end' },
      ],
    ],
    [
      '\nroot  ::= expr "=" termy  \nexpr  ::= termy ([-+*/] termy)*\ntermy  ::= [0-9]+',
      '1',
      [
        { type: 'char', value: [[ord('0'), ord('9')]] },
        { type: 'char', value: [ord('-'), ord('+'), ord('*'), ord('/')] },
        { type: 'char', value: [ord('=')] },
      ],
    ],
    [
      '\nroot  ::= (expr "=" terma "\n")+\nexpr  ::= terma ([-+*/] terma)*\nterma  ::= [0-9]+',
      '1',
      [
        { type: 'char', value: [[ord('0'), ord('9')]] },
        { type: 'char', value: [ord('-'), ord('+'), ord('*'), ord('/')] },
        { type: 'char', value: [ord('=')] },
      ],
    ],
    [
      'root  ::= (expr "=" termb "\n")+\nexpr  ::= termb ([-+*/] termb)*\ntermb  ::= [0-9]+',
      '1+',
      [{ type: 'char', value: [[ord('0'), ord('9')]] }],
    ],
    [
      '\nroot  ::= (expr "=" termc "\n")+\nexpr  ::= termc ([-+*/] termc)*\ntermc  ::= [0-9]+',
      '1=',
      [{ type: 'char', value: [[ord('0'), ord('9')]] }],
    ],
    [
      'root  ::= (expr "=" termd "\n")+\nexpr  ::= termd ([-+*/] termd)*\ntermd  ::= [0-9]+',
      '1+1',
      [
        { type: 'char', value: [[ord('0'), ord('9')]] },
        { type: 'char', value: [ord('-'), ord('+'), ord('*'), ord('/')] },
        { type: 'char', value: [ord('=')] },
      ],
    ],
    [
      'root  ::= (expr "=" term "\n")+\nexpr  ::= term ([-+*/] term)*\nterm  ::= [0-9]+',
      '1=1',
      [{ type: 'char', value: [[ord('0'), ord('9')]] }, { type: 'char', value: [10] }],
    ],
    [
      'root ::= "\\"" ( [^\\"abcdefghA-Z])* ',
      '"is not only in its lyrism, its vow to sustin it in its poo-sion, its r,v:l\'y, it\'s tory,',
      [
        { type: 'char_exclude', value: [ord('"'), ord('a'), ord('b'), ord('c'), ord('d'), ord('e'), ord('f'), ord('g'), ord('h'), [ord('A'), ord('Z')]] },
        { type: 'end' },
      ],
    ],
    [
      'root ::= ( [^abcdefgh] | [b-z])* ',
      'bcdefghzyxw0123ABCZ',
      [
        { type: 'char_exclude', value: [ord('a'), ord('b'), ord('c'), ord('d'), ord('e'), ord('f'), ord('g'), ord('h')] },
        { type: 'char', value: [[ord('b'), ord('z')]] },
        { type: 'end' },
      ],
    ],
  ];

  it.each(cases)(
    'returns parse state for grammar and initial string (case %#)',
    (grammar, inputString, expected) => {
      const state = GBNF(grammar).add(inputString);
      expect(sortRules(state)).toStrictEqual(sortRules(toRules(expected)));
    },
  );
});
