import { printGraphNode } from './print.js';
import type { PrintOpts, UnresolvedRule } from './types.js';

export interface GraphNodeMeta {
  stackId: number;
  pathId: number;
  stepId: number;
}

export class GraphNode<T extends UnresolvedRule = UnresolvedRule> {
  rule: T;
  next?: GraphNode;
  meta: GraphNodeMeta;
  #id?: string;

  constructor(rule: T, meta: GraphNodeMeta, next?: GraphNode) {
    this.rule = rule;
    if (!meta) {
      throw new Error('Meta is undefined');
    }
    this.meta = meta;
    this.next = next;
  }

  get id(): string {
    if (this.#id === undefined) {
      const { stackId, pathId, stepId } = this.meta;
      this.#id = `${stackId},${pathId},${stepId}`;
    }
    return this.#id;
  }

  print(opts: PrintOpts): string {
    return printGraphNode(this)(opts);
  }
}
