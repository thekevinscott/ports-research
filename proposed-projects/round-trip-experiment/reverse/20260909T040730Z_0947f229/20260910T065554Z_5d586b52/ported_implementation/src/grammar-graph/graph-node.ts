/** Port of `gbnf/grammar_graph/graph_node.py`. */

import { Colorize, colorize } from './colorize.js';
import { printGraphNode, type Pointers } from './print.js';
import type { UnresolvedRule } from './types.js';

export interface GraphNodeMeta {
  stackId: number;
  pathId: number;
  stepId: number;
}

export class GraphNode {
  #id: string | undefined = undefined;

  constructor(
    public rule: UnresolvedRule,
    public meta: GraphNodeMeta,
    public next?: GraphNode,
  ) {
    if (meta === undefined) {
      throw new Error('Meta is undefined');
    }
  }

  get id(): string {
    if (this.#id === undefined) {
      this.#id = `${this.meta.stackId},${this.meta.pathId},${this.meta.stepId}`;
    }
    return this.#id;
  }

  print(col: Colorize = colorize, pointers?: Pointers, showPosition = false): string {
    return printGraphNode(this, col, pointers, showPosition);
  }

  toString(): string {
    return this.print(colorize, undefined, false);
  }
}
