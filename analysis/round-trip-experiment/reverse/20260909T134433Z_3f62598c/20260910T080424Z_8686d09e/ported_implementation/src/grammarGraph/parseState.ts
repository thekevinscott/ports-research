import { getSerializedRuleKey } from './getSerializedRuleKey.js';
import type { Graph, Pointers } from './graph.js';
import type { ResolvedRule, ValidInput } from './types.js';

export class ParseState {
  private graph: Graph;
  private pointers: Pointers;

  constructor(graph: Graph, pointers: Pointers) {
    this.graph = graph;
    this.pointers = pointers;
  }

  * rules(): Generator<ResolvedRule> {
    const seen = new Set<string>();
    for (const pointer of this.pointers) {
      const rule = pointer.rule as ResolvedRule;
      const key = getSerializedRuleKey(rule);
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
