import type { GraphNode } from './graph-node.js';
import { RuleType } from './rule-type.js';

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

  equals(other: unknown): boolean {
    return other instanceof RuleRef && this.value === other.value;
  }

  toJSON(): { type: RuleType; value: number } {
    return { type: this.type, value: this.value };
  }
}
