import { InputParseError } from '../utils/errors/input-parse-error.js';
import { isPointInRange } from '../utils/is-point-in-range.js';
import { Colorize, colorize, noColor } from './colorize.js';
import { GenericSet } from './generic-set.js';
import { getInputAsCodePoints } from './get-input-as-code-points.js';
import { getSerializedRuleKey } from './get-serialized-rule-key.js';
import { GraphNode, GraphNodeMeta } from './graph-node.js';
import { GraphPointer } from './graph-pointer.js';
import {
  isRange,
  isRuleChar,
  isRuleCharExcluded,
  isRuleEnd,
  isRuleRef,
} from './type-guards.js';
import type { RuleRef } from './rule-ref.js';
import type { Range, Rule, ValidInput } from './types.js';

type RootNode = Map<number, GraphNode>;
type Pointers = GenericSet<GraphPointer, string>;

const makePointers = (): Pointers =>
  new GenericSet<GraphPointer, string>((p) => p.id);

export class Graph {
  grammar: string;
  roots = new Map<number, RootNode>();
  previousCodePoints: number[] = [];
  private _rootNode: RootNode;

  constructor(
    grammar: string,
    stackedRules: (Rule | RuleRef)[][][],
    rootId: number
  ) {
    this.grammar = grammar;

    const ruleRefs: RuleRef[] = [];
    const uniqueRules = new GenericSet<Rule | RuleRef, string>(
      getSerializedRuleKey
    );
    for (let stackId = 0; stackId < stackedRules.length; stackId++) {
      const stack = stackedRules[stackId] ?? [];
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
          if (uniqueRule === undefined) {
            throw new Error('Could not get unique rule');
          }
          node = new GraphNode(
            uniqueRule,
            meta(stackId, pathId, stepId),
            nextNode
          );
        }
        if (node === undefined) {
          throw new Error('Could not get node');
        }
        nodes.set(pathId, node);
      }

      this.roots.set(stackId, nodes);
    }

    const rootNode = this.roots.get(rootId);
    if (!rootNode || rootNode.size === 0) {
      throw new Error(`Root node not found for value: ${rootId}`);
    }
    this._rootNode = rootNode;

    for (const ruleRef of ruleRefs) {
      const referencedNodes: GraphNode[] = [];
      for (const node of this.getRootNode(ruleRef.value).values()) {
        if (!referencedNodes.includes(node)) {
          referencedNodes.push(node);
        }
      }
      ruleRef.nodes = referencedNodes;
    }
  }

  private getRootNode(value: number): RootNode {
    const rootNode = this.roots.get(value);
    if (!rootNode || rootNode.size === 0) {
      throw new Error(`Root node not found for value: ${value}`);
    }
    return rootNode;
  }

  private getInitialPointers(): Pointers {
    const pointers = makePointers();

    const rootNode = this._rootNode;
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
    for (const [rule, graphPointers] of Graph.iterateOverPointers(
      currentPointers
    )) {
      if (isRuleChar(rule)) {
        let valid = false;
        for (const possibleCodePoint of rule.value) {
          if (valid) {
            break;
          }
          if (isRange(possibleCodePoint)) {
            valid = isPointInRange(codePoint, possibleCodePoint as Range);
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
            valid = !isPointInRange(codePoint, possibleCodePoint as Range);
          } else {
            valid = codePoint !== possibleCodePoint;
          }
        }
        Graph.setValid(graphPointers, valid);
      } else if (!isRuleEnd(rule)) {
        throw new Error(`Unsupported rule: ${rule}`);
      }
    }

    // a pointer's id is the sum of its node's id and its parent's id chain.
    // if two pointers share the same id, it means they point to the same node and
    // have identical parent chains. for the purposes of walking the graph, we only
    // need to keep one of them.
    const nextPointers = makePointers();
    for (const currentPointer of currentPointers) {
      for (const unresolvedNextPointer of currentPointer.fetchNext()) {
        for (const resolvedNextPointer of this.resolvePointer(
          unresolvedNextPointer
        )) {
          nextPointers.add(resolvedNextPointer);
        }
      }
    }
    return nextPointers;
  }

  private *resolvePointer(
    unresolvedPointer: GraphPointer
  ): Generator<GraphPointer> {
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

  add(src: ValidInput, _pointers?: Pointers): Pointers {
    let pointers = _pointers !== undefined ? _pointers : this.getInitialPointers();
    const codePoints = getInputAsCodePoints(src);
    for (
      let codePointPos = 0;
      codePointPos < codePoints.length;
      codePointPos++
    ) {
      pointers = this.parse(pointers, codePoints[codePointPos]);
      if (pointers.size === 0) {
        throw new InputParseError(codePoints, codePointPos, [
          ...this.previousCodePoints,
        ]);
      }
    }
    for (const codePoint of codePoints) {
      this.previousCodePoints.push(codePoint);
    }
    return pointers;
  }

  /**
   * Yield either the node, or if a reference rule, the referenced node.
   *
   * This is distinct from the logic in GraphPointer because that needs a rule ref
   * with already defined nodes; this function is used to _set_ those nodes.
   */
  private *fetchNodesForRootNode(
    rootNodes: RootNode,
    parent?: GraphPointer
  ): Generator<[GraphNode, GraphPointer | undefined]> {
    for (const node of rootNodes.values()) {
      if (isRuleRef(node.rule)) {
        yield* this.fetchNodesForRootNode(
          this.getRootNode(node.rule.value),
          new GraphPointer(node, parent)
        );
      } else {
        yield [node, parent];
      }
    }
  }

  print(pointers?: Pointers, colors = false): string {
    const col: Colorize = colors ? colorize : noColor;
    const graphView: string[] = [];
    for (const nodes of this.roots.values()) {
      for (const node of nodes.values()) {
        graphView.push(node.print(pointers, true, col));
      }
    }
    return `\n${graphView.join('\n')}`;
  }

  toString(): string {
    return this.print(undefined, true);
  }

  private static *iterateOverPointers(
    pointers: Pointers
  ): Generator<[Rule, GraphPointer[]]> {
    // Rules are deduplicated by reference when the graph is built, so grouping by
    // object identity keeps distinct-but-equal rules apart the way a Map does.
    const seenRules = new Map<Rule, GraphPointer[]>();
    for (const pointer of pointers) {
      const rule = pointer.rule;
      if (isRuleRef(rule)) {
        throw new Error(
          'Encountered a reference rule in the graph, this should not happen'
        );
      }
      const entry = seenRules.get(rule as Rule);
      if (entry === undefined) {
        seenRules.set(rule as Rule, [pointer]);
      } else {
        entry.push(pointer);
      }
    }

    yield* seenRules.entries();
  }
}

const meta = (
  stackId: number,
  pathId: number,
  stepId: number
): GraphNodeMeta => ({ stackId, pathId, stepId });
