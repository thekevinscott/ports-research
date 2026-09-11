import { InputParseError } from '../utils/errors/index.js';
import { isPointInRange } from '../utils/isPointInRange.js';
import { colorize } from './colorize.js';
import { getInputAsCodePoints } from './getInputAsCodePoints.js';
import { getSerializedRuleKey } from './getSerializedRuleKey.js';
import type {
  Colorize,
  Range,
  ResolvedRule,
  UnresolvedRule,
  ValidInput,
} from './grammarGraphTypes.js';
import { GraphNode } from './graphNode.js';
import { GraphPointer } from './graphPointer.js';
import { Pointers } from './pointers.js';
import type { RuleRef } from './ruleRef.js';
import {
  isRange,
  isRuleChar,
  isRuleCharExclude,
  isRuleEnd,
  isRuleRef,
} from './typeGuards.js';

export type RootNode = Map<number, GraphNode>;

const noColor: Colorize = (text) => `${text}`;

export class Graph {
  #roots: Map<number, RootNode>;
  #rootNode: RootNode;
  grammar: string;
  previousCodePoints: number[];

  constructor(
    grammar: string,
    stackedRules: UnresolvedRule[][][],
    rootId: number,
  ) {
    this.#roots = new Map();
    this.grammar = grammar;
    this.previousCodePoints = [];
    const ruleRefs: RuleRef[] = [];
    const uniqueRules = new Map<string, UnresolvedRule>();

    for (let stackId = 0; stackId < stackedRules.length; stackId++) {
      const stack = stackedRules[stackId];
      const nodes: RootNode = new Map();
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
            throw new Error('Could not get unique rule');
          }
          node = new GraphNode(uniqueRule, { stackId, pathId, stepId }, nextNode);
        }

        if (node === null) {
          throw new Error('Could not get node');
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
      ruleRef.nodes = new Set(this.#getRootNode(ruleRef.value).values());
    }
  }

  #getRootNode(value: number): RootNode {
    const rootNode = this.#roots.get(value);
    if (rootNode === undefined) {
      throw new Error(`Root node not found for value: ${value}`);
    }
    return rootNode;
  }

  #getInitialPointers(): Pointers {
    const pointers = new Pointers();

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
        let valid = false;
        for (const possibleCodePoint of rule.value) {
          if (valid === true) {
            // already matched; nothing left to check
          } else if (isRange(possibleCodePoint)) {
            if (isPointInRange(codePoint, possibleCodePoint as Range)) {
              valid = true;
            }
          } else if (codePoint === possibleCodePoint) {
            valid = true;
          }
        }
        this.#setValid(graphPointers, valid);
      } else if (isRuleCharExclude(rule)) {
        let valid = true;
        for (const possibleCodePoint of rule.value) {
          if (valid === false) {
            // already excluded; nothing left to check
          } else if (isRange(possibleCodePoint)) {
            if (isPointInRange(codePoint, possibleCodePoint as Range)) {
              valid = false;
            }
          } else if (codePoint === possibleCodePoint) {
            valid = false;
          }
        }
        this.#setValid(graphPointers, valid);
      } else if (!isRuleEnd(rule)) {
        throw new Error(`Unsupported rule: ${rule}`);
      }
    }

    // a pointer's id is the sum of its node's id and its parent's id chain.
    // if two pointers share the same id, it means they point to the same node and have identical
    // parent chains. for the purposes of walking the graph, we only need to keep one of them.
    const nextPointers = new Pointers();
    for (const currentPointer of currentPointers) {
      for (const unresolvedNextPointer of currentPointer.fetchNext()) {
        for (const resolvedNextPointer of this.#resolvePointer(unresolvedNextPointer)) {
          nextPointers.add(resolvedNextPointer);
        }
      }
    }
    return nextPointers;
  }

  *#resolvePointer(
    unresolvedPointer: GraphPointer,
  ): Generator<GraphPointer<ResolvedRule>> {
    for (const resolvedPointer of unresolvedPointer.resolve()) {
      if (isRuleRef(resolvedPointer.node.rule)) {
        throw new Error(
          'Encountered a reference rule when building pointers to the graph',
        );
      }
      if (isRuleEnd(resolvedPointer.node.rule) && resolvedPointer.parent !== null) {
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
    let nextPointers = pointers ?? this.#getInitialPointers();

    const codePoints = getInputAsCodePoints(src);
    for (const codePoint of codePoints) {
      if (!Number.isInteger(codePoint)) {
        throw new Error('code_point must be an integer!');
      }
    }

    for (let codePointPos = 0; codePointPos < codePoints.length; codePointPos++) {
      const codePoint = codePoints[codePointPos];
      nextPointers = this.#parse(nextPointers, codePoint);
      if (nextPointers.size === 0) {
        throw new InputParseError(codePoints, codePointPos, this.previousCodePoints);
      }
    }
    this.previousCodePoints.push(...codePoints);
    return nextPointers;
  }

  // generator that yields either the node, or if a reference rule, the referenced node.
  // we need this function, as distinct from leveraging the logic in GraphPointer,
  // because that needs a rule ref with already defined nodes; this function is used to _set_ those
  // nodes.
  *#fetchNodesForRootNode(
    rootNodes: RootNode,
    parent: GraphPointer | null = null,
  ): Generator<[GraphNode, GraphPointer | null]> {
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

  print(pointers?: Pointers, colors = false): string {
    const nodes: GraphNode[][] = [...this.#roots.values()].map((rootNode) => [
      ...rootNode.values(),
    ]);
    const graphView: string[] = [];
    for (const rootNode of nodes) {
      for (const node of rootNode) {
        graphView.push(
          node.print({
            pointers: pointers ?? new Pointers(),
            show_position: true,
            colorize: colors ? colorize : noColor,
          }),
        );
      }
    }

    return graphView.join('\n');
  }

  *#iterateOverPointers(
    pointers: Pointers,
  ): Generator<[UnresolvedRule, GraphPointer[]]> {
    // rules are deduplicated by reference, matching the reference implementation's use of an
    // identity-hashed dict keyed on the rule object.
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
