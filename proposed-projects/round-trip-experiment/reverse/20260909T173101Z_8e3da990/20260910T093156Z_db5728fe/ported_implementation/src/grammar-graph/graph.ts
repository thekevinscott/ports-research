import { InputParseError } from '../utils/errors/input-parse-error.js';
import { isPointInRange } from '../utils/is-point-in-range.js';
import { colorize, noColorize } from './colorize.js';
import { GenericSet } from './generic-set.js';
import { getInputAsCodePoints } from './get-input-as-code-points.js';
import { getSerializedRuleKey } from './get-serialized-rule-key.js';
import { GraphNode } from './graph-node.js';
import { GraphPointer } from './graph-pointer.js';
import type { RuleRef } from './rule-ref.js';
import {
  isRange,
  isRuleChar,
  isRuleCharExcluded,
  isRuleEnd,
  isRuleRef,
} from './type-guards.js';
import { UnresolvedRule, ValidInput } from './types.js';

export type RuleStack = UnresolvedRule[][];
export type RootNode = Map<number, GraphNode>;
export type Pointers = GenericSet<GraphPointer, string>;

export const makePointers = (): Pointers => new GenericSet<GraphPointer, string>(pointer => pointer.id);

export class Graph {
  grammar: string;
  roots = new Map<number, RootNode>();
  #rootNode: RootNode;
  #previousCodePoints: number[] = [];

  constructor(grammar: string, stackedRules: (RuleStack | undefined)[], rootId: number) {
    this.grammar = grammar;
    const ruleRefs: RuleRef[] = [];
    const uniqueRules = new GenericSet<UnresolvedRule, string>(getSerializedRuleKey);
    for (let stackId = 0; stackId < stackedRules.length; stackId++) {
      const stack = stackedRules[stackId] as RuleStack;
      const nodes: RootNode = new Map();
      for (let pathId = 0; pathId < stack.length; pathId++) {
        const path = stack[pathId];
        let node: GraphNode | undefined = undefined;
        for (let stepId = path.length - 1; stepId >= 0; stepId--) {
          const nextNode = node;
          const rule = stack[pathId][stepId];
          uniqueRules.add(rule);
          if (isRuleRef(rule)) {
            ruleRefs.push(rule);
          }
          // rules coming in may be identical but have different references.
          // here, we ensure we always use the same reference for an identical rule.
          // this makes future comparisons easier.
          const uniqueRule = uniqueRules.get(rule);
          if (uniqueRule === undefined) {
            throw new Error('Could not get unique rule');
          }
          node = new GraphNode(uniqueRule, { stackId, pathId, stepId }, nextNode);
        }
        if (node === undefined) {
          throw new Error('Could not get node');
        }
        nodes.set(pathId, node);
      }

      this.roots.set(stackId, nodes);
    }

    const rootNode = this.roots.get(rootId);
    if (!rootNode) {
      throw new Error(`Root node not found for value: ${rootId}`);
    }
    this.#rootNode = rootNode;

    for (const ruleRef of ruleRefs) {
      const referencedNodes: GraphNode[] = [];
      for (const node of this.#getRootNode(ruleRef.value).values()) {
        if (!referencedNodes.includes(node)) {
          referencedNodes.push(node);
        }
      }
      ruleRef.nodes = referencedNodes;
    }
  }

