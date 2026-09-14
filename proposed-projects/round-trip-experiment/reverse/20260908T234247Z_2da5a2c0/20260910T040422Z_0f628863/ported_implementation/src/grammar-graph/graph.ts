import { InputParseError } from '../utils/errors/input-parse-error.ts';
import { isPointInRange } from '../utils/is-point-in-range.ts';
import { Color, type Colorize, colorize } from './colorize.ts';
import { GenericSet } from './generic-set.ts';
import { getInputAsCodePoints } from './get-input-as-code-points.ts';
import { getSerializedRuleKey } from './get-serialized-rule-key.ts';
import { GraphNode } from './graph-node.ts';
import { GraphPointer } from './graph-pointer.ts';
import type { RuleRef } from './rule-ref.ts';
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
  private roots = new Map<number, RootNode>();
  private rootNode: RootNode;
  private previousCodePoints: number[] = [];

  constructor(
    grammar: string,
    stackedRules: (UnresolvedRule[][] | undefined)[],
    rootId: number
  ) {
    this.grammar = grammar;

    const ruleRefs: RuleRef[] = [];
    const uniqueRules = new GenericSet<UnresolvedRule, string>(getSerializedRuleKey);
    for (let stackId = 0; stackId < stackedRules.length; stackId++) {
      const stack = stackedRules[stackId];
      if (stack === undefined) {
        throw new Error(`No rules defined for stack: ${stackId}`);
      }
      const nodes: RootNode = new Map();
      for (let pathId = 0; pathId < stack.length; pathId++) {
        const path = stack[pathId];
        let node: GraphNode | undefined = undefined;
        for (let stepId = path.length - 1; stepId >= 0; stepId--) {
          const next: GraphNode | undefined = node;
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
    if (!rootNode || rootNode.size === 0) {
      throw new Error(`Root node not found for value: ${rootId}`);
    }
    this.rootNode = rootNode;

    for (const ruleRef of ruleRefs) {
      ruleRef.nodes = [...this.getRootNode(ruleRef.value).values()];
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

  private setValid(pointers: GraphPointer[], valid: boolean): void {
    for (const pointer of pointers) {
      pointer.valid = valid;
    }
  }

  private parse(currentPointers: Pointers, codePoint: number): Pointers {
    for (const [rule, graphPointers] of this.iterateOverPointers(currentPointers)) {
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
        this.setValid(graphPointers, valid);
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
        this.setValid(graphPointers, valid);
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
        for (const resolvedNextPointer of this.resolvePointer(unresolvedNextPointer)) {
          nextPointers.add(resolvedNextPointer);
        }
      }
    }
    return nextPointers;
  }

  private *resolvePointer(unresolvedPointer: GraphPointer): Generator<GraphPointer> {
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

  add(src: ValidInput, providedPointers?: Pointers): Pointers {
    let pointers = providedPointers !== undefined ? providedPointers : this.getInitialPointers();
    const codePoints = getInputAsCodePoints(src);
    for (let codePointPos = 0; codePointPos < codePoints.length; codePointPos++) {
      const codePoint = codePoints[codePointPos];
      pointers = this.parse(pointers, codePoint);
      if (pointers.size === 0) {
        throw new InputParseError(codePoints, codePointPos, [...this.previousCodePoints]);
      }
    }
    this.previousCodePoints.push(...codePoints);
    return pointers;
  }

  /**
   * Yield either the node, or if a reference rule, the referenced node.
   *
   * This is distinct from the logic in `GraphPointer` because that needs a rule ref
   * with already-defined nodes; this function is used to _set_ those nodes.
   */
  private *fetchNodesForRootNode(
    rootNodes: RootNode,
    parent?: GraphPointer
  ): Generator<[GraphNode, GraphPointer | undefined]> {
    for (const node of [...rootNodes.values()]) {
      const rule = node.rule;
      if (isRuleRef(rule)) {
        yield* this.fetchNodesForRootNode(
          this.getRootNode(rule.value),
          new GraphPointer(node, parent)
        );
      } else {
        yield [node, parent];
      }
    }
  }

  print({
    pointers,
    colors = false,
  }: { pointers?: Pointers; colors?: boolean } = {}): string {
    const col: Colorize = colors ? colorize : (str, _color) => `${str}`;
    const nodes: GraphNode[][] = [...this.roots.values()].map((nodeMap) => [
      ...nodeMap.values(),
    ]);
    const graphView: string[] = [];
    for (const rootNode of nodes) {
      for (const node of rootNode) {
        graphView.push(node.print({ pointers, showPosition: true, colorize: col }));
      }
    }
    return '\n' + graphView.join('\n');
  }

  toString(): string {
    return this.print({ colors: true });
  }

  private *iterateOverPointers(
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
