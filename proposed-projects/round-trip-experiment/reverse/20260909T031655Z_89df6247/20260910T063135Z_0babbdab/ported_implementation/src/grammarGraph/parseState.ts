import type { Graph, Pointers } from './graph.js';
import type { CodePointSource } from './getInputAsCodePoints.js';
import type { Rule } from './types.js';

/** An immutable view of where a parse currently stands. */
export class ParseState {
  private readonly graph: Graph;
  private readonly pointers: Pointers;

  public constructor(graph: Graph, pointers: Pointers) {
    this.graph = graph;
    this.pointers = pointers;
  }

  public *rules(): Generator<Rule> {
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

  public [Symbol.iterator](): Generator<Rule> {
    return this.rules();
  }

  public add(input: CodePointSource): ParseState {
    const pointers = this.graph.add(input, this.pointers);
    return new ParseState(this.graph, pointers);
  }

  public get size(): number {
    return [...this.rules()].length;
  }

  public get grammar(): string {
    return this.graph.grammar;
  }
}
