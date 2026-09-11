import { colorize, type Colorize } from './colorize.js';
import { printGraphNode } from './print.js';
import type { GraphRule } from './typeGuards.js';
import type { GraphPointer } from './graphPointer.js';

export class GraphNodeMeta {
  public readonly stackId: number;
  public readonly pathId: number;
  public readonly stepId: number;

  public constructor(stackId: number, pathId: number, stepId: number) {
    this.stackId = stackId;
    this.pathId = pathId;
    this.stepId = stepId;
  }
}

export class GraphNode {
  public readonly rule: GraphRule;
  public readonly meta: GraphNodeMeta;
  public readonly next: GraphNode | undefined;
  private innerId: string | undefined;

  public constructor(
    rule: GraphRule,
    meta: GraphNodeMeta,
    next?: GraphNode | undefined
  ) {
    this.rule = rule;
    if (meta === undefined || meta === null) {
      throw new Error('Meta is undefined');
    }
    this.meta = meta;
    this.next = next;
  }

  public get id(): string {
    if (!this.innerId) {
      this.innerId = `${this.meta.stackId},${this.meta.pathId},${this.meta.stepId}`;
    }
    return this.innerId;
  }

  public print({
    pointers,
    showPosition = false,
    colorize: col = colorize,
  }: {
    pointers?: Iterable<GraphPointer>;
    showPosition?: boolean;
    colorize?: Colorize;
  } = {}): string {
    return printGraphNode(this, { pointers, showPosition, colorize: col });
  }
}
