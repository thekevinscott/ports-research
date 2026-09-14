import type { GraphNode } from './graph-node.js';

/**
 * A reference to another rule in the graph.
 *
 * RuleRefs should never be exposed to the end user; they are resolved away
 * while walking the graph.
 */
export class RuleRef {
  // an insertion ordered set of GraphNodes.
  private _nodes?: Set<GraphNode>;

  constructor(public value: number) {}

  get nodes(): Set<GraphNode> {
    if (this._nodes === undefined) {
      throw new Error('Nodes are not set');
    }
    return this._nodes;
  }

  set nodes(nodes: Iterable<GraphNode>) {
    this._nodes = new Set(nodes);
  }
}
