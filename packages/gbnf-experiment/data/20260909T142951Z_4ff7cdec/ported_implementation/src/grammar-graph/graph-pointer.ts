import type {
  PrintOpts,
  ResolvedRule,
  UnresolvedRule,
} from './grammar-graph-types.ts';
import type { GraphNode } from './graph-node.ts';
import { printGraphPointer } from './print.ts';
import {
  isGraphPointerRuleChar,
  isGraphPointerRuleCharExclude,
  isGraphPointerRuleEnd,
  isGraphPointerRuleRef,
  isRuleEnd,
} from './type-guards.ts';

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
   * Resolve this pointer into pointers that point at concrete (non-reference) rules.
   */
  *resolve(resolved = false): Generator<GraphPointer<ResolvedRule>> {
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
    } else if (
      isGraphPointerRuleChar(pointer) ||
      isGraphPointerRuleCharExclude(pointer)
    ) {
      yield pointer;
    } else {
      throw new Error(`Unknown rule: ${JSON.stringify(pointer.node.rule)}`);
    }
  }

  /**
   * Fetch the next pointers, unresolved.
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
