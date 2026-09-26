import { toCodePoints } from "../utils/code-points.ts";
import { GrammarParseError } from "../utils/errors/grammar-parse-error.ts";
import { isWordChar } from "./is-word-char.ts";
import { parseChar } from "./parse-char.ts";
import { parseName } from "./parse-name.ts";
import { parseSpace } from "./parse-space.ts";
import {
  InternalRuleDefAlt,
  InternalRuleDefChar,
  InternalRuleDefCharAlt,
  InternalRuleDefCharNot,
  InternalRuleDefCharRngUpper,
  InternalRuleDefEnd,
  InternalRuleDefReference,
} from "./rules-builder-types.ts";
import type { InternalRuleDef } from "./rules-builder-types.ts";
import { SymbolIds } from "./symbol-ids.ts";

type InternalRuleDefConstructor =
  | typeof InternalRuleDefChar
  | typeof InternalRuleDefCharNot
  | typeof InternalRuleDefCharRngUpper
  | typeof InternalRuleDefAlt
  | typeof InternalRuleDefEnd
  | typeof InternalRuleDefCharAlt;

export const getOutElements = (
  typeOfRule: InternalRuleDefConstructor,
  startcharValue: number,
): InternalRuleDef => {
  if (typeOfRule === InternalRuleDefChar) {
    return new InternalRuleDefChar([startcharValue]);
  }
  if (typeOfRule === InternalRuleDefCharNot) {
    return new InternalRuleDefCharNot([startcharValue]);
  }
  if (typeOfRule === InternalRuleDefCharRngUpper) {
    return new InternalRuleDefCharRngUpper(startcharValue);
  }
  if (typeOfRule === InternalRuleDefAlt) {
    return new InternalRuleDefAlt();
  }
  if (typeOfRule === InternalRuleDefEnd) {
    return new InternalRuleDefEnd();
  }
  if (typeOfRule === InternalRuleDefCharAlt) {
    return new InternalRuleDefCharAlt(startcharValue);
  }

  throw new Error(`Invalid type: ${typeOfRule}`);
};

export class RulesBuilder {
  pos = 0;
  symbolIds = new SymbolIds();
  rules: InternalRuleDef[][] = [];
  src: string;
  start: number;
  timeLimit: number;
  /** `src`, split into code points; the reference implementation indexes by code point. */
  #chars: string[];

  constructor(src: string, limit = 1000) {
    this.src = src;
    this.#chars = toCodePoints(src);
    this.start = performance.now();
    this.timeLimit = limit;
    this.parse(src);
  }

