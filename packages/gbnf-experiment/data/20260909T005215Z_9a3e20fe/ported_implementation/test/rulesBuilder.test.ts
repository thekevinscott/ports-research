import assert from 'node:assert/strict';
import { describe, it } from 'node:test';

import { RulesBuilder } from '../src/rulesBuilder/rulesBuilder.ts';
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

interface Case {
  key: string;
  grammar: string;
  symbolIds: [string, number][];
  rules: InternalRuleDef[][];
}

const CASES: Case[] = [
  {
    key: "single-string",
    grammar: "root ::= \"foo\"",
    symbolIds: [["root", 0]],
    rules: [
      [ichar([102]), ichar([111]), ichar([111]), iend()],
    ],
  },
  {
    key: "quote character",
    grammar: "root ::= \"\\\"\"",
    symbolIds: [["root", 0]],
    rules: [
      [ichar([34]), iend()],
    ],
  },
  {
    key: "two-lines-referencing-expression",
    grammar: "root ::= foo\n            foo ::= \"bar\"",
    symbolIds: [["root", 0], ["foo", 1]],
    rules: [
      [iref(1), iend()],
      [ichar([98]), ichar([97]), ichar([114]), iend()],
    ],
  },
  {
    key: "expression with dash",
    grammar: "root ::= foo-bar\n            foo-bar ::= \"bar\"",
    symbolIds: [["root", 0], ["foo-bar", 1]],
    rules: [
      [iref(1), iend()],
      [ichar([98]), ichar([97]), ichar([114]), iend()],
    ],
  },
  {
    key: "simple-grammar",
    grammar: "\n            root  ::= (expr \"=\" term \"\n\")+\n            expr  ::= term ([-+*/] term)*\n            term  ::= [0-9]+\n            ",
    symbolIds: [["root", 0], ["root_1", 1], ["expr", 2], ["term", 3], ["root_4", 4], ["expr_5", 5], ["expr_6", 6], ["term_7", 7]],
    rules: [
      [iref(4), iend()],
      [iref(2), ichar([61]), iref(3), ichar([10]), iend()],
      [iref(3), iref(6), iend()],
      [iref(7), iend()],
      [iref(1), iref(4), ialt(), iref(1), iend()],
      [ichar([45]), icharAlt(43), icharAlt(42), icharAlt(47), iref(3), iend()],
      [iref(5), iref(6), ialt(), iend()],
      [ichar([48]), icharRngUpper(57), iref(7), ialt(), ichar([48]), icharRngUpper(57), iend()],
    ],
  },
  {
    key: "longer-grammar",
    grammar: "\n            root  ::= (expr \"=\" ws term \"\n\")+\n            expr  ::= term ([-+*/] term)*\n            term  ::= ident | num | \"(\" ws expr \")\" ws\n            ident ::= [a-z] [a-z0-9_]* ws\n            num   ::= [0-9]+ ws\n            ws    ::= [ \t\n]*\n            ",
    symbolIds: [["root", 0], ["root_1", 1], ["expr", 2], ["ws", 3], ["term", 4], ["root_5", 5], ["expr_6", 6], ["expr_7", 7], ["ident", 8], ["num", 9], ["ident_10", 10], ["num_11", 11], ["ws_12", 12]],
    rules: [
      [iref(5), iend()],
      [iref(2), ichar([61]), iref(3), iref(4), ichar([10]), iend()],
      [iref(4), iref(7), iend()],
      [iref(12), iend()],
      [iref(8), ialt(), iref(9), ialt(), ichar([40]), iref(3), iref(2), ichar([41]), iref(3), iend()],
      [iref(1), iref(5), ialt(), iref(1), iend()],
      [ichar([45]), icharAlt(43), icharAlt(42), icharAlt(47), iref(4), iend()],
      [iref(6), iref(7), ialt(), iend()],
      [ichar([97]), icharRngUpper(122), iref(10), iref(3), iend()],
      [iref(11), iref(3), iend()],
      [ichar([97]), icharRngUpper(122), icharAlt(48), icharRngUpper(57), icharAlt(95), iref(10), ialt(), iend()],
      [ichar([48]), icharRngUpper(57), iref(11), ialt(), ichar([48]), icharRngUpper(57), iend()],
      [ichar([32]), icharAlt(9), icharAlt(10), iref(12), ialt(), iend()],
    ],
  },
  {
    key: "character unicode grammar",
    grammar: "root  ::= [\u3041-\u309f]",
    symbolIds: [["root", 0]],
    rules: [
      [ichar([12353]), icharRngUpper(12447), iend()],
    ],
  },
  {
    key: "character alts grammar",
    grammar: "root  ::= [az]",
    symbolIds: [["root", 0]],
    rules: [
      [ichar([97]), icharAlt(122), iend()],
    ],
  },
  {
    key: "character range grammar",
    grammar: "root  ::= [a-zA-Z0-9]",
    symbolIds: [["root", 0]],
    rules: [
      [ichar([97]), icharRngUpper(122), icharAlt(65), icharRngUpper(90), icharAlt(48), icharRngUpper(57), iend()],
    ],
  },
  {
    key: "character range grammar with dash at end",
    grammar: "root  ::= [a-z-]",
    symbolIds: [["root", 0]],
    rules: [
      [ichar([97]), icharRngUpper(122), icharAlt(45), iend()],
    ],
  },
  {
    key: "grouping",
    grammar: "root  ::= \"f\" (\"b\" | \"a\")",
    symbolIds: [["root", 0], ["root_1", 1]],
    rules: [
      [ichar([102]), iref(1), iend()],
      [ichar([98]), ialt(), ichar([97]), iend()],
    ],
  },
  {
    key: "optional",
    grammar: "root  ::= \"f\"?",
    symbolIds: [["root", 0], ["root_1", 1]],
    rules: [
      [iref(1), iend()],
      [ichar([102]), ialt(), iend()],
    ],
  },
  {
    key: "repeating",
    grammar: "root  ::= \"f\"*",
    symbolIds: [["root", 0], ["root_1", 1]],
    rules: [
      [iref(1), iend()],
      [ichar([102]), iref(1), ialt(), iend()],
    ],
  },
  {
    key: "repeating-at-least-once",
    grammar: "root  ::= \"f\"+",
    symbolIds: [["root", 0], ["root_1", 1]],
    rules: [
      [iref(1), iend()],
      [ichar([102]), iref(1), ialt(), ichar([102]), iend()],
    ],
  },
  {
    key: "character range with optional repeating",
    grammar: "root  ::= [a-zA-Z0-9]*",
    symbolIds: [["root", 0], ["root_1", 1]],
    rules: [
      [iref(1), iend()],
      [ichar([97]), icharRngUpper(122), icharAlt(65), icharRngUpper(90), icharAlt(48), icharRngUpper(57), iref(1), ialt(), iend()],
    ],
  },
  {
    key: "grouping-repeating",
    grammar: "root  ::= \"f\" (\"b\" | \"a\")*",
    symbolIds: [["root", 0], ["root_1", 1], ["root_2", 2]],
    rules: [
      [ichar([102]), iref(2), iend()],
      [ichar([98]), ialt(), ichar([97]), iend()],
      [iref(1), iref(2), ialt(), iend()],
    ],
  },
  {
    key: "negation",
    grammar: "root ::= [^\n]",
    symbolIds: [["root", 0]],
    rules: [
      [icharNot([10]), iend()],
    ],
  },
  {
    key: "negation of range",
    grammar: "root ::= [^0-9]",
    symbolIds: [["root", 0]],
    rules: [
      [icharNot([48]), icharRngUpper(57), iend()],
    ],
  },
  {
    key: "negation with after",
    grammar: "root ::= [^\n]+ \"\n\"",
    symbolIds: [["root", 0], ["root_1", 1]],
    rules: [
      [iref(1), ichar([10]), iend()],
      [icharNot([10]), iref(1), ialt(), icharNot([10]), iend()],
    ],
  },
  {
    key: "longer negation",
    grammar: "root ::= \"\\\"\" ( [^\"abcdefgh])* ",
    symbolIds: [["root", 0], ["root_1", 1], ["root_2", 2]],
    rules: [
      [ichar([34]), iref(2), iend()],
      [icharNot([34]), icharAlt(97), icharAlt(98), icharAlt(99), icharAlt(100), icharAlt(101), icharAlt(102), icharAlt(103), icharAlt(104), iend()],
      [iref(1), iref(2), ialt(), iend()],
    ],
  },
  {
    key: "longer negation with a range",
    grammar: "root ::= \"\\\"\" ( [^\"abcdefghA-Z])* ",
    symbolIds: [["root", 0], ["root_1", 1], ["root_2", 2]],
    rules: [
      [ichar([34]), iref(2), iend()],
      [icharNot([34]), icharAlt(97), icharAlt(98), icharAlt(99), icharAlt(100), icharAlt(101), icharAlt(102), icharAlt(103), icharAlt(104), icharAlt(65), icharRngUpper(90), iend()],
      [iref(1), iref(2), ialt(), iend()],
    ],
  },
  {
    key: "escaped 8-bit unicode char",
    grammar: "root ::= \"\\x2A\"",
    symbolIds: [["root", 0]],
    rules: [
      [ichar([42]), iend()],
    ],
  },
  {
    key: "escaped 16-bit unicode char",
    grammar: "root ::= \"\\u006F\"",
    symbolIds: [["root", 0]],
    rules: [
      [ichar([111]), iend()],
    ],
  },
  {
    key: "escaped 32-bit unicode char",
    grammar: "root ::= \"\\U0001F4A9\"",
    symbolIds: [["root", 0]],
    rules: [
      [ichar([128169]), iend()],
    ],
  },
  {
    key: "escaped tab char",
    grammar: "root ::= \"\\t\"",
    symbolIds: [["root", 0]],
    rules: [
      [ichar([9]), iend()],
    ],
  },
  {
    key: "escaped new line char",
    grammar: "root ::= \"\n\"",
    symbolIds: [["root", 0]],
    rules: [
      [ichar([10]), iend()],
    ],
  },
  {
    key: "escaped \r char",
    grammar: "root ::= \"\\r\"",
    symbolIds: [["root", 0]],
    rules: [
      [ichar([13]), iend()],
    ],
  },
  {
    key: "escaped quote char",
    grammar: "root ::= \"\\\"\"",
    symbolIds: [["root", 0]],
    rules: [
      [ichar([34]), iend()],
    ],
  },
  {
    key: "escaped [ char",
    grammar: "root ::= \"\\[\"",
    symbolIds: [["root", 0]],
    rules: [
      [ichar([91]), iend()],
    ],
  },
  {
    key: "escaped ] char",
    grammar: "root ::= \"\\]\"",
    symbolIds: [["root", 0]],
    rules: [
      [ichar([93]), iend()],
    ],
  },
  {
    key: "escaped \\ char",
    grammar: "root ::= \"\\\\\"",
    symbolIds: [["root", 0]],
    rules: [
      [ichar([92]), iend()],
    ],
  },
  {
    key: "simple arithmetic",
    grammar: "\n            root ::= (expr \"=\" term \"\n\")+\n            expr ::= term ([-+*/] term)*\n            term ::= [0-9]+\n            ",
    symbolIds: [["root", 0], ["root_1", 1], ["expr", 2], ["term", 3], ["root_4", 4], ["expr_5", 5], ["expr_6", 6], ["term_7", 7]],
    rules: [
      [iref(4), iend()],
      [iref(2), ichar([61]), iref(3), ichar([10]), iend()],
      [iref(3), iref(6), iend()],
      [iref(7), iend()],
      [iref(1), iref(4), ialt(), iref(1), iend()],
      [ichar([45]), icharAlt(43), icharAlt(42), icharAlt(47), iref(3), iend()],
      [iref(5), iref(6), ialt(), iend()],
      [ichar([48]), icharRngUpper(57), iref(7), ialt(), ichar([48]), icharRngUpper(57), iend()],
    ],
  },
  {
    key: "ranges with chars",
    grammar: "\n            root ::= [a-z0-9_]*\n            ",
    symbolIds: [["root", 0], ["root_1", 1]],
    rules: [
      [iref(1), iend()],
      [ichar([97]), icharRngUpper(122), icharAlt(48), icharRngUpper(57), icharAlt(95), iref(1), ialt(), iend()],
    ],
  },
  {
    key: "nested ranges with chars",
    grammar: "\n            root ::= [a-z] [a-z0-9_]*\n            ",
    symbolIds: [["root", 0], ["root_1", 1]],
    rules: [
      [ichar([97]), icharRngUpper(122), iref(1), iend()],
      [ichar([97]), icharRngUpper(122), icharAlt(48), icharRngUpper(57), icharAlt(95), iref(1), ialt(), iend()],
    ],
  },
  {
    key: "expression with nested range with chars",
    grammar: "\n            root ::= ident\n            ident ::= [a-z] [a-z0-9_]* ws\n            ws ::= [ \\t\n]*\n            ",
    symbolIds: [["root", 0], ["ident", 1], ["ident_2", 2], ["ws", 3], ["ws_4", 4]],
    rules: [
      [iref(1), iend()],
      [ichar([97]), icharRngUpper(122), iref(2), iref(3), iend()],
      [ichar([97]), icharRngUpper(122), icharAlt(48), icharRngUpper(57), icharAlt(95), iref(2), ialt(), iend()],
      [iref(4), iend()],
      [ichar([32]), icharAlt(9), icharAlt(10), iref(4), ialt(), iend()],
    ],
  },
  {
    key: "lots of escapes",
    grammar: "root ::= \"\\x2A\" \"\\u006F\" \"\\U0001F4A9\" \"\\t\" \"\n\" \"\\r\" \"\\\"\" \"\\[\" \"\\]\" \"\\\\\"",
    symbolIds: [["root", 0]],
    rules: [
      [ichar([42]), ichar([111]), ichar([128169]), ichar([9]), ichar([10]), ichar([13]), ichar([34]), ichar([91]), ichar([93]), ichar([92]), iend()],
    ],
  },
  {
    key: "lots of escape and alternate escapes",
    grammar: "root ::= \"\\x2A\" \"\\u006F\" \"\\U0001F4A9\" \"\\t\" \"\n\" \"\\r\" \"\\\"\" \"\\[\" \"\\]\" \"\\\\\" (\n                \"\\x2A\" | \"\\u006F\" | \"\\U0001F4A9\" | \"\\t\" | \"\n\" | \"\\r\" | \"\\\"\" | \"\\[\" | \"\\]\"  | \"\\\\\" )",
    symbolIds: [["root", 0], ["root_1", 1]],
    rules: [
      [ichar([42]), ichar([111]), ichar([128169]), ichar([9]), ichar([10]), ichar([13]), ichar([34]), ichar([91]), ichar([93]), ichar([92]), iref(1), iend()],
      [ichar([42]), ialt(), ichar([111]), ialt(), ichar([128169]), ialt(), ichar([9]), ialt(), ichar([10]), ialt(), ichar([13]), ialt(), ichar([34]), ialt(), ichar([91]), ialt(), ichar([93]), ialt(), ichar([92]), iend()],
    ],
  },
  {
    key: "arithmetic",
    grammar: "\n            root  ::= (expr \"=\" ws term \"\n\")+\n            expr  ::= term ([-+*/] term)*\n            term  ::= ident | num | \"(\" ws expr \")\" ws\n            ident ::= [a-z] [a-z0-9_]* ws\n            num   ::= [0-9]+ ws\n            ws    ::= [ \\t\n]*\n            ",
    symbolIds: [["root", 0], ["root_1", 1], ["expr", 2], ["ws", 3], ["term", 4], ["root_5", 5], ["expr_6", 6], ["expr_7", 7], ["ident", 8], ["num", 9], ["ident_10", 10], ["num_11", 11], ["ws_12", 12]],
    rules: [
      [iref(5), iend()],
      [iref(2), ichar([61]), iref(3), iref(4), ichar([10]), iend()],
      [iref(4), iref(7), iend()],
      [iref(12), iend()],
      [iref(8), ialt(), iref(9), ialt(), ichar([40]), iref(3), iref(2), ichar([41]), iref(3), iend()],
      [iref(1), iref(5), ialt(), iref(1), iend()],
      [ichar([45]), icharAlt(43), icharAlt(42), icharAlt(47), iref(4), iend()],
      [iref(6), iref(7), ialt(), iend()],
      [ichar([97]), icharRngUpper(122), iref(10), iref(3), iend()],
      [iref(11), iref(3), iend()],
      [ichar([97]), icharRngUpper(122), icharAlt(48), icharRngUpper(57), icharAlt(95), iref(10), ialt(), iend()],
      [ichar([48]), icharRngUpper(57), iref(11), ialt(), ichar([48]), icharRngUpper(57), iend()],
      [ichar([32]), icharAlt(9), icharAlt(10), iref(12), ialt(), iend()],
    ],
  },
  {
    key: "json.gbnf (string)",
    grammar: "\n            root ::=\n            \"\\\"\" (\n                [^\"\\\\\\x7F\\x00-\\x1F] |\n                \"\\\\\" ([\"\\\\/bfnrt] | \"u\" [0-9a-fA-F] [0-9a-fA-F] [0-9a-fA-F] [0-9a-fA-F]) # escapes\n            )* \"\\\"\"\n            ",
    symbolIds: [["root", 0], ["root_1", 1], ["root_2", 2], ["root_3", 3]],
    rules: [
      [ichar([34]), iref(3), ichar([34]), iend()],
      [icharNot([34]), icharAlt(92), icharAlt(127), icharAlt(0), icharRngUpper(31), ialt(), ichar([92]), iref(2), iend()],
      [ichar([34]), icharAlt(92), icharAlt(47), icharAlt(98), icharAlt(102), icharAlt(110), icharAlt(114), icharAlt(116), ialt(), ichar([117]), ichar([48]), icharRngUpper(57), icharAlt(97), icharRngUpper(102), icharAlt(65), icharRngUpper(70), ichar([48]), icharRngUpper(57), icharAlt(97), icharRngUpper(102), icharAlt(65), icharRngUpper(70), ichar([48]), icharRngUpper(57), icharAlt(97), icharRngUpper(102), icharAlt(65), icharRngUpper(70), ichar([48]), icharRngUpper(57), icharAlt(97), icharRngUpper(102), icharAlt(65), icharRngUpper(70), iend()],
      [iref(1), iref(3), ialt(), iend()],
    ],
  },
  {
    key: "json.gbnf (full)",
    grammar: "\n            root   ::= object\n            value  ::= object | array | string | number | (\"true\" | \"false\" | \"null\") ws\n            object ::=\n              \"{\" ws (\n                        string \":\" ws value\n                (\",\" ws string \":\" ws value)*\n              )? \"}\" ws\n            array  ::=\n              \"[\" ws (\n                        value\n                (\",\" ws value)*\n              )? \"]\" ws\n                  string ::=\n              \"\\\"\" (\n                [^\"\\\\\\x7F\\x00-\\x1F] |\n                \"\\\\\" ([\"\\\\/bfnrt] | \"u\" [0-9a-fA-F] [0-9a-fA-F] [0-9a-fA-F] [0-9a-fA-F]) # escapes\n              )* \"\\\"\" ws\n            number ::= (\"-\"? ([0-9] | [1-9] [0-9]*)) (\".\" [0-9]+)? ([eE] [-+]? [0-9]+)? ws\n            # Optional space: by convention, applied in this grammar after literal chars when allowed\n            ws ::= ([ \\t\n] ws)?\n            ",
    symbolIds: [["root", 0], ["object", 1], ["value", 2], ["array", 3], ["string", 4], ["number", 5], ["value_6", 6], ["ws", 7], ["object_8", 8], ["object_9", 9], ["object_10", 10], ["object_11", 11], ["array_12", 12], ["array_13", 13], ["array_14", 14], ["array_15", 15], ["string_16", 16], ["string_17", 17], ["string_18", 18], ["number_19", 19], ["number_20", 20], ["number_21", 21], ["number_22", 22], ["number_23", 23], ["number_24", 24], ["number_25", 25], ["number_26", 26], ["number_27", 27], ["number_28", 28], ["number_29", 29], ["ws_30", 30], ["ws_31", 31]],
    rules: [
      [iref(1), iend()],
      [ichar([123]), iref(7), iref(11), ichar([125]), iref(7), iend()],
      [iref(1), ialt(), iref(3), ialt(), iref(4), ialt(), iref(5), ialt(), iref(6), iref(7), iend()],
      [ichar([91]), iref(7), iref(15), ichar([93]), iref(7), iend()],
      [ichar([34]), iref(18), ichar([34]), iref(7), iend()],
      [iref(19), iref(25), iref(29), iref(7), iend()],
      [ichar([116]), ichar([114]), ichar([117]), ichar([101]), ialt(), ichar([102]), ichar([97]), ichar([108]), ichar([115]), ichar([101]), ialt(), ichar([110]), ichar([117]), ichar([108]), ichar([108]), iend()],
      [iref(31), iend()],
      [iref(4), ichar([58]), iref(7), iref(2), iref(10), iend()],
      [ichar([44]), iref(7), iref(4), ichar([58]), iref(7), iref(2), iend()],
      [iref(9), iref(10), ialt(), iend()],
      [iref(8), ialt(), iend()],
      [iref(2), iref(14), iend()],
      [ichar([44]), iref(7), iref(2), iend()],
      [iref(13), iref(14), ialt(), iend()],
      [iref(12), ialt(), iend()],
      [icharNot([34]), icharAlt(92), icharAlt(127), icharAlt(0), icharRngUpper(31), ialt(), ichar([92]), iref(17), iend()],
      [ichar([34]), icharAlt(92), icharAlt(47), icharAlt(98), icharAlt(102), icharAlt(110), icharAlt(114), icharAlt(116), ialt(), ichar([117]), ichar([48]), icharRngUpper(57), icharAlt(97), icharRngUpper(102), icharAlt(65), icharRngUpper(70), ichar([48]), icharRngUpper(57), icharAlt(97), icharRngUpper(102), icharAlt(65), icharRngUpper(70), ichar([48]), icharRngUpper(57), icharAlt(97), icharRngUpper(102), icharAlt(65), icharRngUpper(70), ichar([48]), icharRngUpper(57), icharAlt(97), icharRngUpper(102), icharAlt(65), icharRngUpper(70), iend()],
      [iref(16), iref(18), ialt(), iend()],
      [iref(20), iref(21), iend()],
      [ichar([45]), ialt(), iend()],
      [ichar([48]), icharRngUpper(57), ialt(), ichar([49]), icharRngUpper(57), iref(22), iend()],
      [ichar([48]), icharRngUpper(57), iref(22), ialt(), iend()],
      [ichar([46]), iref(24), iend()],
      [ichar([48]), icharRngUpper(57), iref(24), ialt(), ichar([48]), icharRngUpper(57), iend()],
      [iref(23), ialt(), iend()],
      [ichar([101]), icharAlt(69), iref(27), iref(28), iend()],
      [ichar([45]), icharAlt(43), ialt(), iend()],
      [ichar([48]), icharRngUpper(57), iref(28), ialt(), ichar([48]), icharRngUpper(57), iend()],
      [iref(26), ialt(), iend()],
      [ichar([32]), icharAlt(9), icharAlt(10), iref(7), iend()],
      [iref(30), ialt(), iend()],
    ],
  },
  {
    key: "japanese",
    grammar: "\n            # A probably incorrect grammar for Japanese\n            root        ::= jp-char+ ([ \\t\n] jp-char+)*\n            jp-char     ::= hiragana | katakana | punctuation | cjk\n            hiragana    ::= [\u3041-\u309f]\n            katakana    ::= [\u30a1-\u30ff]\n            punctuation ::= [\u3001-\u303e]\n            cjk         ::= [\u4e00-\u9fff]\n            ",
    symbolIds: [["root", 0], ["jp-char", 1], ["root_2", 2], ["root_3", 3], ["root_4", 4], ["root_5", 5], ["hiragana", 6], ["katakana", 7], ["punctuation", 8], ["cjk", 9]],
    rules: [
      [iref(2), iref(5), iend()],
      [iref(6), ialt(), iref(7), ialt(), iref(8), ialt(), iref(9), iend()],
      [iref(1), iref(2), ialt(), iref(1), iend()],
      [ichar([32]), icharAlt(9), icharAlt(10), iref(4), iend()],
      [iref(1), iref(4), ialt(), iref(1), iend()],
      [iref(3), iref(5), ialt(), iend()],
      [ichar([12353]), icharRngUpper(12447), iend()],
      [ichar([12449]), icharRngUpper(12543), iend()],
      [ichar([12289]), icharRngUpper(12350), iend()],
      [ichar([19968]), icharRngUpper(40959), iend()],
    ],
  },
];

describe('RulesBuilder', () => {
  for (const { key, grammar, symbolIds, rules } of CASES) {
    it(`parses the grammar: ${key}`, () => {
      const parsedGrammar = new RulesBuilder(grammar);
      assert.deepStrictEqual(parsedGrammar.rules, rules);
      assert.deepStrictEqual([...parsedGrammar.symbolIds.entries()], symbolIds);
    });
  }
});
