import { InputParseError } from '../utils/errors/input-parse-error.js';
import { isPointInRange } from '../utils/is-point-in-range.js';
import { colorize, noColorize } from './colorize.js';
import { GenericSet } from './generic-set.js';
import { getInputAsCodePoints } from './get-input-as-code-points.js';
import { getSerializedRuleKey } from './get-serialized-rule-key.js';
import { GraphNode } from './graph-node.js';
import { GraphPointer, MAX_POINTER_DEPTH } from './graph-pointer.js';
import { RuleRef } from './rule-ref.js';
import {
  isRange,
  isRuleChar,
  isRuleCharExcluded,
  isRuleEnd,
  isRuleRef,
  type UnresolvedRule,
} from './type-guards.js';
import type { ValidInput } from './types.js';

/** The paths of a single rule, indexed by path id. */
export type RootNode = GraphNode[];

export type Pointers = GenericSet<GraphPointer, string>;

const makePointers = (): Pointers =>
  new GenericSet<GraphPointer, string>((pointer) => pointer.id);

export class Graph {
  public readonly grammar: string;
  public readonly roots: RootNode[] = [];

  private readonly rootNode: RootNode;
  private readonly previousCodePoints: number[] = [];

  constructor(
    grammar: string,
    stackedRules: (UnresolvedRule[][] | undefined)[],
    rootId: number
  ) {
    this.grammar = grammar;

    const ruleRefs: RuleRef[] = [];
    const uniqueRules = new GenericSet<UnresolvedRule, string>(getSerializedRuleKey);
    for (let stackId = 0; stackId < stackedRules.length; stackId += 1) {
      // A rule id with no definition leaves a hole in the rules array; it stays an
      // empty root here.
      const stack = stackedRules[stackId] ?? [];
      const nodes: RootNode = [];
      for (let pathId = 0; pathId < stack.length; pathId += 1) {
        const path = stack[pathId];
        let node: GraphNode | undefined = undefined;
        for (let stepId = path.length - 1; stepId >= 0; stepId -= 1) {
          const nextNode = node;
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
          node = new GraphNode(uniqueRule, { stackId, pathId, stepId }, nextNode);
        }
        if (node === undefined) {
          throw new Error('Could not get node');
        }
        nodes[pathId] = node;
      }

      this.roots[stackId] = nodes;
    }

    this.rootNode = this.getRootNode(rootId);

    for (const ruleRef of ruleRefs) {
      const referencedNodes: GraphNode[] = [];
      const seen = new Set<GraphNode>();
      for (const node of this.getRootNode(ruleRef.value)) {
        if (!seen.has(node)) {
          seen.add(node);
          referencedNodes.push(node);
        }
      }
      ruleRef.nodes = referencedNodes;
    }
  }

  getRootNode(value: number): RootNode {
    const rootNode = this.roots[value];
    if (!rootNode || rootNode.length === 0) {
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

  private *resolvePointer(unresolvedPointer: GraphPointer): IterableIterator<GraphPointer> {
    for (const resolvedPointer of unresolvedPointer.resolve()) {
      if (isRuleRef(resolvedPointer.node.rule)) {
        throw new Error('Encountered a reference rule when building pointers to the graph');
      }
      if (isRuleEnd(resolvedPointer.node.rule) && resolvedPointer.parent !== undefined) {
        throw new Error(
          'Encountered an ending rule with a parent when building pointers to the graph'
        );
      }
      yield resolvedPointer;
    }
  }

  add(src: ValidInput, pointers?: Pointers): Pointers {
    let currentPointers = pointers ?? this.getInitialPointers();
    const codePoints = getInputAsCodePoints(src);
    for (let codePointPos = 0; codePointPos < codePoints.length; codePointPos += 1) {
      currentPointers = this.parse(currentPointers, codePoints[codePointPos]);
      if (currentPointers.size === 0) {
        throw new InputParseError(codePoints, codePointPos, this.previousCodePoints);
      }
    }
    this.previousCodePoints.push(...codePoints);
    return currentPointers;
  }

  /**
   * Yields either the node, or if a reference rule, the referenced node.
   *
   * We need this function, as distinct from leveraging the logic in GraphPointer,
   * because that needs a rule ref with already defined nodes; this function is used
   * to _set_ those nodes.
   */
  private *fetchNodesForRootNode(
    rootNodes: RootNode,
    parent?: GraphPointer
  ): IterableIterator<[GraphNode, GraphPointer | undefined]> {
    // Walked with an explicit stack rather than recursively (see
    // `GraphPointer.resolve`), so that a long chain of rule references cannot
    // overrun the call stack.
    const stack: [GraphNode, GraphPointer | undefined][] = [];
    for (let i = rootNodes.length - 1; i >= 0; i -= 1) {
      stack.push([rootNodes[i], parent]);
    }
    while (stack.length) {
      const [node, nodeParent] = stack.pop() as [GraphNode, GraphPointer | undefined];
      const rule = node.rule;
      if (isRuleRef(rule)) {
        const pointer = new GraphPointer(node, nodeParent);
        if (pointer.depth >= MAX_POINTER_DEPTH) {
          throw new RangeError(
            'Maximum grammar depth exceeded; the grammar is most likely infinitely ' +
              'recursive (for instance a rule that references itself as its first element)'
          );
        }
        const referenced = this.getRootNode(rule.value);
        for (let i = referenced.length - 1; i >= 0; i -= 1) {
          stack.push([referenced[i], pointer]);
        }
      } else {
        yield [node, nodeParent];
      }
    }
  }

  print(pointers?: Pointers, colors = false): string {
    const graphView: string[] = [];
    for (const rootNode of this.roots) {
      for (const node of rootNode) {
        graphView.push(
          node.print({
            pointers,
            showPosition: true,
            colorize: colors ? colorize : noColorize,
          })
        );
      }
    }
    return `\n${graphView.join('\n')}`;
  }

  toString(): string {
    return this.print(undefined, true);
  }

  private *iterateOverPointers(
    pointers: Pointers
  ): IterableIterator<[UnresolvedRule, GraphPointer[]]> {
    // Keyed by the rule object itself; identical rules share a single reference.
    const seenRules = new Map<UnresolvedRule, [UnresolvedRule, GraphPointer[]]>();
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

    yield* [...seenRules.values()];
  }
}
