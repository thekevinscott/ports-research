import { describe, expect, test } from 'vitest';
import {
  RuleChar,
  RuleCharExclude,
  RuleEnd,
  type Range,
  type UnresolvedRule,
} from '../../../src/grammar-graph/grammar-graph-types.ts';
import { RuleRef } from '../../../src/grammar-graph/rule-ref.ts';
import { buildRuleStack } from '../../../src/grammar-parser/build-rule-stack.ts';
import {
  InternalRuleDefAlt,
  InternalRuleDefChar,
  InternalRuleDefCharAlt,
  InternalRuleDefCharNot,
  InternalRuleDefCharRngUpper,
  InternalRuleDefEnd,
  InternalRuleDefReference,
  type InternalRuleDef,
} from '../../../src/rules-builder/rules-builder-types.ts';

const ichar = (value: number[]): InternalRuleDef => new InternalRuleDefChar(value);
const icharAlt = (value: number): InternalRuleDef => new InternalRuleDefCharAlt(value);
const icharRngUpper = (value: number): InternalRuleDef => new InternalRuleDefCharRngUpper(value);
const icharNot = (value: number[]): InternalRuleDef => new InternalRuleDefCharNot(value);
const ialt = (): InternalRuleDef => new InternalRuleDefAlt();
const iend = (): InternalRuleDef => new InternalRuleDefEnd();
const iref = (value: number): InternalRuleDef => new InternalRuleDefReference(value);

const cp = (char: string): number => char.codePointAt(0) as number;

const makeRange = (lower: number | string, upper: number | string): Range => [
  typeof lower === 'number' ? lower : cp(lower),
  typeof upper === 'number' ? upper : cp(upper),
];

