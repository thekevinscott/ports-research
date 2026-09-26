import type { Graph, Pointers } from './graph.js';
import type { ResolvedRule, ValidInput } from './types.js';

/**
 * An immutable view of the parser's position within a grammar.
 *
 * Iterating a `ParseState` yields the rules that may match next. Calling `add` with more
 * input returns a new `ParseState`.
 */
export class ParseState {
  private graph: Graph;
  private pointers: Pointers;

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
      const key = JSON.stringify(rule);
      if (!seen.has(key)) {
        seen.add(key);
        yield rule;
      }
    }
  }

  add(input: ValidInput): ParseState {
    const pointers = this.graph.add(input, this.pointers);
    return new ParseState(this.graph, pointers);
  }

  get size(): number {
    return [...this.rules()].length;
  }

  get grammar(): string {
    return this.graph.grammar;
  }

  toString(): string {
    return `ParseState(${[...this.rules()].map((rule) => JSON.stringify(rule)).join(', ')})`;
  }
}
