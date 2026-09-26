import type { GraphNode } from './graph-node';
import { RuleType } from './grammar-graph-types';

export class RuleRef {
  type: typeof RuleType.REF = RuleType.REF;
  value: number;
  private nodesSet: Set<GraphNode> | undefined = undefined;

  constructor(value: number) {
    this.value = value;
  }

  get nodes(): Set<GraphNode> {
    if (this.nodesSet === undefined) {
      throw new Error('Nodes are not set');
    }
    return this.nodesSet;
  }

  set nodes(nodes: Set<GraphNode>) {
    this.nodesSet = nodes;
  }
}
