import type { GraphNode } from './graph-node.js';

/** A reference to another rule; resolved to concrete nodes by the `Graph`. */
export class RuleRef {
  value: number;
  private _nodes: Set<GraphNode> | undefined = undefined;

  constructor(value: number) {
    this.value = value;
  }

  get nodes(): Set<GraphNode> {
    if (this._nodes === undefined) {
      throw new Error('Nodes are not set');
    }
    return this._nodes;
  }

  set nodes(nodes: Set<GraphNode>) {
    this._nodes = new Set(nodes);
  }

  toString(): string {
    return `RuleRef(${this.value})`;
  }
}
