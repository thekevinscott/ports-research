import type { GraphNode } from './graph-node';

/**
 * A reference to another rule in the grammar.
 *
 * `nodes` is kept as an insertion-ordered collection: the order the referenced nodes
 * are walked in decides the order rules come back out of a ParseState.
 */
export class RuleRef {
  public value: number;
  private _nodes?: GraphNode[];

  constructor(value: number) {
    this.value = value;
  }

  get nodes(): GraphNode[] {
    if (this._nodes === undefined) {
      throw new Error('Nodes are not set');
    }
    return this._nodes;
  }

  set nodes(nodes: Iterable<GraphNode>) {
    const unique: GraphNode[] = [];
    const seen = new Set<GraphNode>();
    for (const node of nodes) {
      if (!seen.has(node)) {
        seen.add(node);
        unique.push(node);
      }
    }
    this._nodes = unique;
  }
}
