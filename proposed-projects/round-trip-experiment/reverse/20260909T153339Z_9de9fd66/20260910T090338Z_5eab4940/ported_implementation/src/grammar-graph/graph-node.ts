import { colorize, type Colorize } from './colorize.js';
import type { GenericSet } from './generic-set.js';
import type { GraphPointer } from './graph-pointer.js';
import { printGraphNode } from './print.js';
import type { UnresolvedRule } from './types.js';

export type GraphNodeMeta = {
  stackId: number;
  pathId: number;
  stepId: number;
};

export class GraphNode {
  private _id?: string;

  constructor(
    public rule: UnresolvedRule,
    public meta: GraphNodeMeta,
    public next?: GraphNode
  ) {
    if (!meta) {
      throw new Error('Meta is undefined');
    }
  }

  get id(): string {
    if (!this._id) {
      this._id = `${this.meta.stackId},${this.meta.pathId},${this.meta.stepId}`;
    }
    return this._id;
  }

  print({
    pointers,
    showPosition = false,
    colorize: col = colorize,
  }: {
    pointers?: GenericSet<GraphPointer, string>;
    showPosition?: boolean;
    colorize?: Colorize;
  } = {}): string {
    return printGraphNode(this, { pointers, showPosition, colorize: col });
  }

  toString(): string {
    return this.print({ showPosition: false, colorize: (s) => `${s}` });
  }
}
