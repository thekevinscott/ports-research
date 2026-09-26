import type { GenericSet } from './generic-set.js';
import { getSerializedRuleKey } from './get-serialized-rule-key.js';
import type { Graph } from './graph.js';
import type { GraphPointer } from './graph-pointer.js';
import type { Rule, ValidInput } from './types.js';

export class ParseState {
  constructor(
    private graph: Graph,
    private pointers: GenericSet<GraphPointer, string>
  ) {}

  *[Symbol.iterator](): IterableIterator<Rule> {
    yield* this.rules();
  }

  *rules(): IterableIterator<Rule> {
    const seen = new Set<string>();
    for (const pointer of this.pointers) {
      const rule = pointer.rule as Rule;
      const key = getSerializedRuleKey(rule);
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
