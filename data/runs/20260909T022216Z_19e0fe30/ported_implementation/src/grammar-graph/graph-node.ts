import type { PrintOpts, UnresolvedRule } from './grammar-graph-types.js';
import { printGraphNode } from './print.js';
import type { RuleRef } from './rule-ref.js';

export interface GraphNodeMeta {
  stackId: number;
  pathId: number;
  stepId: number;
}

export class GraphNode<T extends UnresolvedRule = UnresolvedRule> {
  rule: T;
  next: GraphNode | undefined;
  meta: GraphNodeMeta;
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
      const { stackId, pathId, stepId } = this.meta;
      this.#id = `${stackId},${pathId},${stepId}`;
    }
    return this.#id;
  }

  print(opts: PrintOpts): string {
    return printGraphNode(this)(opts);
  }
}

export type GraphNodeRuleRef = GraphNode<RuleRef>;
