import { GrammarParseError } from '../utils/errors/grammar-parse-error';
import { isWordChar } from './is-word-char';
import { parseChar } from './parse-char';
import { parseName } from './parse-name';
import { parseSpace } from './parse-space';
import { SymbolIds } from './symbol-ids';
import { InternalRuleDef, InternalRuleType } from './types';

const WHITESPACE = /\s/;

export class RulesBuilder {
  public pos = 0;
  public symbolIds = new SymbolIds();
  public rules: (InternalRuleDef[] | undefined)[] = [];
  public src: string;
  public start: number;
  private timeLimit: number;

  constructor(src: string, limit = 1000) {
    this.src = src;
    this.start = performance.now();
    this.timeLimit = limit;
    this.parse(src);
  }

  private parse(src: string): void {
    // move cursor forward until we reach non-whitespace content
    this.pos = parseSpace(src, 0, true);

    while (this.pos < src.length) {
      this.parseRule(src);
    }

    // Validate the state to ensure that all rules are defined
    for (const rule of this.rules) {
      if (rule === undefined) {
        continue;
      }
      for (const elem of rule) {
        if (elem.type === InternalRuleType.RULE_REF) {
          // Ensure that the rule at that location exists
          const referenced = this.rules[elem.value];
          const ruleExists =
            elem.value < this.rules.length &&
            referenced !== undefined &&
            referenced.length > 0;
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
              src,
              missingRulePos,
              `Undefined rule identifier "${missingRuleName}"`
            );
          }
        }
      }
    }
  }

  public parseRule(src: string): void {
    const name = parseName(src, this.pos);
    this.pos = parseSpace(src, this.pos + name.length, false);
    const ruleId = this.getSymbolId(name, name.length);

    // Skip over whitespace characters and find the ::= sequence
    this.pos = parseSpace(src, this.pos, true);
    if (!(src[this.pos] === ':' && src[this.pos + 1] === ':' && src[this.pos + 2] === '=')) {
      throw new GrammarParseError(src, this.pos, `Expecting ::= at ${this.pos}`);
    }
    this.pos = parseSpace(src, this.pos + 3, true);

    this.parseAlternates(name, ruleId);

    if (src[this.pos] === '\r') {
      this.pos += src[this.pos + 1] === '\n' ? 2 : 1;
    } else if (src[this.pos] === '\n') {
      this.pos += 1;
    } else if (src[this.pos]) {
      throw new GrammarParseError(src, this.pos, `Expecting newline or end at ${this.pos}`);
    }
    this.pos = parseSpace(src, this.pos, true);
  }

  public getSymbolId(src: string, length: number): number {
    const nextId = this.symbolIds.size;
    const key = src.slice(0, length);
    if (!this.symbolIds.has(key)) {
      this.symbolIds.set(key, nextId, this.pos);
    }
    return this.symbolIds.get(key);
  }

  public generateSymbolId(baseName: string): number {
    const nextId = this.symbolIds.size;
    this.symbolIds.set(`${baseName}_${nextId}`, nextId, this.pos);
    return nextId;
  }

  public addRule(ruleId: number, rule: InternalRuleDef[]): void {
    this.rules[ruleId] = rule;
  }

  public checkDuration(): void {
    if (performance.now() - this.start > this.timeLimit) {
      throw new GrammarParseError(
        this.src,
        this.pos,
        `duration of ${this.timeLimit} exceeded:`
      );
    }
  }

  public parseSequence(
    ruleName: string,
    outElements: InternalRuleDef[],
    depth = 0
  ): void {
    const isNested = depth !== 0;
    const src = this.src;
    let lastSymStart = outElements.length;
    while (src[this.pos]) {
      const char = src[this.pos];
      if (char === '"') {
        this.pos += 1;
        lastSymStart = outElements.length;
        while (src[this.pos] !== '"') {
          this.checkDuration();
          const [value, incPos] = parseChar(src, this.pos);
          outElements.push({ type: InternalRuleType.CHAR, value: [value] });
          this.pos += incPos; // Adjusting pos by the length of parsed characters
        }
        this.pos = parseSpace(src, this.pos + 1, isNested);
      } else if (char === '[') {
        this.pos += 1;
        let startType = InternalRuleType.CHAR as
          | InternalRuleType.CHAR
          | InternalRuleType.CHAR_NOT;
        if (src[this.pos] === '^') {
          this.pos += 1;
          startType = InternalRuleType.CHAR_NOT;
        }
        lastSymStart = outElements.length;
        while (src[this.pos] !== ']') {
          this.checkDuration();
          const type =
            lastSymStart < outElements.length ? InternalRuleType.CHAR_ALT : startType;
          const [startcharValue, incPos] = parseChar(src, this.pos);
          this.pos += incPos;
          if (type === InternalRuleType.CHAR || type === InternalRuleType.CHAR_NOT) {
            outElements.push({ type, value: [startcharValue] });
          } else {
            outElements.push({ type, value: startcharValue });
          }

          if (src[this.pos] === '-' && src[this.pos + 1] !== ']') {
            this.pos += 1;
            const [endcharValue, endIncPos] = parseChar(src, this.pos);
            outElements.push({
              type: InternalRuleType.CHAR_RNG_UPPER,
              value: endcharValue,
            });
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
        outElements.push({ type: InternalRuleType.RULE_REF, value: refRuleId });
      } else if (char === '(') {
        this.pos = parseSpace(src, this.pos + 1, true);
        const subRuleId = this.generateSymbolId(ruleName);
        this.parseAlternates(ruleName, subRuleId, depth + 1);
        lastSymStart = outElements.length;
        outElements.push({ type: InternalRuleType.RULE_REF, value: subRuleId });
        if (src[this.pos] !== ')') {
          throw new GrammarParseError(src, this.pos, `Expecting ')' at ${this.pos}`);
        }
        this.pos = parseSpace(src, this.pos + 1, isNested);
      } else if (char === '*' || char === '+' || char === '?') {
        if (lastSymStart === outElements.length) {
          throw new GrammarParseError(
            src,
            this.pos,
            `Expecting preceding item to */+/? at ${this.pos}`
          );
        }
        const subRuleId = this.generateSymbolId(ruleName);
        const subRule: InternalRuleDef[] = outElements.slice(lastSymStart);
        if (char === '*' || char === '+') {
          subRule.push({ type: InternalRuleType.RULE_REF, value: subRuleId });
        }
        subRule.push({ type: InternalRuleType.ALT });
        if (char === '+') {
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

  public parseAlternates(ruleName: string, ruleId: number, depth = 0): void {
    const src = this.src;
    const rule: InternalRuleDef[] = [];
    this.parseSequence(ruleName, rule, depth);
    while (src[this.pos] === '|') {
      this.checkDuration();
      rule.push({ type: InternalRuleType.ALT });
      this.pos = parseSpace(src, this.pos + 1, true);
      this.parseSequence(ruleName, rule, depth);
    }
    rule.push({ type: InternalRuleType.END });
    this.addRule(ruleId, rule);
  }
}