  parse(src: string): void {
    const chars = this.#chars;
    this.pos = parseSpace(chars, 0, true);
    while (this.pos < chars.length) {
      this.parseRule(src);
    }

    // Validate the state to ensure that all rules are defined
    for (const rule of this.rules) {
      for (const elem of rule) {
        if (elem instanceof InternalRuleDefReference) {
          const ruleExists =
            elem.value < this.rules.length && this.rules[elem.value].length > 0;
          if (!ruleExists) {
            const missingRuleName = this.symbolIds.reverseGet(elem.value);
            let missingRulePos = this.symbolIds.getPos(missingRuleName);

            // Skip over the ::= and any whitespace
            while (
              missingRulePos < chars.length &&
              (chars[missingRulePos] === ":" ||
                chars[missingRulePos] === "=" ||
                /\s/.test(chars[missingRulePos]))
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
    const chars = this.#chars;
    const name = parseName(chars, this.pos);
    this.pos = parseSpace(chars, this.pos + name.length, false);
    const ruleId = this.getSymbolId(name, name.length);

    this.pos = parseSpace(chars, this.pos, true);
    if (
      !(
        this.pos + 2 < chars.length && // Ensure the position + 2 is within bounds
        chars[this.pos] === ":" &&
        chars[this.pos + 1] === ":" &&
        chars[this.pos + 2] === "="
      )
    ) {
      throw new GrammarParseError(src, this.pos, `Expecting ::= at ${this.pos}`);
    }
    this.pos += 3;
    this.pos = parseSpace(chars, this.pos, true);

    this.parseAlternates(name, ruleId);

    // Check if this.pos is within the bounds of src before checking for a carriage return
    if (this.pos < chars.length && chars[this.pos] === "\r") {
      this.pos += chars[this.pos + 1] === "\n" ? 2 : 1;
    } else if (this.pos < chars.length && chars[this.pos] === "\n") {
      this.pos += 1;
    } else if (this.pos < chars.length && chars[this.pos]) {
      throw new GrammarParseError(src, this.pos, `Expecting newline or end at ${this.pos}`);
    }
    this.pos = parseSpace(chars, this.pos, true);
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
      throw new GrammarParseError(
        this.src,
        this.pos,
        `Duration of ${this.timeLimit} exceeded`,
      );
    }
  }

  parseSequence(ruleName: string, outElements: InternalRuleDef[], depth = 0): void {
    const isNested = depth !== 0;
    const chars = this.#chars;
    const src = this.src;
    let lastSymStart = outElements.length;

    while (this.pos < chars.length) {
      if (chars[this.pos] === '"') {
        this.pos += 1;
        lastSymStart = outElements.length;
        while (chars[this.pos] !== '"') {
          this.checkDuration();
          const [value, incPos] = parseChar(chars, this.pos);
          outElements.push(new InternalRuleDefChar([value]));
          this.pos += incPos;
        }
        this.pos = parseSpace(chars, this.pos + 1, isNested);
      } else if (chars[this.pos] === "[") {
        this.pos += 1;
        let startType: InternalRuleDefConstructor = InternalRuleDefChar;
        if (chars[this.pos] === "^") {
          this.pos += 1;
          startType = InternalRuleDefCharNot;
        }
        lastSymStart = outElements.length;
        while (chars[this.pos] !== "]") {
          this.checkDuration();
          const type: InternalRuleDefConstructor =
            lastSymStart < outElements.length ? InternalRuleDefCharAlt : startType;
          const [startcharValue, incPos] = parseChar(chars, this.pos);
          this.pos += incPos;
          outElements.push(getOutElements(type, startcharValue));

          if (chars[this.pos] === "-" && chars[this.pos + 1] !== "]") {
            this.pos += 1;
            const [endcharValue, endIncPos] = parseChar(chars, this.pos);
            outElements.push(new InternalRuleDefCharRngUpper(endcharValue));
            this.pos += endIncPos;
          }
        }
        this.pos = parseSpace(chars, this.pos + 1, isNested);
      } else if (isWordChar(chars[this.pos])) {
        const name = parseName(chars, this.pos);
        const refRuleId = this.getSymbolId(name, name.length);
        this.pos += name.length;
        this.pos = parseSpace(chars, this.pos, isNested);

        lastSymStart = outElements.length;
        outElements.push(new InternalRuleDefReference(refRuleId));
      } else if (chars[this.pos] === "(") {
        this.pos = parseSpace(chars, this.pos + 1, true);
        const subRuleId = this.generateSymbolId(ruleName);
        this.parseAlternates(ruleName, subRuleId, depth + 1);
        lastSymStart = outElements.length;
        outElements.push(new InternalRuleDefReference(subRuleId));
        if (chars[this.pos] !== ")") {
          throw new GrammarParseError(src, this.pos, `Expecting ')' at ${this.pos}`);
        }
        this.pos = parseSpace(chars, this.pos + 1, isNested);
      } else if (chars[this.pos] === "*" || chars[this.pos] === "+" || chars[this.pos] === "?") {
        if (lastSymStart === outElements.length) {
          throw new GrammarParseError(
            src,
            this.pos,
            `Expecting preceding item to */+/? at ${this.pos}`,
          );
        }
        const subRuleId = this.generateSymbolId(ruleName);
        const subRule = outElements.slice(lastSymStart);
        if (chars[this.pos] === "*" || chars[this.pos] === "+") {
          subRule.push(new InternalRuleDefReference(subRuleId));
        }
        subRule.push(new InternalRuleDefAlt());
        if (chars[this.pos] === "+") {
          subRule.push(...outElements.slice(lastSymStart));
        }
        subRule.push(new InternalRuleDefEnd());
        this.addRule(subRuleId, subRule);
        outElements.splice(
          lastSymStart,
          outElements.length - lastSymStart,
          new InternalRuleDefReference(subRuleId),
        );
        this.pos = parseSpace(chars, this.pos + 1, isNested);
      } else {
        break;
      }
    }
  }

  parseAlternates(ruleName: string, ruleId: number, depth = 0): void {
    const chars = this.#chars;
    const rule: InternalRuleDef[] = [];
    this.parseSequence(ruleName, rule, depth);
    // Ensure that this.pos is within bounds before checking chars[this.pos]
    while (this.pos < chars.length && chars[this.pos] === "|") {
      this.checkDuration();
      rule.push(new InternalRuleDefAlt());
      this.pos = parseSpace(chars, this.pos + 1, true);
      this.parseSequence(ruleName, rule, depth);
    }
    rule.push(new InternalRuleDefEnd());
    this.addRule(ruleId, rule);
  }
}
