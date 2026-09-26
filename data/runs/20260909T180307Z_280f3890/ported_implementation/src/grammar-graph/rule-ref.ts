import type { GraphNode } from './graph-node.js';
import { RuleType } from './grammar-graph-types.js';

export class RuleRef {
  readonly type = RuleType.REF;
  #nodes: Set<GraphNode> | undefined = undefined;

  constructor(readonly value: number) {}

  get nodes(): Set<GraphNode> {
    if (this.#nodes === undefined) {
      throw new Error('Nodes are not set');
    }
    return this.#nodes;
  }

  set nodes(nodes: Set<GraphNode>) {
    this.#nodes = nodes;
  }
}
