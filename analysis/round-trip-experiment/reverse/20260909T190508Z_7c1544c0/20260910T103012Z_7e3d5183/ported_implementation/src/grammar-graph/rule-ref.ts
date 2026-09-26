import type { GraphNode } from './graph-node.js';

/**
 * A reference to another rule, resolved to its nodes once the graph is built.
 *
 * The nodes are already distinct, so a list preserves both uniqueness and
 * iteration order.
 */
export class RuleRef {
  public value: number;
  private _nodes: GraphNode[] | undefined = undefined;

  constructor(value: number) {
    this.value = value;
  }

  get nodes(): GraphNode[] {
    if (this._nodes === undefined) {
      throw new Error('Nodes are not set');
    }
    return this._nodes;
  }

  set nodes(nodes: GraphNode[]) {
    this._nodes = [...nodes];
  }
}
