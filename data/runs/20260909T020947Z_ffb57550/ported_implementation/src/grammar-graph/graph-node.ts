import type { PrintOpts, UnresolvedRule } from './grammar-graph-types.js';
import { printGraphNode } from './print.js';

export interface GraphNodeMeta {
  stackId: number;
  pathId: number;
  stepId: number;
}

export class GraphNode<T extends UnresolvedRule = UnresolvedRule> {
  // `rule` is readonly so that `GraphNode` stays covariant in `T`; a mutable
  // property would make narrowed nodes unassignable to `GraphNode`.
  readonly rule: T;
  readonly next: GraphNode | undefined;
  readonly meta: GraphNodeMeta;
  #id: string | undefined = undefined;

  constructor(
    rule: T,
    meta: GraphNodeMeta | undefined,
    nextNode?: GraphNode | undefined,
  ) {
    this.rule = rule;
    if (meta === undefined) {
      throw new Error('Meta is undefined');
    }
    this.meta = meta;
    this.next = nextNode;
  }

  get id(): string {
    if (this.#id === undefined) {
      this.#id = `${this.meta.stackId},${this.meta.pathId},${this.meta.stepId}`;
    }
    return this.#id;
  }

  print(opts: PrintOpts): string {
    return printGraphNode(this)(opts);
  }
}
