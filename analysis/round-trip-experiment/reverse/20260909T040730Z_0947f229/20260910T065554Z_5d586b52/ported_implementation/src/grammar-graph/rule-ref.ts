/** Port of `gbnf/grammar_graph/rule_ref.py`. */

import type { GraphNode } from './graph-node.js';

export class RuleRef {
  #nodes: GraphNode[] | undefined = undefined;

  constructor(public value: number) {}

  get nodes(): GraphNode[] {
    if (this.#nodes === undefined) {
      throw new Error('Nodes are not set');
    }
    return this.#nodes;
  }

  // An array rather than a set: iteration order has to be deterministic, and
  // only unique nodes are ever inserted.
  set nodes(nodes: Iterable<GraphNode>) {
    this.#nodes = [...nodes];
  }

  toString(): string {
    return `RuleRef(${this.value})`;
  }
}
