import { InputParseError } from '../utils/errors/input-parse-error.ts';
import { isPointInRange } from '../utils/is-point-in-range.ts';
import { colorize, noColor } from './colorize.ts';
import { GenericSet } from './generic-set.ts';
import { getInputAsCodePoints } from './get-input-as-code-points.ts';
import { getSerializedRuleKey } from './get-serialized-rule-key.ts';
import { GraphNode } from './graph-node.ts';
import type { GraphNodeMeta } from './graph-node.ts';
import { GraphPointer } from './graph-pointer.ts';
import { RuleRef } from './rule-ref.ts';
import {
  isRange,
  isRuleChar,
  isRuleCharExcluded,
  isRuleEnd,
  isRuleRef,
} from './type-guards.ts';
import type { UnresolvedRule, ValidInput } from './types.ts';

export type RootNode = Map<number, GraphNode>;
export type Pointers = GenericSet<GraphPointer, string>;

const makePointers = (): Pointers =>
  new GenericSet<GraphPointer, string>((pointer) => pointer.id);

export class Graph {
  grammar: string;
  private _roots = new Map<number, RootNode>();
  private _rootNode: RootNode;
  private _previousCodePoints: number[] = [];

  constructor(grammar: string, stackedRules: UnresolvedRule[][][], rootId: number) {
    this.grammar = grammar;
    const ruleRefs: RuleRef[] = [];
    const uniqueRules = new GenericSet<UnresolvedRule, string>(getSerializedRuleKey);
    for (let stackId = 0; stackId < stackedRules.length; stackId++) {
      const stack = stackedRules[stackId];
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
          // here, we ensure we always use the same reference for an identical
          // rule. this makes future comparisons easier.
          const uniqueRule = uniqueRules.get(rule);
          if (!uniqueRule) {
            throw new Error('Could not get unique rule');
          }
          const meta: GraphNodeMeta = { stackId, pathId, stepId };
          node = new GraphNode(uniqueRule, meta, nextNode);
        }
        if (!node) {
          throw new Error('Could not get node');
        }
        nodes.set(pathId, node);
      }

