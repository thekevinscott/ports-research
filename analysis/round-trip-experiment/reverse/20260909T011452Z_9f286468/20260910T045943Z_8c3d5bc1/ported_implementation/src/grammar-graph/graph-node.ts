import { Colorize, colorize as defaultColorize } from './colorize';
import { printGraphNode } from './print';
import type { GraphPointer } from './graph-pointer';
import type { UnresolvedRule } from './type-guards';

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

  get id(): string {
    if (!this._id) {
      const { stackId, pathId, stepId } = this.meta;
      this._id = `${stackId},${pathId},${stepId}`;
    }
    return this._id;
  }

  print({
    pointers,
    showPosition = false,
    colorize = defaultColorize,
  }: {
    pointers?: Iterable<GraphPointer>;
    showPosition?: boolean;
    colorize?: Colorize;
  } = {}): string {
    return printGraphNode(this, { pointers, showPosition, colorize });
  }
}
