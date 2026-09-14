import type { GraphNode } from './graph-node';

export class RuleRef {
  value: number;
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
    // a unique, insertion-ordered collection of nodes
    this.#nodes = [...new Set(nodes)];
  }
}
