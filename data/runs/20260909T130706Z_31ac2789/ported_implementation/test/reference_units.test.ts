import { describe, expect, test } from 'vitest';

import fixtures from './fixtures/unit_fixtures.json' with { type: 'json' };

import {
  buildErrorPosition,
  Color,
  colorize,
  getInputAsCodePoints,
  getInputAsString,
  getParentStackId,
  getSerializedRuleKey,
  GraphNode,
  GraphPointer,
  GrammarParseError,
  isPointInRange,
  isWordChar,
  parseChar,
  parseName,
  parseSpace,
  printGraphNode,
  printGraphPointer,
  RuleChar,
  RuleCharExclude,
  RuleEnd,
  RuleRef,
  type Colorize,
  type Range,
  type UnresolvedRule,
} from '../index.ts';

interface Case {
  args: unknown[];
  result?: unknown;
  error?: string;
  message?: string;
}

const identityColorize: Colorize = (text) => `${text}`;

/**
 * Assert that a call either returns what the reference returned, or throws the
 * same error the reference threw.
 */
const expectCase = (fixture: Case, fn: (...args: never[]) => unknown): void => {
  const label = JSON.stringify(fixture.args);
  if (fixture.error === undefined) {
    expect(fn(...(fixture.args as never[])), label).toEqual(fixture.result);
    return;
  }
  if (fixture.error === 'GrammarParseError') {
    let thrown: unknown;
    try {
      fn(...(fixture.args as never[]));
    } catch (err) {
      thrown = err;
    }
    expect(thrown, label).toBeInstanceOf(GrammarParseError);
    expect((thrown as Error).message, label).toBe(fixture.message);
    return;
  }
  // The reference raises a bare Python error (an IndexError from indexing past
  // the end of a list, say); the port handles these cases without throwing.
  expect(() => fn(...(fixture.args as never[])), label).not.toThrow();
};

const makeRule = (spec: { type: string; value?: unknown }): UnresolvedRule => {
  switch (spec.type) {
    case 'char':
      return new RuleChar(spec.value as (number | Range)[]);
    case 'char_exclude':
      return new RuleCharExclude(spec.value as (number | Range)[]);
    case 'ref':
      return new RuleRef(spec.value as number);
    case 'end':
      return new RuleEnd();
    default:
      throw new Error(`Unknown rule type: ${spec.type}`);
  }
};

const mockPointer = (ids: number[][]): GraphPointer => {
  let pointer: GraphPointer | undefined;
  for (const [stackId, pathId, stepId] of ids) {
    const node = new GraphNode(new RuleEnd(), { stackId, pathId, stepId });
    pointer = new GraphPointer(node, pointer);
  }
  return pointer as GraphPointer;
};

const units = fixtures as unknown as Record<string, never>;
const casesFor = (key: string): Case[] => units[key] as unknown as Case[];

describe('colorize', () => {
  test('exposes the same colors', () => {
    expect(Color).toEqual(units.colors);
  });

  test('prefixes text with the color', () => {
    for (const fixture of casesFor('colorize')) {
      expect(colorize(fixture.args[0] as string, fixture.args[1] as string)).toBe(fixture.result);
    }
  });
});

describe('rules builder helpers', () => {
  test('isWordChar', () => {
    for (const fixture of casesFor('isWordChar')) {
      expectCase(fixture, isWordChar as (...args: never[]) => unknown);
    }
  });

  test('parseSpace', () => {
    for (const fixture of casesFor('parseSpace')) {
      expectCase(fixture, parseSpace as (...args: never[]) => unknown);
    }
  });

  test('parseName', () => {
    for (const fixture of casesFor('parseName')) {
      expectCase(fixture, parseName as (...args: never[]) => unknown);
    }
  });

  test('parseChar', () => {
    for (const fixture of casesFor('parseChar')) {
      expectCase(fixture, parseChar as (...args: never[]) => unknown);
    }
  });
});

describe('errors', () => {
  test('buildErrorPosition', () => {
    for (const fixture of casesFor('buildErrorPosition')) {
      expectCase(fixture, buildErrorPosition as (...args: never[]) => unknown);
    }
  });

  test('getInputAsString', () => {
    for (const fixture of casesFor('getInputAsString')) {
      expectCase(fixture, getInputAsString as (...args: never[]) => unknown);
    }
  });
});

describe('utils', () => {
  test('isPointInRange', () => {
    for (const fixture of casesFor('isPointInRange')) {
      expectCase(fixture, ((point: number, range: Range) =>
        isPointInRange(point, range)) as (...args: never[]) => unknown);
    }
  });

  test('getInputAsCodePoints', () => {
    for (const fixture of casesFor('getInputAsCodePoints')) {
      expectCase(fixture, getInputAsCodePoints as (...args: never[]) => unknown);
    }
  });
});

describe('getSerializedRuleKey', () => {
  test('serializes each rule type', () => {
    for (const fixture of units.getSerializedRuleKey as unknown as {
      rule: { type: string; value?: unknown };
      result: string;
    }[]) {
      // Python's `json.dumps` puts a space after each comma; `JSON.stringify`
      // does not. The key is only ever used to compare rules internally.
      const expected = fixture.result.replace(/, /g, ',');
      expect(getSerializedRuleKey(makeRule(fixture.rule))).toBe(expected);
    }
  });
});

describe('printing', () => {
  test('getParentStackId', () => {
    for (const fixture of units.getParentStackId as unknown as {
      ids: number[][];
      plain: string;
      colorized: string;
    }[]) {
      const pointer = mockPointer(fixture.ids);
      expect(getParentStackId(pointer, identityColorize)).toBe(fixture.plain);
      expect(getParentStackId(pointer, colorize)).toBe(fixture.colorized);
    }
  });

  test('printGraphPointer', () => {
    for (const fixture of units.printGraphPointer as unknown as {
      ids: number[][];
      plain: string;
      colorized: string;
    }[]) {
      const pointer = mockPointer(fixture.ids);
      expect(printGraphPointer(pointer)({ colorize: identityColorize })).toBe(fixture.plain);
      expect(printGraphPointer(pointer)({ colorize })).toBe(fixture.colorized);
    }
  });

  test('printGraphNode', () => {
    const meta = { stackId: 0, pathId: 1, stepId: 2 };
    const nodes: Record<string, GraphNode> = {
      char: new GraphNode(new RuleChar([65]), meta),
      'char-with-position': new GraphNode(new RuleChar([65]), meta),
      'char-range': new GraphNode(new RuleChar([[97, 122]]), meta),
      'char-newline': new GraphNode(new RuleChar([10]), meta),
      'char-mixed': new GraphNode(new RuleChar([[97, 99], 122, 10]), meta),
      ref: new GraphNode(new RuleRef(200), meta),
      chained: new GraphNode(new RuleChar([65]), meta, new GraphNode(new RuleChar([66]), meta)),
    };

    for (const fixture of units.printGraphNode as unknown as {
      name: string;
      showPosition: boolean;
      plain: string;
      colorized: string;
    }[]) {
      const node = nodes[fixture.name];
      expect(
        printGraphNode(node)({ colorize: identityColorize, show_position: fixture.showPosition }),
        fixture.name,
      ).toBe(fixture.plain);
      expect(
        printGraphNode(node)({ colorize, show_position: fixture.showPosition }),
        fixture.name,
      ).toBe(fixture.colorized);
    }
  });
});
