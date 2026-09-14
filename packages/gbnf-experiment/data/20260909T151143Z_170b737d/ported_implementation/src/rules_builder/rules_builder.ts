import { GrammarParseError } from "../utils/errors/index.ts";
import { at } from "../utils/python_compat.ts";
import { is_word_char } from "./is_word_char.ts";
import { parse_char } from "./parse_char.ts";
import { parse_name } from "./parse_name.ts";
import { parse_space } from "./parse_space.ts";
import {
  InternalRuleDefAlt,
  InternalRuleDefChar,
  InternalRuleDefCharAlt,
  InternalRuleDefCharNot,
  InternalRuleDefCharRngUpper,
  InternalRuleDefEnd,
  InternalRuleDefReference,
  type InternalRuleDef,
} from "./rules_builder_types.ts";
import { SymbolIds } from "./symbol_ids.ts";

type InternalRuleDefConstructor =
  | typeof InternalRuleDefChar
  | typeof InternalRuleDefCharNot
  | typeof InternalRuleDefCharRngUpper
  | typeof InternalRuleDefAlt
  | typeof InternalRuleDefEnd
  | typeof InternalRuleDefCharAlt;

export const get_out_elements = (
  type_of_rule: InternalRuleDefConstructor,
  startchar_value: number,
): InternalRuleDef => {
  if (type_of_rule === InternalRuleDefChar) {
    return new InternalRuleDefChar([startchar_value]);
  }
  if (type_of_rule === InternalRuleDefCharNot) {
    return new InternalRuleDefCharNot([startchar_value]);
  }
  if (type_of_rule === InternalRuleDefCharRngUpper) {
    return new InternalRuleDefCharRngUpper(startchar_value);
  }
  if (type_of_rule === InternalRuleDefAlt) {
    return new InternalRuleDefAlt();
  }
  if (type_of_rule === InternalRuleDefEnd) {
    return new InternalRuleDefEnd();
  }
  if (type_of_rule === InternalRuleDefCharAlt) {
    return new InternalRuleDefCharAlt(startchar_value);
  }

  throw new Error(`Invalid type: ${type_of_rule}`);
};

const is_python_space = (char: string): boolean => /\s/.test(char);

export class RulesBuilder {
  pos: number;
  symbol_ids: SymbolIds;
  rules: InternalRuleDef[][];
  src: string;
  start: number;
  time_limit: number;

  constructor(src: string, limit: number = 1000) {
    this.pos = 0;
    this.symbol_ids = new SymbolIds();
    this.rules = [];
    this.src = src;
    this.start = performance.now() / 1000;
    this.time_limit = limit;
    this.parse(src);
  }

  parse(src: string): void {
    this.pos = parse_space(src, 0, true);
    while (this.pos < src.length) {
      this.parse_rule(src);
    }

    // Validate the state to ensure that all rules are defined
    for (const rule of this.rules) {
      for (const elem of rule) {
        if (elem instanceof InternalRuleDefReference) {
          const rule_exists =
            elem.value < this.rules.length && this.rules[elem.value].length > 0;
          if (!rule_exists) {
            const missing_rule_name = this.symbol_ids.reverse_get(elem.value);
            let missing_rule_pos = this.symbol_ids.get_pos(missing_rule_name);

            // Skip over the ::= and any whitespace
            while (
              missing_rule_pos < src.length &&
              (src[missing_rule_pos] === ":" ||
                src[missing_rule_pos] === "=" ||
                is_python_space(src[missing_rule_pos]))
            ) {
              missing_rule_pos += 1;
            }

            throw new GrammarParseError(
              src,
              missing_rule_pos,
              `Undefined rule identifier "${missing_rule_name}"`,
            );
          }
        }
      }
    }
  }

  parse_rule(src: string): void {
    const name = parse_name(src, this.pos);
    this.pos = parse_space(src, this.pos + name.length, false);
    const rule_id = this.get_symbol_id(name, name.length);

    this.pos = parse_space(src, this.pos, true);
    if (
      !(
        this.pos + 2 < src.length && // Ensure the position + 2 is within bounds
        src[this.pos] === ":" &&
        src[this.pos + 1] === ":" &&
        src[this.pos + 2] === "="
      )
    ) {
      throw new GrammarParseError(src, this.pos, `Expecting ::= at ${this.pos}`);
    }
    this.pos += 3;
    this.pos = parse_space(src, this.pos, true);

    this.parse_alternates(name, rule_id);

    // Check if this.pos is within the bounds of src before checking for a carriage return
    if (this.pos < src.length && src[this.pos] === "\r") {
      this.pos += at(src, this.pos + 1) === "\n" ? 2 : 1;
    } else if (this.pos < src.length && src[this.pos] === "\n") {
      this.pos += 1;
    } else if (this.pos < src.length && src[this.pos]) {
      throw new GrammarParseError(src, this.pos, `Expecting newline or end at ${this.pos}`);
    }
    this.pos = parse_space(src, this.pos, true);
  }

  get_symbol_id(src: string, length: number): number {
    const next_id = this.symbol_ids.length;
    const key = src.slice(0, length);
    if (!this.symbol_ids.has(key)) {
      this.symbol_ids.set(key, next_id, this.pos);
    }
    return this.symbol_ids.getItem(key);
  }

