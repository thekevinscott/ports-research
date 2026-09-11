import type { GraphNode } from './graph-node.js';
import { RuleType } from './grammar-graph-types.js';

export class RuleRef {
  type = RuleType.REF as const;
  value: number;
  private privateNodes: Set<GraphNode> | null = null;

  constructor(value: number) {
    this.value = value;
  }

  get nodes(): Set<GraphNode> {
    if (this.privateNodes === null) {
      throw new Error('Nodes are not set');
    }
    return this.privateNodes;
  }

  set nodes(nodes: Set<GraphNode>) {
    this.privateNodes = nodes;
  }
}
