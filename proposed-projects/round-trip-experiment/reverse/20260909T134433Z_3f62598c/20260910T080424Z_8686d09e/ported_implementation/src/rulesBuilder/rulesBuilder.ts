import { charAt } from '../utils/charAt.js';
import { GrammarParseError } from '../utils/errors/GrammarParseError.js';
import { isWordChar } from './isWordChar.js';
import { parseChar } from './parseChar.js';
import { parseName } from './parseName.js';
import { parseSpace } from './parseSpace.js';
import { SymbolIds } from './symbolIds.js';
import type { InternalRuleDef } from './types.js';
import {
  InternalRuleType,
  internalRuleDefAlt,
  internalRuleDefChar,
  internalRuleDefCharAlt,
  internalRuleDefCharNot,
  internalRuleDefCharRngUpper,
  internalRuleDefEnd,
  internalRuleDefReference,
} from './types.js';

const WHITESPACE = /\s/;

const nowMs = (): number => performance.now();

export class RulesBuilder {
  pos = 0;
  symbolIds = new SymbolIds();
  // a sparse list: entries are filled in by rule id, so gaps hold null until the
  // rule they belong to is parsed
  rules: (InternalRuleDef[] | null)[] = [];
  src: string;
  start: number;
  private timeLimit: number;

  constructor(src: string, limit = 1000) {
    this.src = src;
    this.start = nowMs();
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
      if (rule === null) {
        continue;
      }
      for (const elem of rule) {
        if (elem.type === InternalRuleType.RULE_REF) {
          // Ensure that the rule at that location exists
          const referenced = elem.value < this.rules.length ? this.rules[elem.value] : null;
          const ruleExists = referenced !== null && referenced !== undefined &&
            referenced.length > 0;
          if (!ruleExists) {
            const missingRuleName = this.symbolIds.reverseGet(elem.value);
            let missingRulePos = this.symbolIds.getPos(missingRuleName);

            // Skip over the ::= and any whitespace
            while (missingRulePos < src.length && (
              src[missingRulePos] === ':' ||
              src[missingRulePos] === '=' ||
              WHITESPACE.test(src[missingRulePos])
            )) {
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

  private parseRule(src: string): void {
    const name = parseName(src, this.pos);
    this.pos = parseSpace(src, this.pos + name.length, false);
    const ruleId = this.getSymbolId(name, name.length);

    // Skip over whitespace characters and find the ::= sequence
    this.pos = parseSpace(src, this.pos, true);
    if (!(
      charAt(src, this.pos) === ':' &&
      charAt(src, this.pos + 1) === ':' &&
      charAt(src, this.pos + 2) === '='
    )) {
      throw new GrammarParseError(src, this.pos, `Expecting ::= at ${this.pos}`);
    }
    this.pos = parseSpace(src, this.pos + 3, true);

    this.parseAlternates(name, ruleId);

    if (charAt(src, this.pos) === '\r') {
      this.pos += charAt(src, this.pos + 1) === '\n' ? 2 : 1;
    } else if (charAt(src, this.pos) === '\n') {
      this.pos += 1;
    } else if (charAt(src, this.pos)) {
      throw new GrammarParseError(src, this.pos, `Expecting newline or end at ${this.pos}`);
    }
    this.pos = parseSpace(src, this.pos, true);
  }

  private getSymbolId(src: string, length: number): number {
    const nextId = this.symbolIds.size;
    const key = src.slice(0, length);
    if (!this.symbolIds.has(key)) {
      this.symbolIds.set(key, nextId, this.pos);
    }
    return this.symbolIds.get(key);
  }

  private generateSymbolId(baseName: string): number {
    const nextId = this.symbolIds.size;
    this.symbolIds.set(`${baseName}_${nextId}`, nextId, this.pos);
    return nextId;
  }

  private addRule(ruleId: number, rule: InternalRuleDef[]): void {
    while (ruleId >= this.rules.length) {
      this.rules.push(null);
    }
    this.rules[ruleId] = rule;
  }

  private checkDuration(): void {
    if (nowMs() - this.start > this.timeLimit) {
      throw new GrammarParseError(
        this.src,
        this.pos,
        `duration of ${this.timeLimit} exceeded:`,
      );
    }
  }

  private parseSequence(
    ruleName: string,
    outElements: InternalRuleDef[],
    depth = 0,
  ): void {
    const isNested = depth !== 0;
    const src = this.src;
    let lastSymStart = outElements.length;
    while (charAt(src, this.pos)) {
      if (charAt(src, this.pos) === '"') {
        this.pos += 1;
        lastSymStart = outElements.length;
        while (charAt(src, this.pos) !== '"') {
          this.checkDuration();
          const [value, incPos] = parseChar(src, this.pos);
          outElements.push(internalRuleDefChar([value]));
          // Adjusting pos by the length of parsed characters
          this.pos += incPos;
        }
        this.pos = parseSpace(src, this.pos + 1, isNested);
      } else if (charAt(src, this.pos) === '[') {
        this.pos += 1;
        let startType = InternalRuleType.CHAR;
        if (charAt(src, this.pos) === '^') {
          this.pos += 1;
          startType = InternalRuleType.CHAR_NOT;
        }
        lastSymStart = outElements.length;
        while (charAt(src, this.pos) !== ']') {
          this.checkDuration();
          const type = lastSymStart < outElements.length
            ? InternalRuleType.CHAR_ALT
            : startType;
          const [startcharValue, incPos] = parseChar(src, this.pos);
          this.pos += incPos;
          if (type === InternalRuleType.CHAR) {
            outElements.push(internalRuleDefChar([startcharValue]));
          } else if (type === InternalRuleType.CHAR_NOT) {
            outElements.push(internalRuleDefCharNot([startcharValue]));
          } else {
            outElements.push(internalRuleDefCharAlt(startcharValue));
          }

          if (charAt(src, this.pos) === '-' && charAt(src, this.pos + 1) !== ']') {
            this.pos += 1;
            const [endcharValue, endIncPos] = parseChar(src, this.pos);
            outElements.push(internalRuleDefCharRngUpper(endcharValue));
            this.pos += endIncPos;
          }
        }
        this.pos = parseSpace(src, this.pos + 1, isNested);
      } else if (isWordChar(charAt(src, this.pos))) {
        const name = parseName(src, this.pos);
        const refRuleId = this.getSymbolId(name, name.length);
        this.pos += name.length;
        this.pos = parseSpace(src, this.pos, isNested);

        lastSymStart = outElements.length;
        outElements.push(internalRuleDefReference(refRuleId));
      } else if (charAt(src, this.pos) === '(') {
        this.pos = parseSpace(src, this.pos + 1, true);
        const subRuleId = this.generateSymbolId(ruleName);
        this.parseAlternates(ruleName, subRuleId, depth + 1);
        lastSymStart = outElements.length;
        outElements.push(internalRuleDefReference(subRuleId));
        if (charAt(src, this.pos) !== ')') {
          throw new GrammarParseError(src, this.pos, `Expecting ')' at ${this.pos}`);
        }
        this.pos = parseSpace(src, this.pos + 1, isNested);
      } else if (['*', '+', '?'].includes(charAt(src, this.pos))) {
        if (lastSymStart === outElements.length) {
          throw new GrammarParseError(
            src,
            this.pos,
            `Expecting preceding item to */+/? at ${this.pos}`,
          );
        }
        const subRuleId = this.generateSymbolId(ruleName);
        const subRule: InternalRuleDef[] = outElements.slice(lastSymStart);
        if (charAt(src, this.pos) === '*' || charAt(src, this.pos) === '+') {
          subRule.push(internalRuleDefReference(subRuleId));
        }
        subRule.push(internalRuleDefAlt());
        if (charAt(src, this.pos) === '+') {
          subRule.push(...outElements.slice(lastSymStart));
        }
        subRule.push(internalRuleDefEnd());
        this.addRule(subRuleId, subRule);
        outElements.length = lastSymStart;
        outElements.push(internalRuleDefReference(subRuleId));
        this.pos = parseSpace(src, this.pos + 1, isNested);
      } else {
        break;
      }
    }
  }

  private parseAlternates(ruleName: string, ruleId: number, depth = 0): void {
    const src = this.src;
    const rule: InternalRuleDef[] = [];
    this.parseSequence(ruleName, rule, depth);
    while (charAt(src, this.pos) === '|') {
      this.checkDuration();
      rule.push(internalRuleDefAlt());
      this.pos = parseSpace(src, this.pos + 1, true);
      this.parseSequence(ruleName, rule, depth);
    }
    rule.push(internalRuleDefEnd());
    this.addRule(ruleId, rule);
  }
}
