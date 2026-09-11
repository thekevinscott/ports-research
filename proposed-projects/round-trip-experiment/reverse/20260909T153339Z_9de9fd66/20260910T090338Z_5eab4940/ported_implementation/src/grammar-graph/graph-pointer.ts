import { colorize, type Colorize } from './colorize.js';
import type { GraphNode } from './graph-node.js';
import { printGraphPointer } from './print.js';
import {
  isRuleChar,
  isRuleCharExcluded,
  isRuleEnd,
  isRuleRef,
} from './type-guards.js';
import type { UnresolvedRule } from './types.js';

export class GraphPointer {
  id: string;
  private _valid?: boolean;

  constructor(
    public node: GraphNode,
    public parent?: GraphPointer
  ) {
    if (!node) {
      throw new Error('Node is undefined');
    }
    this.id = parent ? `${parent.id}-${node.id}` : node.id;
  }

  /**
   * 1. If the current node is an end node, and the pointer has a parent, return the
   *    parent's `fetchNext`; else return nothing.
   * 2. If the current node is a rule ref, yield the referenced nodes, _unless_ resolved
   *    is true, in which case it returns next.
   * 3. If the current node is a char or range, we go to the next node. If none exists,
   *    throw an error.
   */
  *resolve(resolved = false): IterableIterator<GraphPointer> {
    const rule = this.node.rule;
    if (isRuleRef(rule)) {
      if (resolved) {
        if (!this.node.next) {
          throw new Error(`No next node: ${this.node}`);
        }
        yield* new GraphPointer(this.node.next, this.parent).resolve();
      } else {
        for (const node of rule.nodes) {
          yield* new GraphPointer(node, this).resolve();
        }
      }
    } else if (isRuleEnd(rule)) {
      if (!this.parent) {
        yield this;
      } else {
        yield* this.parent.resolve(true);
      }
    } else if (isRuleChar(rule) || isRuleCharExcluded(rule)) {
      yield this;
    } else {
      throw new Error(`Unknown rule: ${this.node.rule}`);
    }
  }

  *fetchNext(): IterableIterator<GraphPointer> {
    // if this pointer is invalid, then we don't return any new pointers
    if (this._valid === false) {
      return;
    }

    // if this pointer is an end node, we return the parent's next node. If no parent
    // exists, we return nothing, since it's the end of the line.
    if (isRuleEnd(this.node.rule)) {
      if (this.parent) {
        yield* this.parent.fetchNext();
      }
    } else {
      if (!this.node.next) {
        throw new Error(`No next node: ${this.node}`);
      }
      const pointer = new GraphPointer(this.node.next, this.parent);
      yield* pointer.resolve();
    }
  }

  get rule(): UnresolvedRule {
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
