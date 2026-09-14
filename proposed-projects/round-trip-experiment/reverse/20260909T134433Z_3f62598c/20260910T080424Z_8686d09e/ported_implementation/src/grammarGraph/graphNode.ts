import { noColor } from './colorize.js';
import { printGraphNode } from './print.js';
import type { PrintOpts } from './print.js';
import type { UnresolvedRule } from './types.js';

export interface GraphNodeMeta {
  stackId: number;
  pathId: number;
  stepId: number;
}

export class GraphNode {
  rule: UnresolvedRule;
  meta: GraphNodeMeta;
  next?: GraphNode;
  private _id?: string;

  constructor(rule: UnresolvedRule, meta: GraphNodeMeta, next?: GraphNode) {
    this.rule = rule;
    if (!meta) {
      throw new Error('Meta is undefined');
    }
    this.meta = meta;
    this.next = next;
  }

  get id(): string {
    if (!this._id) {
      this._id = `${this.meta.stackId},${this.meta.pathId},${this.meta.stepId}`;
    }
    return this._id;
  }

  print(opts: PrintOpts = {}): string {
    return printGraphNode(this, opts);
  }

  toString(): string {
    return this.print({ showPosition: false, colorize: noColor });
  }
}
