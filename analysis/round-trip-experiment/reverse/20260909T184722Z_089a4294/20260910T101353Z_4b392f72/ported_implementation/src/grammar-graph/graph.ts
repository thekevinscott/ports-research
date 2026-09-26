import { InputParseError } from '../utils/errors/input-parse-error';
import { isPointInRange } from '../utils/is-point-in-range';
import { colorize, noColor } from './colorize';
import type { Colorize } from './colorize';
import { GenericSet } from './generic-set';
import { getInputAsCodePoints } from './get-input-as-code-points';
import { getSerializedRuleKey } from './get-serialized-rule-key';
import { GraphNode } from './graph-node';
import type { GraphRule } from './graph-node';
import { GraphPointer } from './graph-pointer';
import { RuleRef } from './rule-ref';
import {
  isRange,
  isRuleChar,
  isRuleCharExcluded,
  isRuleEnd,
  isRuleRef,
} from './type-guards';
import type { ValidInput } from './types';

export type RootNode = Map<number, GraphNode>;

export type StackedRules = (GraphRule[][] | null)[];

const makePointers = (): GenericSet<GraphPointer, string> =>
  new GenericSet<GraphPointer, string>(p => p.id);

export class Graph {
  grammar: string;
  #roots = new Map<number, RootNode>();
  #previousCodePoints: number[] = [];
  #rootNode: RootNode;

  constructor(grammar: string, stackedRules: StackedRules, rootId: number) {
    this.grammar = grammar;

    const ruleRefs: RuleRef[] = [];
    const uniqueRules = new GenericSet<GraphRule, string>(getSerializedRuleKey);
    for (let stackId = 0; stackId < stackedRules.length; stackId++) {
      const stack = stackedRules[stackId] ?? [];
      const nodes: RootNode = new Map();
      for (let pathId = 0; pathId < stack.length; pathId++) {
        const path = stack[pathId];
        let node: GraphNode | undefined;
        for (let stepId = path.length - 1; stepId >= 0; stepId--) {
          const next = node;
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
          node = new GraphNode(uniqueRule, { stackId, pathId, stepId }, next);
        }
        if (node === undefined) {
          throw new Error('Could not get node');
        }
        nodes.set(pathId, node);
      }

      this.#roots.set(stackId, nodes);
    }

    const rootNode = this.#roots.get(rootId);
    if (!rootNode?.size) {
      throw new Error(`Root node not found for value: ${rootId}`);
    }
    this.#rootNode = rootNode;

    for (const ruleRef of ruleRefs) {
      ruleRef.nodes = [...this.#getRootNode(ruleRef.value).values()];
    }
  }

  #getRootNode(value: number): RootNode {
    const rootNode = this.#roots.get(value);
    if (!rootNode?.size) {
      throw new Error(`Root node not found for value: ${value}`);
    }
    return rootNode;
  }

  #getInitialPointers(): GenericSet<GraphPointer, string> {
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

  #parse(
    currentPointers: GenericSet<GraphPointer, string>,
    codePoint: number,
  ): GenericSet<GraphPointer, string> {
    for (const [rule, graphPointers] of this.#iterateOverPointers(currentPointers)) {
      if (isRuleChar(rule)) {
        let valid = false;
        for (const possibleCodePoint of rule.value) {
          if (valid) {
            break;
          }
          valid = isRange(possibleCodePoint)
            ? isPointInRange(codePoint, possibleCodePoint)
            : codePoint === possibleCodePoint;
        }
        this.#setValid(graphPointers, valid);
      } else if (isRuleCharExcluded(rule)) {
        let valid = true;
        for (const possibleCodePoint of rule.value) {
          if (!valid) {
            break;
          }
          valid = isRange(possibleCodePoint)
            ? !isPointInRange(codePoint, possibleCodePoint)
            : codePoint !== possibleCodePoint;
        }
        this.#setValid(graphPointers, valid);
      } else if (!isRuleEnd(rule)) {
        throw new Error(`Unsupported rule: ${rule}`);
      }
    }

    // a pointer's id is the sum of its node's id and its parent's id chain.
    // if two pointers share the same id, it means they point to the same node and have
    // identical parent chains. for the purposes of walking the graph, we only need to
    // keep one of them.
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
        throw new Error(
          'Encountered an ending rule with a parent when building pointers to the graph',
        );
      }
      yield resolvedPointer;
    }
  }

  add(
    src: ValidInput,
    pointers?: GenericSet<GraphPointer, string>,
  ): GenericSet<GraphPointer, string> {
    let currentPointers = pointers ?? this.#getInitialPointers();
    const codePoints = getInputAsCodePoints(src);
    for (let codePointPos = 0; codePointPos < codePoints.length; codePointPos++) {
      currentPointers = this.#parse(currentPointers, codePoints[codePointPos]);
      if (currentPointers.size === 0) {
        throw new InputParseError(codePoints, codePointPos, this.#previousCodePoints);
      }
    }
    this.#previousCodePoints.push(...codePoints);
    return currentPointers;
  }

  // generator that yields either the node, or if a reference rule, the referenced node
  // we need this function, as distinct from leveraging the logic in GraphPointer,
  // because that needs a rule ref with already defined nodes; this function is used to
  // _set_ those nodes
  *#fetchNodesForRootNode(
    rootNodes: RootNode,
    parent?: GraphPointer,
  ): Generator<[GraphNode, GraphPointer | undefined]> {
    for (const node of rootNodes.values()) {
      const rule = node.rule;
      if (isRuleRef(rule)) {
        yield* this.#fetchNodesForRootNode(
          this.#getRootNode(rule.value),
          new GraphPointer(node, parent),
        );
      } else {
        yield [node, parent];
      }
    }
  }

  print(pointers?: Iterable<GraphPointer>, colors = false): string {
    const col: Colorize = colors ? colorize : noColor;
    const graphView: string[] = [];
    for (const rootNode of this.#roots.values()) {
      for (const node of rootNode.values()) {
        graphView.push(node.print(col, pointers, true));
      }
    }
    return `\n${graphView.join('\n')}`;
  }

  toString(): string {
    return this.print(undefined, true);
  }

  *#iterateOverPointers(
    pointers: GenericSet<GraphPointer, string>,
  ): Generator<[GraphRule, GraphPointer[]]> {
    // rules are deduplicated by reference, mirroring the identity-keyed map of the
    // reference implementation.
    const seenRules = new Map<GraphRule, [GraphRule, GraphPointer[]]>();
    for (const pointer of pointers) {
      const rule = pointer.rule;
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

    yield* seenRules.values();
  }
}
