import { InputParseError } from '../utils/errors/index.js';
import { isPointInRange } from '../utils/is-point-in-range.js';
import { colorize } from './colorize.js';
import { getInputAsCodePoints } from './get-input-as-code-points.js';
import { getSerializedRuleKey } from './get-serialized-rule-key.js';
import type {
  ResolvedGraphPointer,
  UnresolvedRule,
  ValidInput,
} from './grammar-graph-types.js';
import { GraphNode } from './graph-node.js';
import { GraphPointer } from './graph-pointer.js';
import { Pointers } from './pointers.js';
import type { RuleRef } from './rule-ref.js';
import {
  isRange,
  isRuleChar,
  isRuleCharExclude,
  isRuleEnd,
  isRuleRef,
} from './type-guards.js';

export type RootNode = Map<number, GraphNode>;

export class Graph {
  private roots = new Map<number, RootNode>();
  grammar: string;
  private rootNode: RootNode;
  previousCodePoints: number[] = [];

  constructor(
    grammar: string,
    stackedRules: UnresolvedRule[][][],
    rootId: number,
  ) {
    this.grammar = grammar;
    const ruleRefs: RuleRef[] = [];
    const uniqueRules = new Map<string, UnresolvedRule>();

    for (let stackId = 0; stackId < stackedRules.length; stackId++) {
      const stack = stackedRules[stackId];
      const nodes: RootNode = new Map();
      for (let pathId = 0; pathId < stack.length; pathId++) {
        const path = stack[pathId];
        let node: GraphNode | undefined;
        for (let stepId = path.length - 1; stepId >= 0; stepId--) {
          const nextNode = node;
          const rule = stack[pathId][stepId];
          const key = getSerializedRuleKey(rule);
          uniqueRules.set(key, rule);
          if (isRuleRef(rule)) {
            ruleRefs.push(rule);
          }
          // rules coming in may be identical but have different references.
          // here, we ensure we always use the same reference for an identical rule.
          // this makes future comparisons easier.
          const uniqueRule = uniqueRules.get(key);
          if (uniqueRule === undefined) {
            throw new Error('Could not get unique rule');
          }
          node = new GraphNode(
            uniqueRule,
            {
              stackId,
              pathId,
              stepId,
            },
            nextNode,
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
      const referencedNodes = new Set<GraphNode>();
      for (const node of this.getRootNode(ruleRef.value).values()) {
        referencedNodes.add(node);
      }
      ruleRef.nodes = referencedNodes;
    }
  }

  private getRootNode(value: number): RootNode {
    const rootNode = this.roots.get(value);
    if (rootNode === undefined) {
      throw new Error(`Root node not found for value: ${value}`);
    }
    return rootNode;
  }

  private getInitialPointers(): Pointers {
    const pointers = new Pointers();

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
    for (const [rule, graphPointers] of this.iterateOverPointers(
      currentPointers,
    )) {
      if (isRuleChar(rule)) {
        let valid = false;
        for (const possibleCodePoint of rule.value) {
          if (valid === true) {
            continue;
          } else if (isRange(possibleCodePoint)) {
            if (isPointInRange(codePoint, possibleCodePoint)) {
              valid = true;
            }
          } else if (codePoint === possibleCodePoint) {
            valid = true;
          }
        }
        this.setValid(graphPointers, valid);
      } else if (isRuleCharExclude(rule)) {
        let valid = true;
        for (const possibleCodePoint of rule.value) {
          if (valid === false) {
            continue;
          } else if (isRange(possibleCodePoint)) {
            if (isPointInRange(codePoint, possibleCodePoint)) {
              valid = false;
            }
          } else if (codePoint === possibleCodePoint) {
            valid = false;
          }
        }
        this.setValid(graphPointers, valid);
      } else if (!isRuleEnd(rule)) {
        throw new Error(`Unsupported rule: ${rule}`);
      }
    }

    // a pointer's id is the sum of its node's id and its parent's id chain.
    // if two pointers share the same id, it means they point to the same node and have identical parent chains.
    // for the purposes of walking the graph, we only need to keep one of them.
    const nextPointers = new Pointers();
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
  ): Generator<ResolvedGraphPointer> {
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
    if (typeof src !== 'string') {
      throw new Error('src must be a string in graph.add');
    }
    let currentPointers = pointers ?? this.getInitialPointers();

    const codePoints = getInputAsCodePoints(src);
    for (const codePoint of codePoints) {
      if (!Number.isInteger(codePoint)) {
        throw new Error('code_point must be an integer!');
      }
    }

    for (let codePointPos = 0; codePointPos < codePoints.length; codePointPos++) {
      const codePoint = codePoints[codePointPos];
      currentPointers = this.parse(currentPointers, codePoint);
      if (currentPointers.size === 0) {
        throw new InputParseError(
          codePoints,
          codePointPos,
          this.previousCodePoints,
        );
      }
    }
    this.previousCodePoints.push(...codePoints);
    return currentPointers;
  }

  // generator that yields either the node, or if a reference rule, the referenced node
  // we need this function, as distinct from leveraging the logic in GraphPointer,
  // because that needs a rule ref with already defined nodes; this function is used to _set_ those nodes
  private *fetchNodesForRootNode(
    rootNodes: RootNode,
    parent?: GraphPointer,
  ): Generator<[GraphNode, GraphPointer | undefined]> {
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

  print(pointers?: Pointers, colors = false): string {
    const nodes: GraphNode[][] = [...this.roots.values()].map((rootNode) => [
      ...rootNode.values(),
    ]);
    const graphView: string[] = [];
    for (const rootNode of nodes) {
      for (const node of rootNode) {
        graphView.push(
          node.print({
            pointers: pointers ?? new Pointers(),
            showPosition: true,
            colorize: colors ? colorize : (s) => String(s),
          }),
        );
      }
    }

    return graphView.join('\n');
  }

  private *iterateOverPointers(
    pointers: Pointers,
  ): Generator<[UnresolvedRule, GraphPointer[]]> {
    const seenRules = new Map<UnresolvedRule, GraphPointer[]>();
    for (const pointer of pointers) {
      const rule = pointer.rule;
      if (isRuleRef(rule)) {
        throw new Error('Encountered a reference rule in the graph');
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