  #getRootNode(value: number): RootNode {
    const rootNode = this.roots.get(value);
    if (!rootNode) {
      throw new Error(`Root node not found for value: ${value}`);
    }
    return rootNode;
  }

  #getInitialPointers(): Pointers {
    const pointers = makePointers();

    const rootNode = this.#rootNode;
    if (!rootNode) {
      throw new Error('Root node is not defined');
    }

    for (const [node, parent] of this.#fetchNodesForRootNode(rootNode)) {
      const pointer = new GraphPointer(node, parent);
      for (const resolvedPointer of this.#resolvePointer(pointer)) {
        pointers.add(resolvedPointer);
      }
    }
    return pointers;
  }

  #setValid(pointers: GraphPointer[], valid: boolean): void {
    for (const pointer of pointers) {
      pointer.valid = valid;
    }
  }

  #parse(currentPointers: Pointers, codePoint: number): Pointers {
    for (const [rule, graphPointers] of this.#iterateOverPointers(currentPointers)) {
      if (isRuleChar(rule)) {
        this.#setValid(graphPointers, rule.value.some(possibleCodePoint => (
          isRange(possibleCodePoint)
            ? isPointInRange(codePoint, possibleCodePoint)
            : codePoint === possibleCodePoint
        )));
      } else if (isRuleCharExcluded(rule)) {
        this.#setValid(graphPointers, rule.value.every(possibleCodePoint => (
          isRange(possibleCodePoint)
            ? !isPointInRange(codePoint, possibleCodePoint)
            : codePoint !== possibleCodePoint
        )));
      } else if (!isRuleEnd(rule)) {
        throw new Error(`Unsupported rule: ${rule}`);
      }
    }

    // a pointer's id is the sum of its node's id and its parent's id chain.
    // if two pointers share the same id, it means they point to the same node and have identical parent chains.
    // for the purposes of walking the graph, we only need to keep one of them.
    const nextPointers = makePointers();
    for (const currentPointer of currentPointers) {
      for (const unresolvedNextPointer of currentPointer.fetchNext()) {
        for (const resolvedNextPointer of this.#resolvePointer(unresolvedNextPointer)) {
          nextPointers.add(resolvedNextPointer);
        }
      }
    }
    return nextPointers;
  }

  *#resolvePointer(unresolvedPointer: GraphPointer): Generator<GraphPointer> {
    for (const resolvedPointer of unresolvedPointer.resolve()) {
      if (isRuleRef(resolvedPointer.node.rule)) {
        throw new Error('Encountered a reference rule when building pointers to the graph');
      }
      if (isRuleEnd(resolvedPointer.node.rule) && resolvedPointer.parent) {
        throw new Error('Encountered an ending rule with a parent when building pointers to the graph');
      }
      yield resolvedPointer;
    }
  }

  add(src: ValidInput, _pointers?: Pointers): Pointers {
    let pointers = _pointers ?? this.#getInitialPointers();
    const codePoints = getInputAsCodePoints(src);
    for (let codePointPos = 0; codePointPos < codePoints.length; codePointPos++) {
      const codePoint = codePoints[codePointPos];
      pointers = this.#parse(pointers, codePoint);
      if (pointers.size === 0) {
        throw new InputParseError(codePoints, codePointPos, this.#previousCodePoints);
      }
    }
    this.#previousCodePoints.push(...codePoints);
    return pointers;
  }

  // generator that yields either the node, or if a reference rule, the referenced node
  // we need this function, as distinct from leveraging the logic in GraphPointer,
  // because that needs a rule ref with already defined nodes; this function is used to _set_ those nodes
  *#fetchNodesForRootNode(
    rootNodes: RootNode,
    parent?: GraphPointer,
  ): Generator<[GraphNode, GraphPointer | undefined]> {
    for (const node of [...rootNodes.values()]) {
      const { rule } = node;
      if (isRuleRef(rule)) {
        yield* this.#fetchNodesForRootNode(this.#getRootNode(rule.value), new GraphPointer(node, parent));
      } else {
        yield [node, parent];
      }
    }
  }

  print(pointers?: Pointers, colors = false): string {
    const nodes = [...this.roots.values()].map(root => [...root.values()]);
    const graphView: string[] = [];
    for (const rootNode of nodes) {
      for (const node of rootNode) {
        graphView.push(node.print(pointers, true, colors ? colorize : noColorize));
      }
    }
    return `\n${graphView.join('\n')}`;
  }

  toString(): string {
    return this.print(undefined, true);
  }

  *#iterateOverPointers(pointers: Pointers): Generator<[UnresolvedRule, GraphPointer[]]> {
    // keyed on the rule itself; identical rules share a reference by this point
    const seenRules = new Map<UnresolvedRule, [UnresolvedRule, GraphPointer[]]>();
    for (const pointer of pointers) {
      const { rule } = pointer;
      if (isRuleRef(rule)) {
        throw new Error('Encountered a reference rule in the graph, this should not happen');
      }
      const seenRule = seenRules.get(rule);
      if (seenRule === undefined) {
        seenRules.set(rule, [rule, [pointer]]);
      } else {
        seenRule[1].push(pointer);
      }
    }

    yield* [...seenRules.values()];
  }
}
