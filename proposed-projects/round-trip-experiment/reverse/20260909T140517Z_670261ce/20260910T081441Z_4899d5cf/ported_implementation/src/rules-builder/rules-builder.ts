import { GrammarParseError } from '../utils/errors/grammar-parse-error.js';
import { charAt, type Chars, toChars } from '../utils/js.js';
import { isWordChar } from './is-word-char.js';
import { parseChar } from './parse-char.js';
import { parseName } from './parse-name.js';
import { parseSpace } from './parse-space.js';
import { SymbolIds } from './symbol-ids.js';
import { type InternalRuleDef, InternalRuleType } from './types.js';

const WHITESPACE = /\s/;

export class RulesBuilder {
  public pos = 0;
  public readonly symbolIds = new SymbolIds();
  public readonly rules: (InternalRuleDef[] | undefined)[] = [];

  /** The grammar as code points; `grammar` keeps the original string for errors. */
  private readonly src: Chars;
  private readonly grammar: string;
  private readonly start: number;
  private readonly timeLimit: number;

  constructor(src: string, limit = 1000) {
    this.grammar = src;
    this.src = toChars(src);
    this.start = performance.now();
    this.timeLimit = limit;
    this.parse();
  }

  private parse(): void {
    const src = this.src;

    // move cursor forward until we reach non-whitespace content
    this.pos = parseSpace(src, 0, true);

    while (this.pos < src.length) {
      this.parseRule();
    }

    // Validate the state to ensure that all rules are defined
    for (const rule of this.rules) {
      if (rule === undefined) {
        continue;
      }
      for (const elem of rule) {
        if (elem.type === InternalRuleType.RULE_REF) {
          // Ensure that the rule at that location exists
          const referenced = this.rules[elem.value as number];
          const ruleExists = referenced !== undefined && referenced.length > 0;
          if (!ruleExists) {
            const missingRuleName = this.symbolIds.reverseGet(elem.value as number);
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
              this.grammar,
              missingRulePos,
              `Undefined rule identifier "${missingRuleName}"`
            );
          }
        }
      }
    }
  }

  private parseRule(): void {
    const src = this.src;
    const name = parseName(src, this.pos);
    this.pos = parseSpace(src, this.pos + name.length, false);
    const ruleId = this.getSymbolId(name, name.length);

    // Skip over whitespace characters and find the ::= sequence
    this.pos = parseSpace(src, this.pos, true);
    if (
      !(
        charAt(src, this.pos) === ':' &&
        charAt(src, this.pos + 1) === ':' &&
        charAt(src, this.pos + 2) === '='
      )
    ) {
      throw new GrammarParseError(this.grammar, this.pos, `Expecting ::= at ${this.pos}`);
    }
    this.pos = parseSpace(src, this.pos + 3, true);

    this.parseAlternates(name, ruleId);

    if (charAt(src, this.pos) === '\r') {
      this.pos += charAt(src, this.pos + 1) === '\n' ? 2 : 1;
    } else if (charAt(src, this.pos) === '\n') {
      this.pos += 1;
    } else if (charAt(src, this.pos)) {
      throw new GrammarParseError(
        this.grammar,
        this.pos,
        `Expecting newline or end at ${this.pos}`
      );
    }
    this.pos = parseSpace(src, this.pos, true);
  }

  private getSymbolId(src: string, len: number): number {
    const nextId = this.symbolIds.size;
    const key = src.slice(0, len);
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
    while (this.rules.length <= ruleId) {
      this.rules.push(undefined);
    }
    this.rules[ruleId] = rule;
  }

  private checkDuration(): void {
    if (performance.now() - this.start > this.timeLimit) {
      throw new GrammarParseError(
        this.grammar,
        this.pos,
        `duration of ${this.timeLimit} exceeded:`
      );
    }
  }

  private parseSequence(
    ruleName: string,
    outElements: InternalRuleDef[],
    depth = 0
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
          outElements.push({ type: InternalRuleType.CHAR, value: [value] });
          this.pos += incPos; // Adjusting pos by the length of parsed characters
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
          const type =
            lastSymStart < outElements.length ? InternalRuleType.CHAR_ALT : startType;
          const [startcharValue, incPos] = parseChar(src, this.pos);
          this.pos += incPos;
          if (type === InternalRuleType.CHAR || type === InternalRuleType.CHAR_NOT) {
            outElements.push({ type, value: [startcharValue] });
          } else {
            outElements.push({ type, value: startcharValue });
          }

          if (charAt(src, this.pos) === '-' && charAt(src, this.pos + 1) !== ']') {
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
      } else if (isWordChar(charAt(src, this.pos))) {
        const name = parseName(src, this.pos);
        const refRuleId = this.getSymbolId(name, name.length);
        this.pos += name.length;
        this.pos = parseSpace(src, this.pos, isNested);

        lastSymStart = outElements.length;
        outElements.push({ type: InternalRuleType.RULE_REF, value: refRuleId });
      } else if (charAt(src, this.pos) === '(') {
        this.pos = parseSpace(src, this.pos + 1, true);
        const subRuleId = this.generateSymbolId(ruleName);
        this.parseAlternates(ruleName, subRuleId, depth + 1);
        lastSymStart = outElements.length;
        outElements.push({ type: InternalRuleType.RULE_REF, value: subRuleId });
        if (charAt(src, this.pos) !== ')') {
          throw new GrammarParseError(this.grammar, this.pos, `Expecting ')' at ${this.pos}`);
        }
        this.pos = parseSpace(src, this.pos + 1, isNested);
      } else if (['*', '+', '?'].includes(charAt(src, this.pos))) {
        if (lastSymStart === outElements.length) {
          throw new GrammarParseError(
            this.grammar,
            this.pos,
            `Expecting preceding item to */+/? at ${this.pos}`
          );
        }
        const subRuleId = this.generateSymbolId(ruleName);
        const subRule: InternalRuleDef[] = outElements.slice(lastSymStart);
        if (['*', '+'].includes(charAt(src, this.pos))) {
          subRule.push({ type: InternalRuleType.RULE_REF, value: subRuleId });
        }
        subRule.push({ type: InternalRuleType.ALT });
        if (charAt(src, this.pos) === '+') {
          subRule.push(...outElements.slice(lastSymStart));
        }
        subRule.push({ type: InternalRuleType.END });
        this.addRule(subRuleId, subRule);
        outElements.length = lastSymStart;
        outElements.push({ type: InternalRuleType.RULE_REF, value: subRuleId });
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
      rule.push({ type: InternalRuleType.ALT });
      this.pos = parseSpace(src, this.pos + 1, true);
      this.parseSequence(ruleName, rule, depth);
    }
    rule.push({ type: InternalRuleType.END });
    this.addRule(ruleId, rule);
  }
}
