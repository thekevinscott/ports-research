import type { PrintOpts, UnresolvedRule } from './grammar-graph-types';
import { printGraphNode } from './print';
import type { RuleRef } from './rule-ref';

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

  constructor(rule: T, meta?: GraphNodeMeta, nextNode?: GraphNode) {
    if (!rule) {
      throw new Error('Rule is undefined');
    }
    this.rule = rule;
    if (!meta) {
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

export type GraphNodeRuleRef = GraphNode<RuleRef>;
