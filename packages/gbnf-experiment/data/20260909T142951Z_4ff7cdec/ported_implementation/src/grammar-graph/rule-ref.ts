import { RuleType } from './grammar-graph-types.ts';
import type { GraphNode } from './graph-node.ts';

export class RuleRef {
  readonly type = RuleType.REF;
  #nodes: Set<GraphNode> | undefined = undefined;
  value: number;

  constructor(value: number) {
    this.value = value;
  }

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
