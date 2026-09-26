import { dumps } from '../utils/json.js';
import type { Graph, Pointers } from './graph.js';
import { ResolvedRule, ValidInput, ruleToDict } from './types.js';

/**
 * An immutable view of where a parse currently stands.
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

  *rules(): Generator<ResolvedRule> {
    const seen = new Set<string>();
    for (const pointer of this.pointers) {
      const rule = pointer.rule as ResolvedRule;
      const key = JSON.stringify(ruleToDict(rule));
      if (!seen.has(key)) {
        seen.add(key);
        yield rule;
      }
    }
  }

  [Symbol.iterator](): Generator<ResolvedRule> {
    return this.rules();
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
    return `ParseState(${dumps(
      [...this.rules()].map((rule) => ruleToDict(rule))
    )})`;
  }
}
