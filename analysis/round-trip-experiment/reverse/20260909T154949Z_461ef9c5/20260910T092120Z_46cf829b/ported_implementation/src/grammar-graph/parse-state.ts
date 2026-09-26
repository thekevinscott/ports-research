import { getSerializedRuleKey } from './get-serialized-rule-key.js';
import type { Graph } from './graph.js';
import type { Pointers } from './types-internal.js';
import type { ResolvedRule, ValidInput } from './types.js';

/**
 * Instances are callable — `state('foo')` is `state.add('foo')` — which a `Proxy`
 * over a function provides, since a class instance is not callable on its own.
 */
const makeCallable = (state: ParseState): ParseState => new Proxy(
  ((input: ValidInput) => state.add(input)) as unknown as ParseState,
  {
    get: (_target, prop) => {
      const value = Reflect.get(state, prop, state);
      return typeof value === 'function' ? value.bind(state) : value;
    },
    has: (_target, prop) => prop in state,
    getPrototypeOf: () => ParseState.prototype,
  },
);

export interface ParseState {
  (input: ValidInput): ParseState;
}

export class ParseState {
  private graph: Graph;
  private pointers: Pointers;

  constructor(graph: Graph, pointers: Pointers) {
    this.graph = graph;
    this.pointers = pointers;
    return makeCallable(this);
  }

  *[Symbol.iterator](): IterableIterator<ResolvedRule> {
    yield* this.rules();
  }

  *rules(): IterableIterator<ResolvedRule> {
    const seen = new Set<string>();
    for (const pointer of this.pointers) {
      const rule = pointer.rule;
      const key = getSerializedRuleKey(rule);
      if (!seen.has(key)) {
        seen.add(key);
        yield rule as ResolvedRule;
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
