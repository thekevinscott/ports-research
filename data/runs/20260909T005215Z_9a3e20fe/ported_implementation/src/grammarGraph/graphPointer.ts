import { repr } from '../utils/repr.ts';
import type { PrintOpts, ResolvedGraphPointer, UnresolvedRule } from './grammarGraphTypes.ts';
import type { GraphNode } from './graphNode.ts';
import { printGraphPointer } from './print.ts';
import {
  isGraphPointerRuleChar,
  isGraphPointerRuleCharExclude,
  isGraphPointerRuleEnd,
  isGraphPointerRuleRef,
  isRuleEnd,
} from './typeGuards.ts';

export type GraphPointerKey = string;

export class GraphPointer<T extends UnresolvedRule = UnresolvedRule> {
  node: GraphNode<T>;
  parent: GraphPointer | null;
  id: string;
  #valid: boolean | null = null;

  constructor(node: GraphNode<T>, parent: GraphPointer | null = null) {
    if (node === null || node === undefined) {
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
   * Walk this pointer down to the concrete (char / char-exclude / terminal end)
   * pointers it stands for.
   *
   * @param resolved whether the pointer has already been resolved.
   */
  *resolve(resolved = false): Generator<ResolvedGraphPointer> {
    const self = this as GraphPointer;
    if (isGraphPointerRuleRef(self)) {
      if (resolved) {
        if (!self.node.next) {
          throw new Error(`No next node: ${repr(self.node.rule)}`);
        }
        yield* new GraphPointer(self.node.next, self.parent).resolve();
      } else {
        for (const node of self.node.rule.nodes) {
          yield* new GraphPointer(node, self).resolve();
        }
      }
    } else if (isGraphPointerRuleEnd(self)) {
      if (!this.parent) {
        yield this as ResolvedGraphPointer;
      } else {
        yield* this.parent.resolve(true);
      }
    } else if (isGraphPointerRuleChar(self) || isGraphPointerRuleCharExclude(self)) {
      yield this as ResolvedGraphPointer;
    } else {
      throw new Error(`Unknown rule: ${repr(this.node.rule)}`);
    }
  }

  /** Yields the next resolved graph pointers that follow this one. */
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
        throw new Error(`No next node: ${repr(this.node.rule)}`);
      }
      const pointer = new GraphPointer(this.node.next, this.parent);
      yield* pointer.resolve();
    }
  }
}
