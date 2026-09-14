import { colorize, Colorize } from './colorize';
import { printGraphNode } from './print';
import type { GraphPointer } from './graph-pointer';
import type { RuleRef } from './rule-ref';
import type { Rule } from './types';

export type UnresolvedRule = Rule | RuleRef;

export class GraphNodeMeta {
  constructor(
    public stackId: number,
    public pathId: number,
    public stepId: number,
  ) {}
}

export class GraphNode {
  public rule: UnresolvedRule;
  public meta: GraphNodeMeta;
  public next?: GraphNode;
  private _id?: string;

  constructor(rule: UnresolvedRule, meta: GraphNodeMeta, next?: GraphNode) {
    this.rule = rule;
    if (meta === undefined || meta === null) {
      throw new Error('Meta is undefined');
    }
    this.meta = meta;
    this.next = next;
  }

  get id(): string {
    if (this._id === undefined) {
      this._id = `${this.meta.stackId},${this.meta.pathId},${this.meta.stepId}`;
    }
    return this._id;
  }

  print({
    colorize: col = colorize,
    pointers,
    showPosition = false,
  }: {
    colorize?: Colorize;
    pointers?: Iterable<GraphPointer>;
    showPosition?: boolean;
  } = {}): string {
    return printGraphNode(this, col, { pointers, showPosition });
  }

  toString(): string {
    return this.print({ colorize: (v) => `${v}`, showPosition: true });
  }
}
