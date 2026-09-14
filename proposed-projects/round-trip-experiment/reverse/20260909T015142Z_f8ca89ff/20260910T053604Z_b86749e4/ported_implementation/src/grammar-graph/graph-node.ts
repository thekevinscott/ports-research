import { colorize } from './colorize';
import { printGraphNode, PrintOpts } from './print';
import type { UnresolvedRule } from './types';

export interface GraphNodeMeta {
  stackId: number;
  pathId: number;
  stepId: number;
}

export class GraphNode {
  public rule: UnresolvedRule;
  public meta: GraphNodeMeta;
  public next?: GraphNode;
  private _id?: string;

  constructor(rule: UnresolvedRule, meta: GraphNodeMeta, next?: GraphNode) {
    this.rule = rule;
    if (meta === undefined) {
      throw new Error('Meta is undefined');
    }
    this.meta = meta;
    this.next = next;
  }

  public get id(): string {
    if (!this._id) {
      const { stackId, pathId, stepId } = this.meta;
      this._id = `${stackId},${pathId},${stepId}`;
    }
    return this._id;
  }

  public print(opts: PrintOpts = {}): string {
    return printGraphNode(this)({ colorize, ...opts });
  }
}
