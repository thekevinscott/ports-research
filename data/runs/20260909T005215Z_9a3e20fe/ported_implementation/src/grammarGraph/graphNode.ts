import type { PrintOpts, UnresolvedRule } from './grammarGraphTypes.ts';
import { printGraphNode } from './print.ts';
import type { RuleRef } from './ruleRef.ts';

export interface GraphNodeMeta {
  stackId: number;
  pathId: number;
  stepId: number;
}

export class GraphNode<T extends UnresolvedRule = UnresolvedRule> {
  rule: T;
  next: GraphNode | null;
  meta: GraphNodeMeta;
  #id: string | null = null;

  constructor(rule: T, meta: GraphNodeMeta | null, nextNode: GraphNode | null = null) {
    this.rule = rule;
    if (meta === null || meta === undefined) {
      throw new Error('Meta is undefined');
    }
    this.meta = meta;
    this.next = nextNode;
  }

  /** Cached on first read, exactly like the reference implementation. */
  get id(): string {
    if (this.#id === null) {
      this.#id = `${this.meta.stackId},${this.meta.pathId},${this.meta.stepId}`;
    }
    return this.#id;
  }

  print(opts: PrintOpts): string {
    return printGraphNode(this)(opts);
  }
}

export type GraphNodeRuleRef = GraphNode<RuleRef>;
