import type { PrintOpts, ResolvedRule, UnresolvedRule } from './grammarGraphTypes.js';
import type { GraphNode } from './graphNode.js';
import { printGraphPointer } from './print.js';
import {
  isGraphPointerRuleChar,
  isGraphPointerRuleCharExclude,
  isGraphPointerRuleEnd,
  isGraphPointerRuleRef,
  isRuleEnd,
} from './typeGuards.js';

export type GraphPointerKey = string;

export class GraphPointer<T extends UnresolvedRule = UnresolvedRule> {
  node: GraphNode<T>;
  parent: GraphPointer | null;
  id: GraphPointerKey;
  #valid: boolean | null = null;

  constructor(node: GraphNode<T>, parent: GraphPointer | null = null) {
    if (!node) {
      throw new Error('Node is undefined');
    }
    this.node = node;
    this.parent = parent;
    this.id = parent ? `${parent.id}-${node.id}` : node.id;
  }

  get rule(): T {
    return this.node.rule;
  }

  get valid(): boolean | null {
    return this.#valid;
  }

  set valid(valid: boolean) {
    this.#valid = valid;
  }

  print(opts: PrintOpts): string {
    return printGraphPointer(this)(opts);
  }

  /**
   * Resolve the graph pointer, yielding pointers that sit on a concrete (non-reference) rule.
   *
   * @param resolved whether the pointer has already been resolved.
   */
  *resolve(resolved = false): Generator<GraphPointer<ResolvedRule>> {
    if (isGraphPointerRuleRef(this)) {
      if (resolved) {
        if (!this.node.next) {
          throw new Error(`No next node: ${this.node}`);
        }
        yield* new GraphPointer(this.node.next, this.parent).resolve();
      } else {
        for (const node of this.node.rule.nodes) {
          yield* new GraphPointer(node, this).resolve();
        }
      }
    } else if (isGraphPointerRuleEnd(this)) {
      if (!this.parent) {
        yield this;
      } else {
        yield* this.parent.resolve(true);
      }
    } else if (isGraphPointerRuleChar(this) || isGraphPointerRuleCharExclude(this)) {
      yield this;
    } else {
      throw new Error(`Unknown rule: ${this.node.rule}`);
    }
  }

  /**
   * Fetch the next resolved graph pointers.
   */
  *fetchNext(): Generator<GraphPointer<ResolvedRule>> {
    // If this pointer is invalid, then we don't return any new pointers
    if (!this.valid) {
      return;
    }

    // If this pointer is an end node, we return the parent's next node.
    // If no parent exists, we return nothing, since it's the end of the line.
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

  toString(): string {
    return `<GraphPointer ${this.id} ${this.node}>`;
  }
}
