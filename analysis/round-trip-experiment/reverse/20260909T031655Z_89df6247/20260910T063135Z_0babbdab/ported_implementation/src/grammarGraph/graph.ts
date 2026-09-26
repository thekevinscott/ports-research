import { InputParseError } from '../utils/errors/inputParseError.js';
import { isPointInRange } from '../utils/isPointInRange.js';
import { colorize, type Colorize } from './colorize.js';
import { GenericSet } from './genericSet.js';
import {
  getInputAsCodePoints,
  type CodePointSource,
} from './getInputAsCodePoints.js';
import { getSerializedRuleKey } from './getSerializedRuleKey.js';
import { GraphNode, GraphNodeMeta } from './graphNode.js';
import { GraphPointer } from './graphPointer.js';
import { RuleRef } from './ruleRef.js';
import {
  isRange,
  isRuleChar,
  isRuleCharExcluded,
  isRuleEnd,
  isRuleRef,
  type GraphRule,
} from './typeGuards.js';

export type Pointers = GenericSet<GraphPointer, string>;

const makePointers = (): Pointers =>
  new GenericSet<GraphPointer, string>((p) => p.id);

export type StackedRules = (GraphRule[][] | null)[];

export class Graph {
  public readonly grammar: string;
  private readonly roots = new Map<number, Map<number, GraphNode>>();
  private readonly previousCodePoints: number[] = [];
  private readonly rootNode: Map<number, GraphNode>;

  public constructor(
    grammar: string,
    stackedRules: StackedRules,
    rootId: number
  ) {
    this.grammar = grammar;

    const ruleRefs: RuleRef[] = [];
    const uniqueRules = new GenericSet<GraphRule, string>(getSerializedRuleKey);
    for (let stackId = 0; stackId < stackedRules.length; stackId += 1) {
      const stack = stackedRules[stackId];
      if (stack === null || stack === undefined) {
        // a symbol that was referenced but never defined; the rules builder has
        // already rejected any grammar that can reach one
        continue;
      }
      const nodes = new Map<number, GraphNode>();
      for (let pathId = 0; pathId < stack.length; pathId += 1) {
        const path = stack[pathId];
        let node: GraphNode | undefined = undefined;
        for (let stepId = path.length - 1; stepId >= 0; stepId -= 1) {
          const nextNode: GraphNode | undefined = node;
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
            new GraphNodeMeta(stackId, pathId, stepId),
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
    if (rootNode === undefined) {
      throw new Error(`Root node not found for value: ${rootId}`);
    }
    this.rootNode = rootNode;

    for (const ruleRef of ruleRefs) {
      ruleRef.nodes = [...this.getRootNode(ruleRef.value).values()];
    }
  }

  private getRootNode(value: number): Map<number, GraphNode> {
    const node = this.roots.get(value);
    if (node === undefined) {
      throw new Error(`Root node not found for value: ${value}`);
    }
    return node;
  }

  private getInitialPointers(): Pointers {
    const pointers = makePointers();

    const rootNode = this.rootNode;
    if (rootNode === undefined) {
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
          valid = isRange(possibleCodePoint)
            ? isPointInRange(codePoint, possibleCodePoint)
            : codePoint === possibleCodePoint;
        }
        Graph.setValid(graphPointers, valid);
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
        Graph.setValid(graphPointers, valid);
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

  public add(src: CodePointSource, pointers?: Pointers): Pointers {
    let current = pointers !== undefined ? pointers : this.getInitialPointers();
    const codePoints = getInputAsCodePoints(src);
    for (
      let codePointPos = 0;
      codePointPos < codePoints.length;
      codePointPos += 1
    ) {
      current = this.parse(current, codePoints[codePointPos]);
      if (current.size === 0) {
        throw new InputParseError(codePoints, codePointPos, [
          ...this.previousCodePoints,
        ]);
      }
    }
    this.previousCodePoints.push(...codePoints);
    return current;
  }

  /**
   * Yield each node, or -- for a reference rule -- the referenced nodes.
   *
   * This is distinct from the logic in GraphPointer because that needs a rule ref
   * with already defined nodes; this function is used to _set_ those nodes.
   */
  private *fetchNodesForRootNode(
    rootNodes: Map<number, GraphNode>,
    parent?: GraphPointer | undefined
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

  public print(pointers?: Iterable<GraphPointer>, colors = false): string {
    const col: Colorize = colors ? colorize : (string) => `${string}`;
    const graphView: string[] = [];
    for (const nodes of this.roots.values()) {
      for (const node of nodes.values()) {
        graphView.push(
          node.print({ pointers, showPosition: true, colorize: col })
        );
      }
    }
    return `\n${graphView.join('\n')}`;
  }

  private static *iterateOverPointers(
    pointers: Iterable<GraphPointer>
  ): Generator<[GraphRule, GraphPointer[]]> {
    // keyed on rule identity, mirroring the reference implementation's `Map`
    const seenRules = new Map<GraphRule, [GraphRule, GraphPointer[]]>();
    for (const pointer of pointers) {
      const rule = pointer.rule;
      if (isRuleRef(rule)) {
        throw new Error(
          'Encountered a reference rule in the graph, this should not happen'
        );
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