  generate_symbol_id(base_name: string): number {
    const next_id = this.symbol_ids.length;
    this.symbol_ids.set(`${base_name}_${next_id}`, next_id, this.pos);
    return next_id;
  }

  add_rule(rule_id: number, rule: InternalRuleDef[]): void {
    while (this.rules.length <= rule_id) {
      this.rules.push([]);
    }
    this.rules[rule_id] = rule;
  }

  check_duration(): void {
    if (performance.now() / 1000 - this.start > this.time_limit) {
      throw new GrammarParseError(this.src, this.pos, `Duration of ${this.time_limit} exceeded`);
    }
  }

  parse_sequence(rule_name: string, out_elements: InternalRuleDef[], depth: number = 0): void {
    const is_nested = depth !== 0;
    const src = this.src;
    let last_sym_start = out_elements.length;

    while (this.pos < src.length) {
      if (src[this.pos] === '"') {
        this.pos += 1;
        last_sym_start = out_elements.length;
        while (at(src, this.pos) !== '"') {
          this.check_duration();
          const [value, inc_pos] = parse_char(src, this.pos);
          out_elements.push(new InternalRuleDefChar([value]));
          this.pos += inc_pos;
        }
        this.pos = parse_space(src, this.pos + 1, is_nested);
      } else if (src[this.pos] === "[") {
        this.pos += 1;
        let start_type: InternalRuleDefConstructor = InternalRuleDefChar;
        if (at(src, this.pos) === "^") {
          this.pos += 1;
          start_type = InternalRuleDefCharNot;
        }
        last_sym_start = out_elements.length;
        while (at(src, this.pos) !== "]") {
          this.check_duration();
          const type_: InternalRuleDefConstructor =
            last_sym_start < out_elements.length ? InternalRuleDefCharAlt : start_type;
          const [startchar_value, inc_pos] = parse_char(src, this.pos);
          this.pos += inc_pos;
          out_elements.push(get_out_elements(type_, startchar_value));

          if (at(src, this.pos) === "-" && at(src, this.pos + 1) !== "]") {
            this.pos += 1;
            const [endchar_value, end_inc_pos] = parse_char(src, this.pos);
            out_elements.push(new InternalRuleDefCharRngUpper(endchar_value));
            this.pos += end_inc_pos;
          }
        }
        this.pos = parse_space(src, this.pos + 1, is_nested);
      } else if (is_word_char(src[this.pos])) {
        const name = parse_name(src, this.pos);
        const ref_rule_id = this.get_symbol_id(name, name.length);
        this.pos += name.length;
        this.pos = parse_space(src, this.pos, is_nested);

        last_sym_start = out_elements.length;
        out_elements.push(new InternalRuleDefReference(ref_rule_id));
      } else if (src[this.pos] === "(") {
        this.pos = parse_space(src, this.pos + 1, true);
        const sub_rule_id = this.generate_symbol_id(rule_name);
        this.parse_alternates(rule_name, sub_rule_id, depth + 1);
        last_sym_start = out_elements.length;
        out_elements.push(new InternalRuleDefReference(sub_rule_id));
        if (at(src, this.pos) !== ")") {
          throw new GrammarParseError(src, this.pos, `Expecting ')' at ${this.pos}`);
        }
        this.pos = parse_space(src, this.pos + 1, is_nested);
      } else if ("*+?".includes(src[this.pos])) {
        if (last_sym_start === out_elements.length) {
          throw new GrammarParseError(
            src,
            this.pos,
            `Expecting preceding item to */+/? at ${this.pos}`,
          );
        }
        const sub_rule_id = this.generate_symbol_id(rule_name);
        const sub_rule = out_elements.slice(last_sym_start);
        if ("*+".includes(src[this.pos])) {
          sub_rule.push(new InternalRuleDefReference(sub_rule_id));
        }
        sub_rule.push(new InternalRuleDefAlt());
        if (src[this.pos] === "+") {
          sub_rule.push(...out_elements.slice(last_sym_start));
        }
        sub_rule.push(new InternalRuleDefEnd());
        this.add_rule(sub_rule_id, sub_rule);
        out_elements.splice(
          last_sym_start,
          out_elements.length - last_sym_start,
          new InternalRuleDefReference(sub_rule_id),
        );
        this.pos = parse_space(src, this.pos + 1, is_nested);
      } else {
        break;
      }
    }
  }

  parse_alternates(rule_name: string, rule_id: number, depth: number = 0): void {
    const src = this.src;
    const rule: InternalRuleDef[] = [];
    this.parse_sequence(rule_name, rule, depth);
    // Ensure that this.pos is within bounds before checking src[this.pos]
    while (this.pos < src.length && src[this.pos] === "|") {
      this.check_duration();
      rule.push(new InternalRuleDefAlt());
      this.pos = parse_space(src, this.pos + 1, true);
      this.parse_sequence(rule_name, rule, depth);
    }
    rule.push(new InternalRuleDefEnd());
    this.add_rule(rule_id, rule);
  }
}
