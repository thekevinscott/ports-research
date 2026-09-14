import { InputParseError } from "../utils/errors/input-parse-error.ts";
import { isPointInRange } from "../utils/is-point-in-range.ts";
import { colorize } from "./colorize.ts";
import { getInputAsCodePoints } from "./get-input-as-code-points.ts";
import { getSerializedRuleKey } from "./get-serialized-rule-key.ts";
import type {
  ResolvedGraphPointer,
  RuleCharValue,
  UnresolvedRule,
  ValidInput,
} from "./grammar-graph-types.ts";
import { GraphNode } from "./graph-node.ts";
import { GraphPointer } from "./graph-pointer.ts";
import { Pointers } from "./pointers.ts";
import type { RuleRef } from "./rule-ref.ts";
import {
  isRange,
  isRuleChar,
  isRuleCharExclude,
  isRuleEnd,
  isRuleRef,
} from "./type-guards.ts";

export type RootNode = Map<number, GraphNode>;

/** Does `codePoint` match any of a char rule's code points or ranges? */
const matchesCodePoint = (value: RuleCharValue, codePoint: number): boolean =>
  value.some((possibleCodePoint) =>
    isRange(possibleCodePoint)
      ? isPointInRange(codePoint, possibleCodePoint)
      : codePoint === possibleCodePoint,
  );

export class Graph {
  #roots = new Map<number, RootNode>();
  #rootNode: RootNode | null = null;
  grammar: string;
  previousCodePoints: number[] = [];

  constructor(grammar: string, stackedRules: UnresolvedRule[][][], rootId: number) {
    this.grammar = grammar;
    const ruleRefs: RuleRef[] = [];
    const uniqueRules = new Map<string, UnresolvedRule>();

    for (let stackId = 0; stackId < stackedRules.length; stackId++) {
      const stack = stackedRules[stackId];
      const nodes: RootNode = new Map<number, GraphNode>();
      for (let pathId = 0; pathId < stack.length; pathId++) {
        const path = stack[pathId];
        let node: GraphNode | null = null;
        for (let stepId = path.length - 1; stepId >= 0; stepId--) {
          const nextNode: GraphNode | null = node;
          const rule = stack[pathId][stepId];
          uniqueRules.set(getSerializedRuleKey(rule), rule);
          if (isRuleRef(rule)) {
            ruleRefs.push(rule);
          }
          // rules coming in may be identical but have different references.
          // here, we ensure we always use the same reference for an identical rule.
          // this makes future comparisons easier.
          const uniqueRule = uniqueRules.get(getSerializedRuleKey(rule));
          if (uniqueRule === undefined) {
            throw new Error("Could not get unique rule");
          }
          node = new GraphNode(uniqueRule, { stackId, pathId, stepId }, nextNode);
        }

        if (node === null) {
          throw new Error("Could not get node");
        }
        nodes.set(pathId, node);
      }
      this.#roots.set(stackId, nodes);
    }

    const rootNode = this.#roots.get(rootId);
    if (rootNode === undefined) {
      throw new Error(`Root node not found for value: ${rootId}`);
    }
    this.#rootNode = rootNode;

    for (const ruleRef of ruleRefs) {
      ruleRef.nodes = new Set(this.getRootNode(ruleRef.value).values());
    }
  }

  get roots(): Map<number, RootNode> {
    return this.#roots;
  }

  get rootNode(): RootNode | null {
    return this.#rootNode;
  }

  getRootNode(value: number): RootNode {
    const rootNode = this.#roots.get(value);
    if (rootNode === undefined) {
      throw new Error(`Root node not found for value: ${value}`);
    }
    return rootNode;
  }

  getInitialPointers(): Pointers {
    const pointers = new Pointers();

    const rootNode = this.#rootNode;
    if (rootNode === null) {
      throw new Error("Root node is not defined");
    }

    for (const [node, parent] of this.fetchNodesForRootNode(rootNode)) {
      const pointer = new GraphPointer(node, parent);
      for (const resolvedPointer of this.resolvePointer(pointer)) {
        pointers.add(resolvedPointer);
      }
    }
    return pointers;
  }

  setValid(pointers: GraphPointer[], valid: boolean): void {
    for (const pointer of pointers) {
      pointer.valid = valid;
    }
  }

