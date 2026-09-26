import type {
  PrintOpts,
  ResolvedGraphPointer,
  ResolvedRule,
  UnresolvedRule,
} from './grammar-graph-types';
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
  parent?: GraphPointer;
  id: GraphPointerKey;
  #valid?: boolean;

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

  get valid(): boolean | undefined {
    return this.#valid;
  }

  set valid(valid: boolean | undefined) {
    this.#valid = valid;
  }

  print(opts: PrintOpts): string {
    return printGraphPointer(this as GraphPointer)(opts);
  }

  /**
   * Resolve this pointer into pointers that point at concrete (non-reference) rules.
   *
   * @param resolved whether the pointer has already been resolved
   */
  *resolve(resolved = false): Generator<ResolvedGraphPointer> {
    const pointer = this as GraphPointer;
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
        yield pointer as GraphPointer<ResolvedRule>;
      } else {
        yield* pointer.parent.resolve(true);
      }
    } else if (isGraphPointerRuleChar(pointer) || isGraphPointerRuleCharExclude(pointer)) {
      yield pointer as GraphPointer<ResolvedRule>;
    } else {
      throw new Error(`Unknown rule: ${pointer.node.rule}`);
    }
  }

  /**
   * Fetch the pointers that follow this one, if this pointer was valid.
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
