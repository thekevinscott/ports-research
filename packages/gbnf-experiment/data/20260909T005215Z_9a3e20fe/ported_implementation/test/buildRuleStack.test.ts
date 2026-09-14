import assert from 'node:assert/strict';
import { describe, it } from 'node:test';

import {
  RuleChar,
  RuleCharExclude,
  RuleEnd,
} from '../src/grammarGraph/grammarGraphTypes.ts';
import type { Range, UnresolvedRule } from '../src/grammarGraph/grammarGraphTypes.ts';
import { RuleRef } from '../src/grammarGraph/ruleRef.ts';
import { buildRuleStack } from '../src/grammarParser/buildRuleStack.ts';
import {
  InternalRuleDefAlt,
  InternalRuleDefChar,
  InternalRuleDefCharAlt,
  InternalRuleDefCharNot,
  InternalRuleDefCharRngUpper,
  InternalRuleDefEnd,
  InternalRuleDefReference,
} from '../src/rulesBuilder/rulesBuilderTypes.ts';
import type { InternalRuleDef } from '../src/rulesBuilder/rulesBuilderTypes.ts';

const ichar = (value: number[]): InternalRuleDef => new InternalRuleDefChar(value);
const icharNot = (value: number[]): InternalRuleDef => new InternalRuleDefCharNot(value);
const icharAlt = (value: number): InternalRuleDef => new InternalRuleDefCharAlt(value);
const icharRngUpper = (value: number): InternalRuleDef => new InternalRuleDefCharRngUpper(value);
const iref = (value: number): InternalRuleDef => new InternalRuleDefReference(value);
const ialt = (): InternalRuleDef => new InternalRuleDefAlt();
const iend = (): InternalRuleDef => new InternalRuleDefEnd();

const char = (value: (number | Range)[]): UnresolvedRule => new RuleChar(value);
const charExclude = (value: (number | Range)[]): UnresolvedRule => new RuleCharExclude(value);
const ref = (value: number): UnresolvedRule => new RuleRef(value);
const end = (): UnresolvedRule => new RuleEnd();

interface Case {
  name: string;
  input: InternalRuleDef[];
  expected: UnresolvedRule[][];
}

