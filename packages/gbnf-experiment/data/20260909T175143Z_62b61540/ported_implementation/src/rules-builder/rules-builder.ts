import { GrammarParseError } from '../utils/errors';
import { isWordChar } from './is-word-char';
import { parseChar } from './parse-char';
import { parseName } from './parse-name';
import { parseSpace } from './parse-space';
import {
  InternalRuleDef,
  InternalRuleType,
  isRuleDefRef,
} from './rules-builder-types';
import { SymbolIds } from './symbol-ids';

export const getOutElements = (
  typeOfRule: InternalRuleType,
  startCharValue: number,
): InternalRuleDef => {
  switch (typeOfRule) {
    case InternalRuleType.CHAR:
      return { type: InternalRuleType.CHAR, value: [startCharValue] };
    case InternalRuleType.CHAR_NOT:
      return { type: InternalRuleType.CHAR_NOT, value: [startCharValue] };
    case InternalRuleType.CHAR_RNG_UPPER:
      return { type: InternalRuleType.CHAR_RNG_UPPER, value: startCharValue };
    case InternalRuleType.ALT:
      return { type: InternalRuleType.ALT };
    case InternalRuleType.END:
      return { type: InternalRuleType.END };
    case InternalRuleType.CHAR_ALT:
      return { type: InternalRuleType.CHAR_ALT, value: startCharValue };
    default:
      throw new Error(`Invalid type: ${typeOfRule}`);
  }
};

const MODIFIERS = ['*', '+', '?'];

export class RulesBuilder {
  pos = 0;
  symbolIds = new SymbolIds();
  rules: InternalRuleDef[][] = [];
  src: string;
  start: number;
  timeLimit: number;

  constructor(src: string, limit = 1000) {
    this.src = src;
    this.start = performance.now();
    this.timeLimit = limit;
    this.parse(src);
  }

