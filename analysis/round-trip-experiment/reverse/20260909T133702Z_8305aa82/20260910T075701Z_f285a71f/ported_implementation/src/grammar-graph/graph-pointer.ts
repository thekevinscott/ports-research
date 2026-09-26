import { colorize, Colorize } from './colorize.js';
import type { GraphNode } from './graph-node.js';
import { printGraphPointer } from './print.js';
import {
  isGraphPointerRuleChar,
  isGraphPointerRuleCharExclude,
  isGraphPointerRuleEnd,
  isGraphPointerRuleRef,
  isRuleEnd,
  isRuleRef,
  type Rule,
} from './type-guards.js';

export class GraphPointer {
  public node: GraphNode;
  public parent?: GraphPointer;
  public id: string;
  private _valid?: boolean;

  constructor(node: GraphNode, parent?: GraphPointer) {
    if (node === undefined || node === null) {
      throw new Error('Node is undefined');
    }
    this.node = node;
    this.parent = parent;
    this.id = parent !== undefined ? `${parent.id}-${node.id}` : node.id;
  }

  /**
   * 1. If the current node is an end node, and the pointer has a parent, return the parent's `fetchNext`; else return nothing.
   * 2. If the current node is a rule ref, yield the referenced nodes, _unless_ resolved is true, in which case it returns next.
   * 3. If the current node is a char or range, we go to the next node. If none exists, throw an error.
   */
  *resolve(resolved = false): Generator<GraphPointer> {
    if (isGraphPointerRuleRef(this)) {
      if (resolved) {
        if (this.node.next === undefined) {
          throw new Error(`No next node: ${this.node}`);
        }
        yield* new GraphPointer(this.node.next, this.parent).resolve();
      } else {
        if (!isRuleRef(this.node.rule)) {
          throw new Error(`Expected a rule ref: ${this.node.rule}`);
        }
        for (const node of this.node.rule.nodes) {
          yield* new GraphPointer(node, this).resolve();
        }
      }
    } else if (isGraphPointerRuleEnd(this)) {
      if (this.parent === undefined) {
        yield this;
      } else {
        yield* this.parent.resolve(true);
      }
    } else if (
      isGraphPointerRuleChar(this) ||
      isGraphPointerRuleCharExclude(this)
    ) {
      yield this;
    } else {
      throw new Error(`Unknown rule: ${this.node.rule}`);
    }
  }

  *fetchNext(): Generator<GraphPointer> {
    // if this pointer is invalid, then we don't return any new pointers
    if (this._valid === false) {
      return;
    }

    // if this pointer is an end node, we return the parent's next node. If no parent exists,
    // we return nothing, since it's the end of the line.
    if (isRuleEnd(this.node.rule)) {
      if (this.parent !== undefined) {
        yield* this.parent.fetchNext();
      }
    } else {
      if (this.node.next === undefined) {
        throw new Error(`No next node: ${this.node}`);
      }
      const pointer = new GraphPointer(this.node.next, this.parent);
      yield* pointer.resolve();
    }
  }

  get rule(): Rule {
    return this.node.rule;
  }

  get valid(): boolean | undefined {
    return this._valid;
  }

  set valid(valid: boolean | undefined) {
    this._valid = valid;
  }

  print(col: Colorize = colorize): string {
    return printGraphPointer(this, col);
  }

  toString(): string {
    return this.print((s) => `${s}`);
  }
}