  parse(currentPointers: Pointers, codePoint: number): Pointers {
    for (const [rule, graphPointers] of this.iterateOverPointers(currentPointers)) {
      if (isRuleChar(rule)) {
        this.setValid(graphPointers, matchesCodePoint(rule.value, codePoint));
      } else if (isRuleCharExclude(rule)) {
        this.setValid(graphPointers, !matchesCodePoint(rule.value, codePoint));
      } else if (!isRuleEnd(rule)) {
        throw new Error(`Unsupported rule: ${rule}`);
      }
    }

    // a pointer's id is the sum of its node's id and its parent's id chain.
    // if two pointers share the same id, it means they point to the same node and have
    // identical parent chains. for the purposes of walking the graph, we only need to
    // keep one of them.
    const nextPointers = new Pointers();
    for (const currentPointer of currentPointers) {
      for (const unresolvedNextPointer of currentPointer.fetchNext()) {
        for (const resolvedNextPointer of this.resolvePointer(unresolvedNextPointer)) {
          nextPointers.add(resolvedNextPointer);
        }
      }
    }
    return nextPointers;
  }

  *resolvePointer(unresolvedPointer: GraphPointer): Generator<ResolvedGraphPointer> {
    for (const resolvedPointer of unresolvedPointer.resolve()) {
      if (isRuleRef(resolvedPointer.node.rule)) {
        throw new Error("Encountered a reference rule when building pointers to the graph");
      }
      if (isRuleEnd(resolvedPointer.node.rule) && resolvedPointer.parent !== null) {
        throw new Error(
          "Encountered an ending rule with a parent when building pointers to the graph",
        );
      }
      yield resolvedPointer as ResolvedGraphPointer;
    }
  }

  add(src: ValidInput, pointers?: Pointers | null): Pointers {
    if (typeof src !== "string") {
      throw new Error("src must be a string in graph.add");
    }
    // matches the reference implementation, where an empty `Pointers` is falsy and so
    // falls back to the initial pointers.
    let currentPointers =
      pointers && pointers.size > 0 ? pointers : this.getInitialPointers();

    const codePoints = getInputAsCodePoints(src);
    for (const codePoint of codePoints) {
      if (!Number.isInteger(codePoint)) {
        throw new Error("code_point must be an integer!");
      }
    }

    for (let codePointPos = 0; codePointPos < codePoints.length; codePointPos++) {
      const codePoint = codePoints[codePointPos];
      currentPointers = this.parse(currentPointers, codePoint);
      if (currentPointers.size === 0) {
        throw new InputParseError(codePoints, codePointPos, this.previousCodePoints);
      }
    }
    this.previousCodePoints.push(...codePoints);
    return currentPointers;
  }

  /**
   * Generator that yields either the node, or if a reference rule, the referenced node.
   *
   * We need this function, as distinct from leveraging the logic in GraphPointer,
   * because that needs a rule ref with already defined nodes; this function is used to
   * _set_ those nodes.
   */
  *fetchNodesForRootNode(
    rootNodes: RootNode,
    parent: GraphPointer | null = null,
  ): Generator<[GraphNode, GraphPointer | null]> {
    for (const node of rootNodes.values()) {
      if (isRuleRef(node.rule)) {
        yield* this.fetchNodesForRootNode(
          this.getRootNode(node.rule.value),
          new GraphPointer(node, parent),
        );
      } else {
        yield [node, parent];
      }
    }
  }

  print(pointers?: Pointers | null, colors = false): string {
    const nodes: GraphNode[][] = [...this.#roots.values()].map((rootNode) => [
      ...rootNode.values(),
    ]);
    const printPointers = pointers ?? new Pointers();
    const graphView: string[] = [];
    for (const rootNode of nodes) {
      for (const node of rootNode) {
        graphView.push(
          node.print({
            pointers: printPointers,
            showPosition: true,
            colorize: colors ? colorize : (s: string | number) => `${s}`,
          }),
        );
      }
    }

    return graphView.join("\n");
  }

  *iterateOverPointers(
    pointers: Pointers,
  ): Generator<[UnresolvedRule, GraphPointer[]]> {
    const seenRules = new Map<UnresolvedRule, GraphPointer[]>();
    for (const pointer of pointers) {
      const rule = pointer.rule;
      if (isRuleRef(rule)) {
        throw new Error("Encountered a reference rule in the graph");
      }

      let seenRule = seenRules.get(rule);
      if (seenRule === undefined) {
        seenRule = [pointer];
        seenRules.set(rule, seenRule);
      }
      seenRule.push(pointer);
    }

    yield* seenRules.entries();
  }
}
