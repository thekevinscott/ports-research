import { colorize } from './colorize.js';
import { printGraphNode, type PrintNodeOpts } from './print.js';
import type { UnresolvedRule } from './type-guards.js';

export interface GraphNodeMeta {
  stackId: number;
  pathId: number;
  stepId: number;
}

export class GraphNode {
  public readonly rule: UnresolvedRule;
  public readonly meta: GraphNodeMeta;
  public readonly next: GraphNode | undefined;
  public readonly print: (opts: PrintNodeOpts) => string;

  private _id: string | undefined = undefined;

  constructor(rule: UnresolvedRule, meta: GraphNodeMeta, next?: GraphNode) {
    this.rule = rule;
    if (!meta) {
      throw new Error('Meta is undefined');
    }
    this.meta = meta;
    this.next = next;
    this.print = printGraphNode(this);
  }

  get id(): string {
    if (!this._id) {
      this._id = `${this.meta.stackId},${this.meta.pathId},${this.meta.stepId}`;
    }
    return this._id;
  }

  toString(): string {
    return this.print({ colorize, showPosition: false });
  }
}
