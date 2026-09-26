import { type Colorize, colorize as defaultColorize } from './colorize.ts';
import type { GraphPointer } from './graph-pointer.ts';
import { printGraphNode } from './print.ts';
import type { UnresolvedRule } from './types.ts';

export interface GraphNodeMeta {
  stackId: number;
  pathId: number;
  stepId: number;
}

/** Compared by identity. */
export class GraphNode {
  rule: UnresolvedRule;
  next: GraphNode | undefined;
  meta: GraphNodeMeta;
  #id: string | undefined = undefined;

  constructor(rule: UnresolvedRule, meta: GraphNodeMeta, next?: GraphNode) {
    this.rule = rule;
    if (meta === undefined) {
      throw new Error('Meta is undefined');
    }
    this.meta = meta;
    this.next = next;
  }

  get id(): string {
    if (!this.#id) {
      const { stackId, pathId, stepId } = this.meta;
      this.#id = `${stackId},${pathId},${stepId}`;
    }
    return this.#id;
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

  toString(): string {
    return this.print({ colorize: defaultColorize, showPosition: false });
  }
}