const CASES: Case[] = [
  {
    name: "test_it_builds_rule_stack_for_a_single_path",
    input: [ichar([120])],
    expected: [[char([120]), end()]],
  },
  {
    name: "test_it_builds_rule_stack_for_two_alternate_paths",
    input: [ichar([120]), ialt(), ichar([121])],
    expected: [[char([120]), end()], [char([121]), end()]],
  },
  {
    name: "test_it_builds_rule_stack_for_three_alternate_paths",
    input: [ichar([120]), ialt(), ichar([121]), ialt(), ichar([122])],
    expected: [[char([120]), end()], [char([121]), end()], [char([122]), end()]],
  },
  {
    name: "test_it_builds_rule_stack_for_char_not",
    input: [icharNot([120]), ialt(), icharNot([121]), ialt(), icharNot([122])],
    expected: [[charExclude([120]), end()], [charExclude([121]), end()], [charExclude([122]), end()]],
  },
  {
    name: "test_it_builds_rule_stack_for_mixed_char_and_char_not",
    input: [icharNot([120]), ialt(), ichar([121]), ialt(), icharNot([122])],
    expected: [[charExclude([120]), end()], [char([121]), end()], [charExclude([122]), end()]],
  },
  {
    name: "test_it_builds_rule_stack_for_char_not_with_two_characters_and_a_range",
    input: [icharNot([120]), icharAlt(121), icharAlt(122), icharRngUpper(130)],
    expected: [[charExclude([120, 121, [122, 130]]), end()]],
  },
  {
    name: "test_it_builds_rule_stack_for_a_char_with_no_modifiers",
    input: [ichar([97]), icharRngUpper(122), iend()],
    expected: [[char([[97, 122]]), end()]],
  },
  {
    name: "test_it_builds_rule_stack_for_a_char_with_no_modifiers",
    input: [ichar([97]), icharRngUpper(122), icharAlt(65), icharRngUpper(90), iend()],
    expected: [[char([[97, 122], [65, 90]]), end()]],
  },
  {
    name: "test_it_builds_rule_stack_for_a_char_with_no_modifiers",
    input: [ichar([97]), icharRngUpper(122), icharAlt(65), icharRngUpper(90), icharAlt(48), icharRngUpper(57), iend()],
    expected: [[char([[97, 122], [65, 90], [48, 57]]), end()]],
  },
  {
    name: "test_it_builds_rule_stack_for_a_char_with_question_mark_modifier",
    input: [ichar([97]), icharRngUpper(122), ialt(), iend()],
    expected: [[char([[97, 122]]), end()], [end()]],
  },
  {
    name: "test_it_builds_rule_stack_for_a_char_with_question_mark_modifier",
    input: [ichar([97]), icharRngUpper(122), icharAlt(65), icharRngUpper(90), ialt(), iend()],
    expected: [[char([[97, 122], [65, 90]]), end()], [end()]],
  },
  {
    name: "test_it_builds_rule_stack_for_a_char_with_question_mark_modifier",
    input: [ichar([97]), icharRngUpper(122), icharAlt(65), icharRngUpper(90), icharAlt(48), icharRngUpper(57), ialt(), iend()],
    expected: [[char([[97, 122], [65, 90], [48, 57]]), end()], [end()]],
  },
  {
    name: "test_it_builds_rule_stack_for_a_char_with_plus_modifier",
    input: [ichar([97]), icharRngUpper(122), iref(1), ialt(), ichar([97]), icharRngUpper(122), iend()],
    expected: [[char([[97, 122]]), ref(1), end()], [char([[97, 122]]), end()]],
  },
  {
    name: "test_it_builds_rule_stack_for_a_char_with_plus_modifier",
    input: [ichar([97]), icharRngUpper(122), icharAlt(65), icharRngUpper(90), iref(1), ialt(), ichar([97]), icharRngUpper(122), icharAlt(65), icharRngUpper(90), iend()],
    expected: [[char([[97, 122], [65, 90]]), ref(1), end()], [char([[97, 122], [65, 90]]), end()]],
  },
  {
    name: "test_it_builds_rule_stack_for_a_char_with_plus_modifier",
    input: [ichar([97]), icharRngUpper(122), icharAlt(65), icharRngUpper(90), icharAlt(48), icharRngUpper(57), iref(1), ialt(), ichar([97]), icharRngUpper(122), icharAlt(65), icharRngUpper(90), icharAlt(48), icharRngUpper(57), iend()],
    expected: [[char([[97, 122], [65, 90], [48, 57]]), ref(1), end()], [char([[97, 122], [65, 90], [48, 57]]), end()]],
  },
  {
    name: "test_it_builds_rule_stack_for_a_char_with_asterisk_modifier",
    input: [ichar([97]), icharRngUpper(122), iref(1), ialt(), iend()],
    expected: [[char([[97, 122]]), ref(1), end()], [end()]],
  },
  {
    name: "test_it_builds_rule_stack_for_a_char_with_asterisk_modifier",
    input: [ichar([97]), icharRngUpper(122), icharAlt(65), icharRngUpper(90), iref(1), ialt(), iend()],
    expected: [[char([[97, 122], [65, 90]]), ref(1), end()], [end()]],
  },
  {
    name: "test_it_builds_rule_stack_for_a_char_with_asterisk_modifier",
    input: [ichar([97]), icharRngUpper(122), icharAlt(65), icharRngUpper(90), icharAlt(48), icharRngUpper(57), iref(1), ialt(), iend()],
    expected: [[char([[97, 122], [65, 90], [48, 57]]), ref(1), end()], [end()]],
  },
  {
    name: "test_char_with_range",
    input: [ichar([97]), icharRngUpper(122), icharAlt(65), icharRngUpper(90), icharAlt(95), iend()],
    expected: [[char([[97, 122], [65, 90], 95]), end()]],
  },
  {
    name: "test_it_builds_rule_stack_for_situation_root_ws_plus_newline_ws_star",
    input: [ichar([32]), icharAlt(92), icharAlt(110), iref(4), ialt(), iend()],
    expected: [[char([32, 92, 110]), ref(4), end()], [end()]],
  },
  {
    name: "test_it_builds_rule_stack_for_situation_root_char_plus_char_range",
    input: [ichar([97]), icharRngUpper(122), icharAlt(65), icharRngUpper(90), iref(1), ialt(), ichar([97]), icharRngUpper(122), icharAlt(65), icharRngUpper(90), iend()],
    expected: [[char([[97, 122], [65, 90]]), ref(1), end()], [char([[97, 122], [65, 90]]), end()]],
  },
];

describe('buildRuleStack', () => {
  const seen = new Map<string, number>();
  for (const { name, input, expected } of CASES) {
    const n = (seen.get(name) ?? 0) + 1;
    seen.set(name, n);
    const title = name.replace(/^test_/u, '').replace(/_/gu, ' ');
    it(`${title} (case ${n})`, () => {
      assert.deepStrictEqual(buildRuleStack(input), expected);
    });
  }

  it('throws when an alt appears before anything else', () => {
    assert.throws(() => buildRuleStack([ialt()]), /Encountered alt without anything before it/u);
  });

  it('throws when a char alt is not preceded by a char', () => {
    assert.throws(
      () => buildRuleStack([icharAlt(97)]),
      /Encountered char alt, should be handled by above block/u,
    );
  });

  it('throws on an unsupported rule type', () => {
    assert.throws(
      () => buildRuleStack([{ type: 'UNKNOWN' } as unknown as InternalRuleDef]),
      /Unsupported rule type/u,
    );
  });
});