      this._roots.set(stackId, nodes);
    }

    const rootNode = this._roots.get(rootId);
    if (!rootNode) {
      throw new Error(`Root node not found for value: ${rootId}`);
    }
    this._rootNode = rootNode;

    for (const ruleRef of ruleRefs) {
      const referencedNodes: GraphNode[] = [];
      for (const node of this._getRootNode(ruleRef.value).values()) {
        if (!referencedNodes.includes(node)) {
          referencedNodes.push(node);
        }
      }
      ruleRef.nodes = referencedNodes;
    }
  }

  private _getRootNode(value: number): RootNode {
    const rootNode = this._roots.get(value);
    if (!rootNode) {
      throw new Error(`Root node not found for value: ${value}`);
    }
    return rootNode;
  }

  private _getInitialPointers(): Pointers {
    const pointers = makePointers();

    const rootNode = this._rootNode;
    if (!rootNode) {
      throw new Error('Root node is not defined');
    }

    for (const [node, parent] of this._fetchNodesForRootNode(rootNode)) {
      const pointer = new GraphPointer(node, parent);
      for (const resolvedPointer of this._resolvePointer(pointer)) {
        pointers.add(resolvedPointer);
      }
    }
    return pointers;
  }

  private _setValid(pointers: GraphPointer[], valid: boolean): void {
    for (const pointer of pointers) {
      pointer.valid = valid;
    }
  }

  private _parse(currentPointers: Pointers, codePoint: number): Pointers {
    for (const [rule, graphPointers] of this._iterateOverPointers(currentPointers)) {
      if (isRuleChar(rule)) {
        const valid = rule.value.some((possibleCodePoint) =>
          isRange(possibleCodePoint)
            ? isPointInRange(codePoint, possibleCodePoint)
            : codePoint === possibleCodePoint
        );
        this._setValid(graphPointers, valid);
      } else if (isRuleCharExcluded(rule)) {
        const valid = rule.value.every((possibleCodePoint) =>
          isRange(possibleCodePoint)
            ? !isPointInRange(codePoint, possibleCodePoint)
            : codePoint !== possibleCodePoint
        );
        this._setValid(graphPointers, valid);
      } else if (!isRuleEnd(rule)) {
        throw new Error(`Unsupported rule: ${JSON.stringify(rule)}`);
      }
    }

    // a pointer's id is the sum of its node's id and its parent's id chain.
    // if two pointers share the same id, it means they point to the same node and
    // have identical parent chains. for the purposes of walking the graph, we only
    // need to keep one of them.
    const nextPointers = makePointers();
    for (const currentPointer of currentPointers) {
      for (const unresolvedNextPointer of currentPointer.fetchNext()) {
        for (const resolvedNextPointer of this._resolvePointer(unresolvedNextPointer)) {
          nextPointers.add(resolvedNextPointer);
        }
      }
    }
    return nextPointers;
  }

  private *_resolvePointer(unresolvedPointer: GraphPointer): Generator<GraphPointer> {
    for (const resolvedPointer of unresolvedPointer.resolve()) {
      if (isRuleRef(resolvedPointer.node.rule)) {
        throw new Error(
          'Encountered a reference rule when building pointers to the graph'
        );
      }
      if (isRuleEnd(resolvedPointer.node.rule) && resolvedPointer.parent) {
        throw new Error(
          'Encountered an ending rule with a parent when building pointers to the graph'
        );
      }
      yield resolvedPointer;
    }
  }

  add(src: ValidInput, pointers?: Pointers): Pointers {
    if (!pointers) {
      pointers = this._getInitialPointers();
    }
    const codePoints = getInputAsCodePoints(src);
    for (let codePointPos = 0; codePointPos < codePoints.length; codePointPos++) {
      pointers = this._parse(pointers, codePoints[codePointPos]);
      if (pointers.size === 0) {
        throw new InputParseError(codePoints, codePointPos, [
          ...this._previousCodePoints,
        ]);
      }
    }
    this._previousCodePoints.push(...codePoints);
    return pointers;
  }

  /**
   * Generator that yields either the node, or if a reference rule, the referenced
   * node. We need this function, as distinct from leveraging the logic in
   * GraphPointer, because that needs a rule ref with already defined nodes; this
   * function is used to _set_ those nodes.
   */
  private *_fetchNodesForRootNode(
    rootNodes: RootNode,
    parent?: GraphPointer
  ): Generator<[GraphNode, GraphPointer | undefined]> {
    for (const node of rootNodes.values()) {
      const rule = node.rule;
      if (isRuleRef(rule)) {
        yield* this._fetchNodesForRootNode(
          this._getRootNode(rule.value),
          new GraphPointer(node, parent)
        );
      } else {
        yield [node, parent];
      }
    }
  }

  print(pointers?: Pointers, colors = false): string {
    const nodes = [...this._roots.values()].map((rootNodes) => [...rootNodes.values()]);
    const graphView: string[] = [];
    for (const rootNode of nodes) {
      for (const node of rootNode) {
        graphView.push(
          node.print({
            pointers,
            showPosition: true,
            colorize: colors ? colorize : noColor,
          })
        );
      }
    }
    return `\n${graphView.join('\n')}`;
  }

  private *_iterateOverPointers(
    pointers: Pointers
  ): Generator<[UnresolvedRule, GraphPointer[]]> {
    const seenRules = new Map<UnresolvedRule, GraphPointer[]>();
    for (const pointer of pointers) {
      const rule = pointer.rule;
      if (isRuleRef(rule)) {
        throw new Error(
          'Encountered a reference rule in the graph, this should not happen'
        );
      }
      const seenRule = seenRules.get(rule);
      if (!seenRule) {
        seenRules.set(rule, [pointer]);
      } else {
        seenRule.push(pointer);
      }
    }
    yield* seenRules.entries();
  }
}
