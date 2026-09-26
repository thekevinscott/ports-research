import type { Graph, Pointers } from './graph.ts';
import type { ResolvedRule, ValidInput } from './types.ts';

/**
 * The parse state is callable — `state('foo')` is the same as `state.add('foo')` —
 * which is done by extending `Function` and handing back a `Proxy` with an `apply`
 * trap.
 */
export interface ParseState {
  (input: ValidInput): ParseState;
}

export class ParseState extends Function {
  private _graph: Graph;
  private _pointers: Pointers;

  constructor(graph: Graph, pointers: Pointers) {
    super();
    this._graph = graph;
    this._pointers = pointers;

    return new Proxy(this, {
      apply: (target, _thisArg, args) => target.add(args[0] as ValidInput),
    });
  }

  *[Symbol.iterator](): Generator<ResolvedRule> {
    yield* this.rules();
  }

  *rules(): Generator<ResolvedRule> {
    // rules are de-duplicated, but yielded in pointer order
    const seen = new Set<ResolvedRule>();
    for (const pointer of this._pointers) {
      const rule = pointer.rule as ResolvedRule;
      if (!seen.has(rule)) {
        seen.add(rule);
        yield rule;
      }
    }
  }

  add(input: ValidInput): ParseState {
    const pointers = this._graph.add(input, this._pointers);
    return new ParseState(this._graph, pointers);
  }

  get size(): number {
    return [...this.rules()].length;
  }

  get grammar(): string {
    return this._graph.grammar;
  }

  toString(): string {
    return `ParseState([${[...this.rules()].map((rule) => JSON.stringify(rule)).join(', ')}])`;
  }
}
