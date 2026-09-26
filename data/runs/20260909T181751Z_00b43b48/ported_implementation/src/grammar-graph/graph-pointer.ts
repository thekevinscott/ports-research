import type { PrintOpts, ResolvedGraphPointer, UnresolvedRule } from './grammar-graph-types.js';
import type { GraphNode } from './graph-node.js';
import { printGraphPointer } from './print.js';
import {
  isGraphPointerRuleChar,
  isGraphPointerRuleCharExclude,
  isGraphPointerRuleEnd,
  isGraphPointerRuleRef,
  isRuleEnd,
} from './type-guards.js';

export type GraphPointerKey = string;

export class GraphPointer<T extends UnresolvedRule = UnresolvedRule> {
  node: GraphNode<T>;
  parent: GraphPointer | undefined;
  id: GraphPointerKey;
  valid: boolean | undefined = undefined;

  constructor(node: GraphNode<T>, parent?: GraphPointer) {
    if (node === undefined) {
      throw new Error('Node is undefined');
    }
    this.node = node;
    this.parent = parent;
    this.id = parent ? `${parent.id}-${node.id}` : node.id;
  }

  get rule(): T {
    return this.node.rule;
  }

  print(opts: PrintOpts): string {
    return printGraphPointer(this)(opts);
  }

  /**
   * Resolve the graph pointer, yielding pointers to concrete (non-reference) rules.
   *
   * @param resolved whether the pointer has already been resolved
   */
  *resolve(resolved = false): IterableIterator<ResolvedGraphPointer> {
    const pointer: GraphPointer = this;
    if (isGraphPointerRuleRef(pointer)) {
      if (resolved) {
        if (!pointer.node.next) {
          throw new Error(`No next node: ${pointer.node.id}`);
        }
        yield* new GraphPointer(pointer.node.next, pointer.parent).resolve();
      } else {
        for (const node of pointer.rule.nodes) {
          yield* new GraphPointer(node, pointer).resolve();
        }
      }
    } else if (isGraphPointerRuleEnd(pointer)) {
      if (!pointer.parent) {
        yield pointer;
      } else {
        yield* pointer.parent.resolve(true);
      }
    } else if (isGraphPointerRuleChar(pointer) || isGraphPointerRuleCharExclude(pointer)) {
      yield pointer;
    } else {
      throw new Error(`Unknown rule: ${JSON.stringify(pointer.node.rule)}`);
    }
  }

  /**
   * Fetch the next resolved graph pointers.
   */
  *fetchNext(): IterableIterator<ResolvedGraphPointer> {
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
        throw new Error(`No next node: ${this.node.id}`);
      }
      const pointer = new GraphPointer(this.node.next, this.parent);
      yield* pointer.resolve();
    }
  }
}