  parse(src: string): void {
    this.pos = parseSpace(src, 0, true);
    while (this.pos < src.length) {
      this.parseRule(src);
    }

    // Validate the state to ensure that all rules are defined
    for (const rule of this.rules) {
      for (const elem of rule) {
        if (isRuleDefRef(elem)) {
          const ruleExists = elem.value < this.rules.length && this.rules[elem.value].length > 0;
          if (!ruleExists) {
            const missingRuleName = this.symbolIds.reverseGet(elem.value);
            let missingRulePos = this.symbolIds.getPos(missingRuleName);

            // Skip over the ::= and any whitespace
            while (
              missingRulePos < src.length
              && (
                src[missingRulePos] === ':'
                || src[missingRulePos] === '='
                || /\s/.test(src[missingRulePos])
              )
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

    this.pos = parseSpace(src, this.pos, true);
    if (!(
      this.pos + 2 < src.length // Ensure the position + 2 is within bounds
      && src[this.pos] === ':'
      && src[this.pos + 1] === ':'
      && src[this.pos + 2] === '='
    )) {
      throw new GrammarParseError(src, this.pos, `Expecting ::= at ${this.pos}`);
    }
    this.pos += 3;
    this.pos = parseSpace(src, this.pos, true);

    this.parseAlternates(name, ruleId);

    // Check if this.pos is within the bounds of src before checking for a carriage return
    if (this.pos < src.length && src[this.pos] === '\r') {
      this.pos += src[this.pos + 1] === '\n' ? 2 : 1;
    } else if (this.pos < src.length && src[this.pos] === '\n') {
      this.pos += 1;
    } else if (this.pos < src.length && src[this.pos]) {
      throw new GrammarParseError(src, this.pos, `Expecting newline or end at ${this.pos}`);
    }
    this.pos = parseSpace(src, this.pos, true);
  }

  getSymbolId(src: string, length: number): number {
    const nextId = this.symbolIds.size;
    const key = src.slice(0, length);
    if (!this.symbolIds.has(key)) {
      this.symbolIds.set(key, nextId, this.pos);
    }
    return this.symbolIds.get(key) as number;
  }

  generateSymbolId(baseName: string): number {
    const nextId = this.symbolIds.size;
    this.symbolIds.set(`${baseName}_${nextId}`, nextId, this.pos);
    return nextId;
  }

  addRule(ruleId: number, rule: InternalRuleDef[]): void {
    while (this.rules.length <= ruleId) {
      this.rules.push([]);
    }
    this.rules[ruleId] = rule;
  }

  checkDuration(): void {
    if ((performance.now() - this.start) / 1000 > this.timeLimit) {
      throw new GrammarParseError(this.src, this.pos, `Duration of ${this.timeLimit} exceeded`);
    }
  }

  parseSequence(ruleName: string, outElements: InternalRuleDef[], depth = 0): void {
    const isNested = depth !== 0;
    const { src } = this;
    let lastSymStart = outElements.length;

    while (this.pos < src.length) {
      if (src[this.pos] === '"') {
        this.pos += 1;
        lastSymStart = outElements.length;
        while (src[this.pos] !== '"') {
          this.checkDuration();
          const [value, incPos] = parseChar(src, this.pos);
          outElements.push({ type: InternalRuleType.CHAR, value: [value] });
          this.pos += incPos;
        }
        this.pos = parseSpace(src, this.pos + 1, isNested);
      } else if (src[this.pos] === '[') {
        this.pos += 1;
        let startType = InternalRuleType.CHAR;
        if (src[this.pos] === '^') {
          this.pos += 1;
          startType = InternalRuleType.CHAR_NOT;
        }
        lastSymStart = outElements.length;
        while (src[this.pos] !== ']') {
          this.checkDuration();
          const type = lastSymStart < outElements.length ? InternalRuleType.CHAR_ALT : startType;
          const [startCharValue, incPos] = parseChar(src, this.pos);
          this.pos += incPos;
          outElements.push(getOutElements(type, startCharValue));

          if (src[this.pos] === '-' && src[this.pos + 1] !== ']') {
            this.pos += 1;
            const [endCharValue, endIncPos] = parseChar(src, this.pos);
            outElements.push({
              type: InternalRuleType.CHAR_RNG_UPPER,
              value: endCharValue,
            });
            this.pos += endIncPos;
          }
        }
        this.pos = parseSpace(src, this.pos + 1, isNested);
      } else if (isWordChar(src[this.pos])) {
        const name = parseName(src, this.pos);
        const refRuleId = this.getSymbolId(name, name.length);
        this.pos += name.length;
        this.pos = parseSpace(src, this.pos, isNested);

        lastSymStart = outElements.length;
        outElements.push({ type: InternalRuleType.RULE_REF, value: refRuleId });
      } else if (src[this.pos] === '(') {
        this.pos = parseSpace(src, this.pos + 1, true);
        const subRuleId = this.generateSymbolId(ruleName);
        this.parseAlternates(ruleName, subRuleId, depth + 1);
        lastSymStart = outElements.length;
        outElements.push({ type: InternalRuleType.RULE_REF, value: subRuleId });
        if (src[this.pos] !== ')') {
          throw new GrammarParseError(src, this.pos, `Expecting ')' at ${this.pos}`);
        }
        this.pos = parseSpace(src, this.pos + 1, isNested);
      } else if (MODIFIERS.includes(src[this.pos])) {
        if (lastSymStart === outElements.length) {
          throw new GrammarParseError(
            src,
            this.pos,
            `Expecting preceding item to */+/? at ${this.pos}`,
          );
        }
        const subRuleId = this.generateSymbolId(ruleName);
        const subRule = outElements.slice(lastSymStart);
        if (src[this.pos] === '*' || src[this.pos] === '+') {
          subRule.push({ type: InternalRuleType.RULE_REF, value: subRuleId });
        }
        subRule.push({ type: InternalRuleType.ALT });
        if (src[this.pos] === '+') {
          subRule.push(...outElements.slice(lastSymStart));
        }
        subRule.push({ type: InternalRuleType.END });
        this.addRule(subRuleId, subRule);
        outElements.splice(lastSymStart, outElements.length - lastSymStart, {
          type: InternalRuleType.RULE_REF,
          value: subRuleId,
        });
        this.pos = parseSpace(src, this.pos + 1, isNested);
      } else {
        break;
      }
    }
  }

  parseAlternates(ruleName: string, ruleId: number, depth = 0): void {
    const { src } = this;
    const rule: InternalRuleDef[] = [];
    this.parseSequence(ruleName, rule, depth);
    // Ensure that this.pos is within bounds before checking src[this.pos]
    while (this.pos < src.length && src[this.pos] === '|') {
      this.checkDuration();
      rule.push({ type: InternalRuleType.ALT });
      this.pos = parseSpace(src, this.pos + 1, true);
      this.parseSequence(ruleName, rule, depth);
    }
    rule.push({ type: InternalRuleType.END });
    this.addRule(ruleId, rule);
  }
}
