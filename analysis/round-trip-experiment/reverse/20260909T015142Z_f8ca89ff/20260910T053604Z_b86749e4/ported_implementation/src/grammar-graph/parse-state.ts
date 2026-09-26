import type { Graph } from './graph';
import type { Pointers, ResolvedRule, ValidInput } from './types';

/**
 * An immutable view of the parser's position within a grammar.
 *
 * Iterate it to see the rules that may come next; call `add` with more input to
 * get the next state.
 */
export class ParseState {
  private graph: Graph;
  private pointers: Pointers;

  constructor(graph: Graph, pointers: Pointers) {
    this.graph = graph;
    this.pointers = pointers;
  }

  public *[Symbol.iterator](): Generator<ResolvedRule> {
    yield* this.rules();
  }

  public *rules(): Generator<ResolvedRule> {
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

  public add(input: ValidInput): ParseState {
    return new ParseState(this.graph, this.graph.add(input, this.pointers));
  }

  public get size(): number {
    return [...this.rules()].length;
  }

  public get grammar(): string {
    return this.graph.grammar;
  }
}
