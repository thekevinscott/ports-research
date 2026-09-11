import { InputParseError } from '../utils/errors/inputParseError';
import { isPointInRange } from '../utils/isPointInRange';
import { colorize, noColor } from './colorize';
import type { Colorize } from './colorize';
import { GenericSet } from './genericSet';
import { getInputAsCodePoints } from './getInputAsCodePoints';
import { getSerializedRuleKey } from './getSerializedRuleKey';
import { GraphNode } from './graphNode';
import { GraphPointer } from './graphPointer';
import {
  isRange,
  isRuleChar,
  isRuleCharExcluded,
  isRuleEnd,
  isRuleRef,
} from './typeGuards';
import type { RuleRef } from './ruleRef';
import type { UnresolvedRule, ValidInput } from './types';

export type Pointers = GenericSet<GraphPointer, string>;

const makePointers = (): Pointers =>
  new GenericSet<GraphPointer, string>((pointer) => pointer.id);

export class Graph {
  public grammar: string;
  /** stackId -> pathId -> GraphNode */
  private roots = new Map<number, Map<number, GraphNode>>();
  private rootNode: Map<number, GraphNode>;
  private previousCodePoints: number[] = [];

  constructor(
    grammar: string,
    stackedRules: (UnresolvedRule[][] | undefined)[],
    rootId: number,
  ) {
    this.grammar = grammar;

    const ruleRefs: RuleRef[] = [];
    const uniqueRules = new GenericSet<UnresolvedRule, string>(
      getSerializedRuleKey,
    );
    for (let stackId = 0; stackId < stackedRules.length; stackId++) {
      const stack = stackedRules[stackId] ?? [];
      const nodes = new Map<number, GraphNode>();
      for (let pathId = 0; pathId < stack.length; pathId++) {
        const path = stack[pathId];
        let node: GraphNode | undefined;
        for (let stepId = path.length - 1; stepId >= 0; stepId--) {
          const next = node;
          const rule = path[stepId];
          uniqueRules.add(rule);
          if (isRuleRef(rule)) {
            ruleRefs.push(rule);
          }
          // rules coming in may be identical but have different references.
          // here, we ensure we always use the same reference for an identical
          // rule. this makes future comparisons easier.
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

      this.roots.set(stackId, nodes);
    }

    const rootNode = this.roots.get(rootId);
    if (!rootNode) {
      throw new Error(`Root node not found for value: ${rootId}`);
    }
    this.rootNode = rootNode;

    for (const ruleRef of ruleRefs) {
      const referencedNodes = new Set<GraphNode>();
      for (const node of this.getRootNode(ruleRef.value).values()) {
        referencedNodes.add(node);
      }
      ruleRef.nodes = [...referencedNodes];
    }
  }

  private getRootNode(value: number): Map<number, GraphNode> {
    const rootNode = this.roots.get(value);
    if (!rootNode) {
      throw new Error(`Root node not found for value: ${value}`);
    }
    return rootNode;
  }

  private getInitialPointers(): Pointers {
    const pointers = makePointers();

    const rootNode = this.rootNode;
    if (!rootNode) {
      throw new Error('Root node is not defined');
    }

    for (const [node, parent] of this.fetchNodesForRootNode(rootNode)) {
      const pointer = new GraphPointer(node, parent);
      for (const resolvedPointer of this.resolvePointer(pointer)) {
        pointers.add(resolvedPointer);
      }
    }
    return pointers;
  }

  private static setValid(pointers: GraphPointer[], valid: boolean): void {
    for (const pointer of pointers) {
      pointer.valid = valid;
    }
  }

  private parse(currentPointers: Pointers, codePoint: number): Pointers {
    for (const [rule, graphPointers] of this.iterateOverPointers(
      currentPointers,
    )) {
      if (isRuleChar(rule)) {
        let valid = false;
        for (const possibleCodePoint of rule.value) {
          if (valid) {
            break;
          }
          if (isRange(possibleCodePoint)) {
            valid = isPointInRange(codePoint, possibleCodePoint);
          } else {
            valid = codePoint === possibleCodePoint;
          }
        }
        Graph.setValid(graphPointers, valid);
      } else if (isRuleCharExcluded(rule)) {
        let valid = true;
        for (const possibleCodePoint of rule.value) {
          if (!valid) {
            break;
          }
          if (isRange(possibleCodePoint)) {
            valid = !isPointInRange(codePoint, possibleCodePoint);
          } else {
            valid = codePoint !== possibleCodePoint;
          }
        }
        Graph.setValid(graphPointers, valid);
      } else if (!isRuleEnd(rule)) {
        throw new Error(`Unsupported rule: ${JSON.stringify(rule)}`);
      }
    }

    // a pointer's id is the sum of its node's id and its parent's id chain.
    // if two pointers share the same id, it means they point to the same node
    // and have identical parent chains. for the purposes of walking the graph,
    // we only need to keep one of them.
    const nextPointers = makePointers();
    for (const currentPointer of currentPointers) {
      for (const unresolvedNextPointer of currentPointer.fetchNext()) {
        for (const resolvedNextPointer of this.resolvePointer(
          unresolvedNextPointer,
        )) {
          nextPointers.add(resolvedNextPointer);
        }
      }
    }
    return nextPointers;
  }

  private *resolvePointer(
    unresolvedPointer: GraphPointer,
  ): IterableIterator<GraphPointer> {
    for (const resolvedPointer of unresolvedPointer.resolve()) {
      if (isRuleRef(resolvedPointer.node.rule)) {
        throw new Error(
          'Encountered a reference rule when building pointers to the graph',
        );
      }
      if (isRuleEnd(resolvedPointer.node.rule) && resolvedPointer.parent) {
        throw new Error(
          'Encountered an ending rule with a parent when building pointers to the graph',
        );
      }
      yield resolvedPointer;
    }
  }

  add(src: ValidInput, pointers?: Pointers): Pointers {
    let currentPointers = pointers ?? this.getInitialPointers();
    const codePoints = getInputAsCodePoints(src);
    for (
      let codePointPos = 0;
      codePointPos < codePoints.length;
      codePointPos++
    ) {
      const codePoint = codePoints[codePointPos];
      currentPointers = this.parse(currentPointers, codePoint);
      if (currentPointers.size === 0) {
        throw new InputParseError(codePoints, codePointPos, [
          ...this.previousCodePoints,
        ]);
      }
    }
    this.previousCodePoints.push(...codePoints);
    return currentPointers;
  }

  /**
   * Yield either the node, or, for a reference rule, the referenced node.
   *
   * This is distinct from the logic in GraphPointer, which needs a rule ref
   * with already-defined nodes; this function is used to _set_ those nodes.
   */
  private *fetchNodesForRootNode(
    rootNodes: Map<number, GraphNode>,
    parent?: GraphPointer,
  ): IterableIterator<[GraphNode, GraphPointer | undefined]> {
    for (const node of rootNodes.values()) {
      const rule = node.rule;
      if (isRuleRef(rule)) {
        yield* this.fetchNodesForRootNode(
          this.getRootNode(rule.value),
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
    for (const nodes of this.roots.values()) {
      for (const node of nodes.values()) {
        graphView.push(node.print(col, pointers, true));
      }
    }
    return `\n${graphView.join('\n')}`;
  }

  private *iterateOverPointers(
    pointers: Pointers,
  ): IterableIterator<[UnresolvedRule, GraphPointer[]]> {
    // grouped by rule identity
    const seenRules = new Map<UnresolvedRule, GraphPointer[]>();
    for (const pointer of pointers) {
      const rule = pointer.rule;
      if (isRuleRef(rule)) {
        throw new Error(
          'Encountered a reference rule in the graph, this should not happen',
        );
      }
      const seenRule = seenRules.get(rule);
      if (seenRule === undefined) {
        seenRules.set(rule, [pointer]);
      } else {
        seenRule.push(pointer);
      }
    }

    for (const [rule, graphPointers] of seenRules) {
      yield [rule, graphPointers];
    }
  }
}
