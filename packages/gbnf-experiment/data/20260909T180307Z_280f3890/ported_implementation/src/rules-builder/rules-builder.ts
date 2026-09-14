import { GrammarParseError } from '../utils/errors/index.js';
import { isWordChar } from './is-word-char.js';
import { parseChar } from './parse-char.js';
import { parseName } from './parse-name.js';
import { parseSpace } from './parse-space.js';
import {
  type InternalRuleDef,
  InternalRuleDefAlt,
  InternalRuleDefChar,
  InternalRuleDefCharAlt,
  InternalRuleDefCharNot,
  InternalRuleDefCharRngUpper,
  InternalRuleDefEnd,
  InternalRuleDefReference,
  InternalRuleType,
} from './rules-builder-types.js';
import { SymbolIds } from './symbol-ids.js';

type OutElementType =
  | typeof InternalRuleType.CHAR
  | typeof InternalRuleType.CHAR_NOT
  | typeof InternalRuleType.CHAR_RNG_UPPER
  | typeof InternalRuleType.ALT
  | typeof InternalRuleType.END
  | typeof InternalRuleType.CHAR_ALT;

export const getOutElements = (
  typeOfRule: OutElementType,
  startcharValue: number,
): InternalRuleDef => {
  switch (typeOfRule) {
    case InternalRuleType.CHAR:
      return new InternalRuleDefChar([startcharValue]);
    case InternalRuleType.CHAR_NOT:
      return new InternalRuleDefCharNot([startcharValue]);
    case InternalRuleType.CHAR_RNG_UPPER:
      return new InternalRuleDefCharRngUpper(startcharValue);
    case InternalRuleType.ALT:
      return new InternalRuleDefAlt();
    case InternalRuleType.END:
      return new InternalRuleDefEnd();
    case InternalRuleType.CHAR_ALT:
      return new InternalRuleDefCharAlt(startcharValue);
    default:
      throw new Error(`Invalid type: ${String(typeOfRule)}`);
  }
};

export class RulesBuilder {
  pos = 0;
  readonly symbolIds = new SymbolIds();
  readonly rules: InternalRuleDef[][] = [];
  readonly src: string;
  readonly start: number;
  readonly timeLimit: number;

  constructor(src: string, limit = 1000) {
    this.src = src;
    this.start = Date.now() / 1000;
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
        if (elem.type === InternalRuleType.REFERENCE) {
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
                /\s/.test(src[missingRulePos] as string))
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
    if (
      !(
        this.pos + 2 < src.length && // Ensure the position + 2 is within bounds
        src[this.pos] === ':' &&
        src[this.pos + 1] === ':' &&
        src[this.pos + 2] === '='
      )
    ) {
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
    if (Date.now() / 1000 - this.start > this.timeLimit) {
      throw new GrammarParseError(this.src, this.pos, `Duration of ${this.timeLimit} exceeded`);
    }
  }

  parseSequence(ruleName: string, outElements: InternalRuleDef[], depth = 0): void {
    const isNested = depth !== 0;
    const src = this.src;
    let lastSymStart = outElements.length;

    while (this.pos < src.length) {
      if (src[this.pos] === '"') {
        this.pos += 1;
        lastSymStart = outElements.length;
        while (src[this.pos] !== '"') {
          this.checkDuration();
          const [value, incPos] = parseChar(src, this.pos);
          outElements.push(new InternalRuleDefChar([value]));
          this.pos += incPos;
        }
        this.pos = parseSpace(src, this.pos + 1, isNested);
      } else if (src[this.pos] === '[') {
        this.pos += 1;
        let startType: OutElementType = InternalRuleType.CHAR;
        if (src[this.pos] === '^') {
          this.pos += 1;
          startType = InternalRuleType.CHAR_NOT;
        }
        lastSymStart = outElements.length;
        while (src[this.pos] !== ']') {
          this.checkDuration();
          const type: OutElementType =
            lastSymStart < outElements.length ? InternalRuleType.CHAR_ALT : startType;
          const [startcharValue, incPos] = parseChar(src, this.pos);
          this.pos += incPos;
          outElements.push(getOutElements(type, startcharValue));

          if (src[this.pos] === '-' && src[this.pos + 1] !== ']') {
            this.pos += 1;
            const [endcharValue, endIncPos] = parseChar(src, this.pos);
            outElements.push(new InternalRuleDefCharRngUpper(endcharValue));
            this.pos += endIncPos;
          }
        }
        this.pos = parseSpace(src, this.pos + 1, isNested);
      } else if (isWordChar(src[this.pos] as string)) {
        const name = parseName(src, this.pos);
        const refRuleId = this.getSymbolId(name, name.length);
        this.pos += name.length;
        this.pos = parseSpace(src, this.pos, isNested);

        lastSymStart = outElements.length;
        outElements.push(new InternalRuleDefReference(refRuleId));
      } else if (src[this.pos] === '(') {
        this.pos = parseSpace(src, this.pos + 1, true);
        const subRuleId = this.generateSymbolId(ruleName);
        this.parseAlternates(ruleName, subRuleId, depth + 1);
        lastSymStart = outElements.length;
        outElements.push(new InternalRuleDefReference(subRuleId));
        if (src[this.pos] !== ')') {
          throw new GrammarParseError(src, this.pos, `Expecting ')' at ${this.pos}`);
        }
        this.pos = parseSpace(src, this.pos + 1, isNested);
      } else if (src[this.pos] === '*' || src[this.pos] === '+' || src[this.pos] === '?') {
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
          subRule.push(new InternalRuleDefReference(subRuleId));
        }
        subRule.push(new InternalRuleDefAlt());
        if (src[this.pos] === '+') {
          subRule.push(...outElements.slice(lastSymStart));
        }
        subRule.push(new InternalRuleDefEnd());
        this.addRule(subRuleId, subRule);
        outElements.splice(
          lastSymStart,
          outElements.length - lastSymStart,
          new InternalRuleDefReference(subRuleId),
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
    // Ensure that this.pos is within bounds before checking src[this.pos]
    while (this.pos < src.length && src[this.pos] === '|') {
      this.checkDuration();
      rule.push(new InternalRuleDefAlt());
      this.pos = parseSpace(src, this.pos + 1, true);
      this.parseSequence(ruleName, rule, depth);
    }
    rule.push(new InternalRuleDefEnd());
    this.addRule(ruleId, rule);
  }
}
