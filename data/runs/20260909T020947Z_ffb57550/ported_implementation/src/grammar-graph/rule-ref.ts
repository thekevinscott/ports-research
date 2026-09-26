import type { GraphNode } from './graph-node.js';
import { RuleType } from './rule-type.js';

export class RuleRef {
  readonly type = RuleType.REF;
  value: number;
  #nodes: Set<GraphNode> | undefined = undefined;

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
