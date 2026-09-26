import { GrammarParseError } from '../utils/errors/grammar-parse-error.js';
import { isWordChar } from './is-word-char.js';
import { parseChar } from './parse-char.js';
import { parseName } from './parse-name.js';
import { parseSpace } from './parse-space.js';
import { SymbolIds } from './symbol-ids.js';
import { InternalRuleDef, InternalRuleType } from './types.js';

const WHITESPACE = /\s/;

export class RulesBuilder {
  public pos = 0;
  public symbolIds = new SymbolIds();
  // A sparse list: entries are `null` until the rule with that id is defined.
  public rules: (InternalRuleDef[] | null)[] = [];
  public src: string;
  public start: number;
  private timeLimit: number;

  constructor(src: string, limit = 1000) {
    this.src = src;
    this.start = performance.now();
    this.timeLimit = limit;
    this.parse(src);
  }

  private at(pos: number): string {
    return pos >= 0 && pos < this.src.length ? this.src[pos] : '';
  }

  parse(src: string): void {
    // move cursor forward until we reach non-whitespace content
    this.pos = parseSpace(src, 0, true);

    while (this.pos < src.length) {
      this.parseRule(src);
    }

    // Validate the state to ensure that all rules are defined
    for (const rule of this.rules) {
      if (rule === null) {
        continue;
      }
      for (const elem of rule) {
        if (elem.type === InternalRuleType.RULE_REF) {
          // Ensure that the rule at that location exists
          const value = elem.value as number;
          const referenced = value < this.rules.length ? this.rules[value] : null;
          const ruleExists = referenced !== null && referenced.length > 0;
          if (!ruleExists) {
            const missingRuleName = this.symbolIds.reverseGet(value);
            let missingRulePos = this.symbolIds.getPos(missingRuleName);

            // Skip over the ::= and any whitespace
            while (
              missingRulePos < src.length &&
              (src[missingRulePos] === ':' ||
                src[missingRulePos] === '=' ||
                WHITESPACE.test(src[missingRulePos]))
            ) {
              missingRulePos += 1;
            }

            throw new GrammarParseError(
              src,
              missingRulePos,
              `Undefined rule identifier "${missingRuleName}"`,
            );
          }
        }
      }
    }
  }

  parseRule(src: string): void {
    const name = parseName(src, this.pos);
    this.pos = parseSpace(src, this.pos + name.length, false);
    const ruleId = this.getSymbolId(name, name.length);

    // Skip over whitespace characters and find the ::= sequence
    this.pos = parseSpace(src, this.pos, true);
    if (
      !(
        this.at(this.pos) === ':' &&
        this.at(this.pos + 1) === ':' &&
        this.at(this.pos + 2) === '='
      )
    ) {
      throw new GrammarParseError(src, this.pos, `Expecting ::= at ${this.pos}`);
    }
    this.pos = parseSpace(src, this.pos + 3, true);

    this.parseAlternates(name, ruleId);

    if (this.at(this.pos) === '\r') {
      this.pos += this.at(this.pos + 1) === '\n' ? 2 : 1;
    } else if (this.at(this.pos) === '\n') {
      this.pos += 1;
    } else if (this.at(this.pos)) {
      throw new GrammarParseError(
        src,
        this.pos,
        `Expecting newline or end at ${this.pos}`,
      );
    }
    this.pos = parseSpace(src, this.pos, true);
  }

  getSymbolId(src: string, length: number): number {
    const nextId = this.symbolIds.size;
    const key = src.slice(0, length);
    if (!this.symbolIds.has(key)) {
      this.symbolIds.set(key, nextId, this.pos);
    }
    return this.symbolIds.get(key);
  }

  generateSymbolId(baseName: string): number {
    const nextId = this.symbolIds.size;
    this.symbolIds.set(`${baseName}_${nextId}`, nextId, this.pos);
    return nextId;
  }

  addRule(ruleId: number, rule: InternalRuleDef[]): void {
    while (this.rules.length <= ruleId) {
      this.rules.push(null);
    }
    this.rules[ruleId] = rule;
  }

  checkDuration(): void {
    if (performance.now() - this.start > this.timeLimit) {
      throw new GrammarParseError(
        this.src,
        this.pos,
        `duration of ${this.timeLimit} exceeded:`,
      );
    }
  }

