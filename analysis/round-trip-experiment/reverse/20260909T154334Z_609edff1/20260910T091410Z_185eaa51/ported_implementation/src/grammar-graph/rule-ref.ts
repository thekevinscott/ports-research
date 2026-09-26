import type { GraphNode } from './graph-node';

export class RuleRef {
  value: number;
  // Ordered set of nodes, keyed by identity.
  private referencedNodes?: Set<GraphNode>;

  constructor(value: number) {
    this.value = value;
  }

  get nodes(): Set<GraphNode> {
    if (this.referencedNodes === undefined) {
      throw new Error('Nodes are not set');
    }
    return this.referencedNodes;
  }

  set nodes(nodes: Set<GraphNode>) {
    this.referencedNodes = nodes;
  }
}
