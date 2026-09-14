import type { Graph, Pointers } from './graph.js';
import { isRuleEnd } from './type-guards.js';
import type { ResolvedRule, ValidInput } from './types.js';

/** The deduplication key used by `rules()`. */
const serializeRule = (rule: ResolvedRule): string =>
  isRuleEnd(rule)
    ? JSON.stringify({ type: rule.type })
    : JSON.stringify({ type: rule.type, value: rule.value });

/**
 * The immutable parse state returned by `GBNF`.
 *
 * Iterating it yields the rules the grammar will accept next; `add` returns a new
 * state advanced past some input.
 */
export class ParseState {
  private readonly graph: Graph;
  private readonly pointers: Pointers;

  constructor(graph: Graph, pointers: Pointers) {
    this.graph = graph;
    this.pointers = pointers;
  }

  *[Symbol.iterator](): IterableIterator<ResolvedRule> {
    yield* this.rules();
  }

  *rules(): IterableIterator<ResolvedRule> {
    const seen = new Set<string>();
    for (const pointer of this.pointers) {
      const rule = pointer.rule as ResolvedRule;
      const key = serializeRule(rule);
      if (!seen.has(key)) {
        seen.add(key);
        yield rule;
      }
    }
  }

  add(input: ValidInput): ParseState {
    return new ParseState(this.graph, this.graph.add(input, this.pointers));
  }

  get size(): number {
    return [...this.rules()].length;
  }

  get grammar(): string {
    return this.graph.grammar;
  }

  toString(): string {
    return `ParseState(${JSON.stringify([...this.rules()])})`;
  }
}