  parseSequence(
    ruleName: string,
    outElements: InternalRuleDef[],
    depth = 0,
  ): void {
    const isNested = depth !== 0;
    const src = this.src;
    let lastSymStart = outElements.length;
    while (this.at(this.pos)) {
      const char = this.at(this.pos);
      if (char === '"') {
        this.pos += 1;
        lastSymStart = outElements.length;
        while (this.at(this.pos) !== '"') {
          this.checkDuration();
          const [value, incPos] = parseChar(src, this.pos);
          outElements.push(new InternalRuleDef(InternalRuleType.CHAR, [value]));
          // Adjusting pos by the length of parsed characters
          this.pos += incPos;
        }
        this.pos = parseSpace(src, this.pos + 1, isNested);
      } else if (char === '[') {
        this.pos += 1;
        let startType = InternalRuleType.CHAR;
        if (this.at(this.pos) === '^') {
          this.pos += 1;
          startType = InternalRuleType.CHAR_NOT;
        }
        lastSymStart = outElements.length;
        while (this.at(this.pos) !== ']') {
          this.checkDuration();
          const type =
            lastSymStart < outElements.length
              ? InternalRuleType.CHAR_ALT
              : startType;
          const [startcharValue, incPos] = parseChar(src, this.pos);
          this.pos += incPos;
          if (
            type === InternalRuleType.CHAR ||
            type === InternalRuleType.CHAR_NOT
          ) {
            outElements.push(new InternalRuleDef(type, [startcharValue]));
          } else {
            outElements.push(new InternalRuleDef(type, startcharValue));
          }

          if (this.at(this.pos) === '-' && this.at(this.pos + 1) !== ']') {
            this.pos += 1;
            const [endcharValue, endIncPos] = parseChar(src, this.pos);
            outElements.push(
              new InternalRuleDef(
                InternalRuleType.CHAR_RNG_UPPER,
                endcharValue,
              ),
            );
            this.pos += endIncPos;
          }
        }
        this.pos = parseSpace(src, this.pos + 1, isNested);
      } else if (isWordChar(char)) {
        const name = parseName(src, this.pos);
        const refRuleId = this.getSymbolId(name, name.length);
        this.pos += name.length;
        this.pos = parseSpace(src, this.pos, isNested);

        lastSymStart = outElements.length;
        outElements.push(
          new InternalRuleDef(InternalRuleType.RULE_REF, refRuleId),
        );
      } else if (char === '(') {
        this.pos = parseSpace(src, this.pos + 1, true);
        const subRuleId = this.generateSymbolId(ruleName);
        this.parseAlternates(ruleName, subRuleId, depth + 1);
        lastSymStart = outElements.length;
        outElements.push(
          new InternalRuleDef(InternalRuleType.RULE_REF, subRuleId),
        );
        if (this.at(this.pos) !== ')') {
          throw new GrammarParseError(
            src,
            this.pos,
            `Expecting ')' at ${this.pos}`,
          );
        }
        this.pos = parseSpace(src, this.pos + 1, isNested);
      } else if (char === '*' || char === '+' || char === '?') {
        if (lastSymStart === outElements.length) {
          throw new GrammarParseError(
            src,
            this.pos,
            `Expecting preceding item to */+/? at ${this.pos}`,
          );
        }
        const subRuleId = this.generateSymbolId(ruleName);
        const subRule = outElements.slice(lastSymStart);
        if (char === '*' || char === '+') {
          subRule.push(
            new InternalRuleDef(InternalRuleType.RULE_REF, subRuleId),
          );
        }
        subRule.push(new InternalRuleDef(InternalRuleType.ALT));
        if (char === '+') {
          subRule.push(...outElements.slice(lastSymStart));
        }
        subRule.push(new InternalRuleDef(InternalRuleType.END));
        this.addRule(subRuleId, subRule);
        outElements.length = lastSymStart;
        outElements.push(
          new InternalRuleDef(InternalRuleType.RULE_REF, subRuleId),
        );
        this.pos = parseSpace(src, this.pos + 1, isNested);
      } else {
        break;
      }
    }
  }

  parseAlternates(ruleName: string, ruleId: number, depth = 0): void {
    const src = this.src;
    const rule: InternalRuleDef[] = [];
    this.parseSequence(ruleName, rule, depth);
    while (this.at(this.pos) === '|') {
      this.checkDuration();
      rule.push(new InternalRuleDef(InternalRuleType.ALT));
      this.pos = parseSpace(src, this.pos + 1, true);
      this.parseSequence(ruleName, rule, depth);
    }
    rule.push(new InternalRuleDef(InternalRuleType.END));
    this.addRule(ruleId, rule);
  }
}
