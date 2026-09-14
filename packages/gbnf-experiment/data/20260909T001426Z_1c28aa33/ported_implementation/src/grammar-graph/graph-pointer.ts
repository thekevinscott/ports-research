import type { PrintOpts, UnresolvedRule } from './grammar-graph-types';
import type { GraphNode } from './graph-node';
import { printGraphPointer } from './print';
import {
  isGraphPointerRuleChar,
  isGraphPointerRuleCharExclude,
  isGraphPointerRuleEnd,
  isGraphPointerRuleRef,
  isRuleEnd,
} from './type-guards';

export type GraphPointerKey = string;

export class GraphPointer<T extends UnresolvedRule = UnresolvedRule> {
  node: GraphNode<T>;
  parent: GraphPointer | undefined;
  id: string;
  #valid: boolean | undefined = undefined;

  constructor(node: GraphNode<T>, parent?: GraphPointer) {
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

  get valid(): boolean | undefined {
    return this.#valid;
  }

  set valid(valid: boolean) {
    this.#valid = valid;
  }

  print(opts: PrintOpts): string {
    return printGraphPointer(this)(opts);
  }

  /**
   * Resolve the graph pointer.
   *
   * @param resolved Whether the pointer has already been resolved.
   * @yields the resolved graph pointers.
   */
  *resolve(resolved = false): Generator<GraphPointer> {
    const self = this as GraphPointer;
    if (isGraphPointerRuleRef(self)) {
      if (resolved) {
        if (!self.node.next) {
          throw new Error(`No next node: ${self.node.id}`);
        }
        yield* new GraphPointer(self.node.next, self.parent).resolve();
      } else {
        for (const node of self.node.rule.nodes) {
          yield* new GraphPointer(node, self).resolve();
        }
      }
    } else if (isGraphPointerRuleEnd(self)) {
      if (!self.parent) {
        yield self;
      } else {
        yield* self.parent.resolve(true);
      }
    } else if (
      isGraphPointerRuleChar(self) ||
      isGraphPointerRuleCharExclude(self)
    ) {
      yield self;
    } else {
      throw new Error(`Unknown rule: ${self.node.rule}`);
    }
  }

  /**
   * Fetch the next resolved graph pointers.
   */
  *fetchNext(): Generator<GraphPointer> {
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
