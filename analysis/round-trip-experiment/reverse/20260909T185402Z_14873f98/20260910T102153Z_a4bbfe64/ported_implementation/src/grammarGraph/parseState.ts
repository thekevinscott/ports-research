import type { Graph, Pointers } from './graph';
import type { Rule, ValidInput } from './types';

/**
 * An immutable view of the parse: the rules that may come next.
 *
 * Iterate it for the possible rules, and `add` input to advance it.
 */
export class ParseState {
  constructor(
    private graph: Graph,
    private pointers: Pointers,
  ) {}

  *[Symbol.iterator](): IterableIterator<Rule> {
    yield* this.rules();
  }

  *rules(): IterableIterator<Rule> {
    const seen = new Set<string>();
    for (const pointer of this.pointers) {
      const rule = pointer.rule as Rule;
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
}
