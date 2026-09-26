import { at, toChars } from '../utils/code-points.ts';
import { GrammarParseError } from '../utils/errors/grammar-parse-error.ts';
import { isWordChar } from './is-word-char.ts';
import { parseChar } from './parse-char.ts';
import { parseName } from './parse-name.ts';
import { parseSpace } from './parse-space.ts';
import { SymbolIds } from './symbol-ids.ts';
import { type InternalRuleDef, InternalRuleType } from './types.ts';

const WHITESPACE = /\s/;

export class RulesBuilder {
  pos = 0;
  symbolIds = new SymbolIds();
  /** A sparse array indexed by rule id; holes read back as `undefined`. */
  rules: (InternalRuleDef[] | undefined)[] = [];
  src: string;
  /** `src` as a list of code points; every position below indexes into this. */
  private chars: string[];
  private start: number;
  private timeLimit: number;

  constructor(src: string, limit = 1000) {
    this.src = src;
    this.chars = toChars(src);
    this.start = Date.now();
    this.timeLimit = limit;
    this.parse();
  }

  private at(pos: number): string {
    return at(this.chars, pos);
  }

  private parse(): void {
    const src = this.chars;
    // move cursor forward until we reach non-whitespace content
    this.pos = parseSpace(src, 0, true);

    while (this.pos < src.length) {
      this.parseRule(src);
    }

    // Validate the state to ensure that all rules are defined
    for (const rule of this.rules) {
      if (rule === undefined) {
        // a hole in the sparse array
        continue;
      }
      for (const elem of rule) {
        if (elem.type === InternalRuleType.RULE_REF) {
          // Ensure that the rule at that location exists
          const referenced = this.rules[elem.value];
          const ruleExists = referenced !== undefined && referenced.length > 0;
          if (!ruleExists) {
            const missingRuleName = this.symbolIds.reverseGet(elem.value);
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
              this.src,
              missingRulePos,
              `Undefined rule identifier "${missingRuleName}"`
            );
          }
        }
      }
    }
  }

  private parseRule(src: string[]): void {
    const name = parseName(src, this.pos);
    this.pos = parseSpace(src, this.pos + name.length, false);
    const ruleId = this.getSymbolId(name, name.length);

    // Skip over whitespace characters and find the ::= sequence
    this.pos = parseSpace(src, this.pos, true);
    if (
      !(this.at(this.pos) === ':' && this.at(this.pos + 1) === ':' && this.at(this.pos + 2) === '=')
    ) {
      throw new GrammarParseError(this.src, this.pos, `Expecting ::= at ${this.pos}`);
    }
    this.pos = parseSpace(src, this.pos + 3, true);

    this.parseAlternates(name, ruleId);

    if (this.at(this.pos) === '\r') {
      this.pos += this.at(this.pos + 1) === '\n' ? 2 : 1;
    } else if (this.at(this.pos) === '\n') {
      this.pos += 1;
    } else if (this.at(this.pos)) {
      throw new GrammarParseError(
        this.src,
        this.pos,
        `Expecting newline or end at ${this.pos}`
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
    this.rules[ruleId] = rule;
  }

  checkDuration(): void {
    if (Date.now() - this.start > this.timeLimit) {
      throw new GrammarParseError(
        this.src,
        this.pos,
        `duration of ${this.timeLimit} exceeded:`
      );
    }
  }

  parseSequence(ruleName: string, outElements: InternalRuleDef[], depth = 0): void {
    const isNested = depth !== 0;
    const src = this.chars;
    let lastSymStart = outElements.length;
    while (this.at(this.pos)) {
      if (this.at(this.pos) === '"') {
        this.pos += 1;
        lastSymStart = outElements.length;
        while (this.at(this.pos) !== '"') {
          this.checkDuration();
          const [value, incPos] = parseChar(src, this.pos);
          outElements.push({ type: InternalRuleType.CHAR, value: [value] });
          this.pos += incPos; // Adjusting pos by the length of parsed characters
        }
        this.pos = parseSpace(src, this.pos + 1, isNested);
      } else if (this.at(this.pos) === '[') {
        this.pos += 1;
        let startType: typeof InternalRuleType.CHAR | typeof InternalRuleType.CHAR_NOT =
          InternalRuleType.CHAR;
        if (this.at(this.pos) === '^') {
          this.pos += 1;
          startType = InternalRuleType.CHAR_NOT;
        }
        lastSymStart = outElements.length;
        while (this.at(this.pos) !== ']') {
          this.checkDuration();
          const type =
            lastSymStart < outElements.length ? InternalRuleType.CHAR_ALT : startType;
          const [startcharValue, incPos] = parseChar(src, this.pos);
          this.pos += incPos;
          if (type === InternalRuleType.CHAR) {
            outElements.push({ type: InternalRuleType.CHAR, value: [startcharValue] });
          } else if (type === InternalRuleType.CHAR_NOT) {
            outElements.push({ type: InternalRuleType.CHAR_NOT, value: [startcharValue] });
          } else {
            outElements.push({ type: InternalRuleType.CHAR_ALT, value: startcharValue });
          }

          if (this.at(this.pos) === '-' && this.at(this.pos + 1) !== ']') {
            this.pos += 1;
            const [endcharValue, incPos] = parseChar(src, this.pos);
            outElements.push({
              type: InternalRuleType.CHAR_RNG_UPPER,
              value: endcharValue,
            });
            this.pos += incPos;
          }
        }
        this.pos = parseSpace(src, this.pos + 1, isNested);
      } else if (isWordChar(this.at(this.pos))) {
        const name = parseName(src, this.pos);
        const refRuleId = this.getSymbolId(name, name.length);
        this.pos += name.length;
        this.pos = parseSpace(src, this.pos, isNested);

        lastSymStart = outElements.length;
        outElements.push({ type: InternalRuleType.RULE_REF, value: refRuleId });
      } else if (this.at(this.pos) === '(') {
        this.pos = parseSpace(src, this.pos + 1, true);
        const subRuleId = this.generateSymbolId(ruleName);
        this.parseAlternates(ruleName, subRuleId, depth + 1);
        lastSymStart = outElements.length;
        outElements.push({ type: InternalRuleType.RULE_REF, value: subRuleId });
        if (this.at(this.pos) !== ')') {
          throw new GrammarParseError(this.src, this.pos, `Expecting ')' at ${this.pos}`);
        }
        this.pos = parseSpace(src, this.pos + 1, isNested);
      } else if (
        this.at(this.pos) === '*' ||
        this.at(this.pos) === '+' ||
        this.at(this.pos) === '?'
      ) {
        if (lastSymStart === outElements.length) {
          throw new GrammarParseError(
            this.src,
            this.pos,
            `Expecting preceding item to */+/? at ${this.pos}`
          );
        }
        const subRuleId = this.generateSymbolId(ruleName);
        const subRule: InternalRuleDef[] = outElements.slice(lastSymStart);
        if (this.at(this.pos) === '*' || this.at(this.pos) === '+') {
          subRule.push({ type: InternalRuleType.RULE_REF, value: subRuleId });
        }
        subRule.push({ type: InternalRuleType.ALT });
        if (this.at(this.pos) === '+') {
          subRule.push(...outElements.slice(lastSymStart));
        }
        subRule.push({ type: InternalRuleType.END });
        this.addRule(subRuleId, subRule);
        outElements.splice(lastSymStart);
        outElements.push({ type: InternalRuleType.RULE_REF, value: subRuleId });
        this.pos = parseSpace(src, this.pos + 1, isNested);
      } else {
        break;
      }
    }
  }

  parseAlternates(ruleName: string, ruleId: number, depth = 0): void {
    const src = this.chars;
    const rule: InternalRuleDef[] = [];
    this.parseSequence(ruleName, rule, depth);
    while (this.at(this.pos) === '|') {
      this.checkDuration();
      rule.push({ type: InternalRuleType.ALT });
      this.pos = parseSpace(src, this.pos + 1, true);
      this.parseSequence(ruleName, rule, depth);
    }
    rule.push({ type: InternalRuleType.END });
    this.addRule(ruleId, rule);
  }
}
