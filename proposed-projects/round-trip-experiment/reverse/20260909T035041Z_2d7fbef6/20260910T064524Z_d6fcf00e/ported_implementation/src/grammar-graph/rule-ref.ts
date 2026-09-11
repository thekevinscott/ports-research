import { GBNFError } from '../utils/errors/gbnf-error.js';
import type { GraphNode } from './graph-node.js';

/** A reference to another rule stack; resolved into graph nodes by `Graph`. */
export class RuleRef {
  value: number;
  private _nodes: GraphNode[] | undefined = undefined;

  constructor(value: number) {
    this.value = value;
  }

  get nodes(): GraphNode[] {
    if (this._nodes === undefined) {
      throw new GBNFError('Nodes are not set');
    }
    return this._nodes;
  }

  set nodes(nodes: GraphNode[]) {
    this._nodes = nodes;
  }

  toString(): string {
    return `Ref(${this.value})`;
  }
}
