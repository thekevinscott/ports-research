import type { GraphNode } from './graph-node.js';

export class RuleRef {
  value: number;
  // an array rather than a set: the order the referenced nodes are visited in
  // decides the order rules come back out of the graph.
  #nodes: GraphNode[] | undefined;

  constructor(value: number) {
    this.value = value;
  }

  get nodes(): GraphNode[] {
    if (this.#nodes === undefined) {
      throw new Error('Nodes are not set');
    }
    return this.#nodes;
  }

  set nodes(nodes: GraphNode[]) {
    this.#nodes = [...nodes];
  }

  toString(): string {
    return `RuleRef(${this.value})`;
  }
}
