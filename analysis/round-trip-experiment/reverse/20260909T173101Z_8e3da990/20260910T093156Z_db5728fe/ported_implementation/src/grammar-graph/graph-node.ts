import { Colorize, colorize as defaultColorize } from './colorize.js';
import type { GraphPointer } from './graph-pointer.js';
import { printGraphNode } from './print.js';
import type { UnresolvedRule } from './types.js';

export interface GraphNodeMeta {
  stackId: number;
  pathId: number;
  stepId: number;
}

export class GraphNode {
  rule: UnresolvedRule;
  meta: GraphNodeMeta;
  next: GraphNode | undefined;
  #id: string | undefined;

  constructor(rule: UnresolvedRule, meta: GraphNodeMeta, next?: GraphNode) {
    this.rule = rule;
    if (!meta) {
      throw new Error('Meta is undefined');
    }
    this.meta = meta;
    this.next = next;
  }

  get id(): string {
    if (!this.#id) {
      const { stackId, pathId, stepId } = this.meta;
      this.#id = `${stackId},${pathId},${stepId}`;
    }
    return this.#id;
  }

  print(
    pointers?: Iterable<GraphPointer>,
    showPosition = false,
    colorize: Colorize = defaultColorize,
  ): string {
    return printGraphNode(this, pointers, showPosition, colorize);
  }

  toString(): string {
    return this.print(undefined, false);
  }
}