describe('build_rule_stack', () => {
  test('it builds rule stack for a single path', () => {
    expect(buildRuleStack([ichar([120])])).toStrictEqual([
      [new RuleChar([120]), new RuleEnd()],
    ]);
  });

  test('it builds rule stack for two alternate paths', () => {
    expect(buildRuleStack([
      ichar([cp('x')]),
      ialt(),
      ichar([cp('y')]),
    ])).toStrictEqual([
      [new RuleChar([cp('x')]), new RuleEnd()],
      [new RuleChar([cp('y')]), new RuleEnd()],
    ]);
  });

  test('it builds rule stack for three alternate paths', () => {
    expect(buildRuleStack([
      ichar([cp('x')]),
      ialt(),
      ichar([cp('y')]),
      ialt(),
      ichar([cp('z')]),
    ])).toStrictEqual([
      [new RuleChar([cp('x')]), new RuleEnd()],
      [new RuleChar([cp('y')]), new RuleEnd()],
      [new RuleChar([cp('z')]), new RuleEnd()],
    ]);
  });

  test('it builds rule stack for char not', () => {
    expect(buildRuleStack([
      icharNot([cp('x')]),
      ialt(),
      icharNot([cp('y')]),
      ialt(),
      icharNot([cp('z')]),
    ])).toStrictEqual([
      [new RuleCharExclude([cp('x')]), new RuleEnd()],
      [new RuleCharExclude([cp('y')]), new RuleEnd()],
      [new RuleCharExclude([cp('z')]), new RuleEnd()],
    ]);
  });

  test('it builds rule stack for mixed char and char not', () => {
    expect(buildRuleStack([
      icharNot([cp('x')]),
      ialt(),
      ichar([cp('y')]),
      ialt(),
      icharNot([cp('z')]),
    ])).toStrictEqual([
      [new RuleCharExclude([cp('x')]), new RuleEnd()],
      [new RuleChar([cp('y')]), new RuleEnd()],
      [new RuleCharExclude([cp('z')]), new RuleEnd()],
    ]);
  });

  test('it builds rule stack for char not with two characters and a range', () => {
    expect(buildRuleStack([
      icharNot([cp('x')]),
      icharAlt(cp('y')),
      icharAlt(cp('z')),
      icharRngUpper(130),
    ])).toStrictEqual([
      [new RuleCharExclude([120, 121, makeRange(122, 130)]), new RuleEnd()],
    ]);
  });

  describe('ranges', () => {
    test.each([
      [
        '[a-z]',
        [ichar([cp('a')]), icharRngUpper(cp('z')), iend()],
        [[new RuleChar([makeRange('a', 'z')]), new RuleEnd()]],
      ],
      [
        '[a-zA-Z]',
        [
          ichar([cp('a')]),
          icharRngUpper(cp('z')),
          icharAlt(cp('A')),
          icharRngUpper(cp('Z')),
          iend(),
        ],
        [[new RuleChar([makeRange('a', 'z'), makeRange('A', 'Z')]), new RuleEnd()]],
      ],
      [
        '[a-zA-Z0-9]',
        [
          ichar([cp('a')]),
          icharRngUpper(cp('z')),
          icharAlt(cp('A')),
          icharRngUpper(cp('Z')),
          icharAlt(cp('0')),
          icharRngUpper(cp('9')),
          iend(),
        ],
        [[
          new RuleChar([makeRange('a', 'z'), makeRange('A', 'Z'), makeRange('0', '9')]),
          new RuleEnd(),
        ]],
      ],
    ] as [string, InternalRuleDef[], UnresolvedRule[][]][])(
      'it builds rule stack for a char with no modifiers: %s',
      (_grammar, input, expected) => {
        expect(buildRuleStack(input)).toStrictEqual(expected);
      },
    );
  });

  test.each([
    [
      '[a-z]?',
      [ichar([cp('a')]), icharRngUpper(cp('z')), ialt(), iend()],
      [
        [new RuleChar([makeRange('a', 'z')]), new RuleEnd()],
        [new RuleEnd()],
      ],
    ],
    [
      '[a-zA-Z]?',
      [
        ichar([cp('a')]),
        icharRngUpper(cp('z')),
        icharAlt(cp('A')),
        icharRngUpper(cp('Z')),
        ialt(),
        iend(),
      ],
      [
        [new RuleChar([makeRange('a', 'z'), makeRange('A', 'Z')]), new RuleEnd()],
        [new RuleEnd()],
      ],
    ],
    [
      '[a-zA-Z0-9]?',
      [
        ichar([cp('a')]),
        icharRngUpper(cp('z')),
        icharAlt(cp('A')),
        icharRngUpper(cp('Z')),
        icharAlt(cp('0')),
        icharRngUpper(cp('9')),
        ialt(),
        iend(),
      ],
      [
        [
          new RuleChar([makeRange('a', 'z'), makeRange('A', 'Z'), makeRange('0', '9')]),
          new RuleEnd(),
        ],
        [new RuleEnd()],
      ],
    ],
  ] as [string, InternalRuleDef[], UnresolvedRule[][]][])(
    'it builds rule stack for a char with question mark modifier: %s',
    (_grammar, input, expected) => {
      expect(buildRuleStack(input)).toStrictEqual(expected);
    },
  );

  test.each([
    [
      '[a-z]+',
      [
        ichar([cp('a')]),
        icharRngUpper(cp('z')),
        iref(1),
        ialt(),
        ichar([cp('a')]),
        icharRngUpper(cp('z')),
        iend(),
      ],
      [
        [new RuleChar([makeRange('a', 'z')]), new RuleRef(1), new RuleEnd()],
        [new RuleChar([makeRange('a', 'z')]), new RuleEnd()],
      ],
    ],
    [
      '[a-zA-Z]+',
      [
        ichar([cp('a')]),
        icharRngUpper(cp('z')),
        icharAlt(cp('A')),
        icharRngUpper(cp('Z')),
        iref(1),
        ialt(),
        ichar([cp('a')]),
        icharRngUpper(cp('z')),
        icharAlt(cp('A')),
        icharRngUpper(cp('Z')),
        iend(),
      ],
      [
        [
          new RuleChar([makeRange('a', 'z'), makeRange('A', 'Z')]),
          new RuleRef(1),
          new RuleEnd(),
        ],
        [new RuleChar([makeRange('a', 'z'), makeRange('A', 'Z')]), new RuleEnd()],
      ],
    ],
    [
      '[a-zA-Z0-9]+',
      [
        ichar([cp('a')]),
        icharRngUpper(cp('z')),
        icharAlt(cp('A')),
        icharRngUpper(cp('Z')),
        icharAlt(cp('0')),
        icharRngUpper(cp('9')),
        iref(1),
        ialt(),
        ichar([cp('a')]),
        icharRngUpper(cp('z')),
        icharAlt(cp('A')),
        icharRngUpper(cp('Z')),
        icharAlt(cp('0')),
        icharRngUpper(cp('9')),
        iend(),
      ],
      [
        [
          new RuleChar([makeRange('a', 'z'), makeRange('A', 'Z'), makeRange('0', '9')]),
          new RuleRef(1),
          new RuleEnd(),
        ],
        [
          new RuleChar([makeRange('a', 'z'), makeRange('A', 'Z'), makeRange('0', '9')]),
          new RuleEnd(),
        ],
      ],
    ],
  ] as [string, InternalRuleDef[], UnresolvedRule[][]][])(
    'it builds rule stack for a char with plus modifier: %s',
    (_grammar, input, expected) => {
      expect(buildRuleStack(input)).toStrictEqual(expected);
    },
  );

  test.each([
    [
      '[a-z]*',
      [ichar([cp('a')]), icharRngUpper(cp('z')), iref(1), ialt(), iend()],
      [
        [new RuleChar([makeRange('a', 'z')]), new RuleRef(1), new RuleEnd()],
        [new RuleEnd()],
      ],
    ],
    [
      '[a-zA-Z]*',
      [
        ichar([cp('a')]),
        icharRngUpper(cp('z')),
        icharAlt(cp('A')),
        icharRngUpper(cp('Z')),
        iref(1),
        ialt(),
        iend(),
      ],
      [
        [
          new RuleChar([makeRange('a', 'z'), makeRange('A', 'Z')]),
          new RuleRef(1),
          new RuleEnd(),
        ],
        [new RuleEnd()],
      ],
    ],
    [
      '[a-zA-Z0-9]*',
      [
        ichar([cp('a')]),
        icharRngUpper(cp('z')),
        icharAlt(cp('A')),
        icharRngUpper(cp('Z')),
        icharAlt(cp('0')),
        icharRngUpper(cp('9')),
        iref(1),
        ialt(),
        iend(),
      ],
      [
        [
          new RuleChar([makeRange('a', 'z'), makeRange('A', 'Z'), makeRange('0', '9')]),
          new RuleRef(1),
          new RuleEnd(),
        ],
        [new RuleEnd()],
      ],
    ],
  ] as [string, InternalRuleDef[], UnresolvedRule[][]][])(
    'it builds rule stack for a char with asterisk modifier: %s',
    (_grammar, input, expected) => {
      expect(buildRuleStack(input)).toStrictEqual(expected);
    },
  );

  test('char with range', () => {
    const input = [
      ichar([cp('a')]),
      icharRngUpper(cp('z')),
      icharAlt(cp('A')),
      icharRngUpper(cp('Z')),
      icharAlt(cp('_')),
      iend(),
    ];

    expect(buildRuleStack(input)).toStrictEqual([
      [
        new RuleChar([makeRange('a', 'z'), makeRange('A', 'Z'), cp('_')]),
        new RuleEnd(),
      ],
    ]);
  });

  test('it builds rule stack for situation root ws plus newline ws star', () => {
    const input = [
      ichar([32]),
      icharAlt(92),
      icharAlt(110),
      iref(4),
      ialt(),
      iend(),
    ];

    expect(buildRuleStack(input)).toStrictEqual([
      [new RuleChar([32, 92, 110]), new RuleRef(4), new RuleEnd()],
      [new RuleEnd()],
    ]);
  });

  test('it builds rule stack for situation root char plus char range', () => {
    const input = [
      ichar([cp('a')]),
      icharRngUpper(cp('z')),
      icharAlt(cp('A')),
      icharRngUpper(cp('Z')),
      iref(1),
      ialt(),
      ichar([cp('a')]),
      icharRngUpper(cp('z')),
      icharAlt(cp('A')),
      icharRngUpper(cp('Z')),
      iend(),
    ];

    expect(buildRuleStack(input)).toStrictEqual([
      [
        new RuleChar([makeRange('a', 'z'), makeRange('A', 'Z')]),
        new RuleRef(1),
        new RuleEnd(),
      ],
      [
        new RuleChar([makeRange('a', 'z'), makeRange('A', 'Z')]),
        new RuleEnd(),
      ],
    ]);
  });
});
