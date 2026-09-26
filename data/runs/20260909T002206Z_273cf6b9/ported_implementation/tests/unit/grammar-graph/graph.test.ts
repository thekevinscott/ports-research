import { describe, expect, test } from 'vitest';
import {
  RuleChar,
  RuleCharExclude,
  RuleEnd,
  type UnresolvedRule,
} from '../../../src/grammar-graph/grammar-graph-types.ts';
import { Graph, type RootNode } from '../../../src/grammar-graph/graph.ts';
import { GraphNode } from '../../../src/grammar-graph/graph-node.ts';
import { GraphPointer } from '../../../src/grammar-graph/graph-pointer.ts';
import { Pointers } from '../../../src/grammar-graph/pointers.ts';
import { RuleRef } from '../../../src/grammar-graph/rule-ref.ts';
import { isRule } from '../../../src/grammar-graph/type-guards.ts';

// The reference implementation exposes these as dunder-named (but reachable) methods; in
// TypeScript they are `private`, so the tests reach them the same way the Python tests do.
interface GraphInternals {
  getRootNode: (value: number) => RootNode;
  iterateOverPointers: (
    pointers: Iterable<GraphPointer>,
  ) => Generator<[UnresolvedRule, GraphPointer[]]>;
}

const internals = (graph: Graph): GraphInternals => graph as unknown as GraphInternals;

const grammar = 'example-grammar';
const stackedRules: UnresolvedRule[][][] = [
  [
    [new RuleChar([65, 66, 67])],
    [new RuleChar([68, 69, 70])],
  ],
  [
    [new RuleChar([71, 72, 73])],
    [new RuleChar([74, 75, 76])],
  ],
];
const rootId = 0;

describe('graph', () => {
  test('should create a graph instance', () => {
    const graph = new Graph(grammar, stackedRules, rootId);
    expect(graph).toBeInstanceOf(Graph);
    expect(graph.grammar).toBe(grammar);
  });

  test('should get the root node', () => {
    const graph = new Graph(grammar, stackedRules, rootId);
    const rootNode = internals(graph).getRootNode(rootId);
    expect(rootNode).toBeInstanceOf(Map);
    expect(rootNode.size).toBe(2);
  });

  test('should get the initial pointers', () => {
    const graph = new Graph(grammar, stackedRules, rootId);
    const rootNode = internals(graph).getRootNode(rootId);
    expect(rootNode).toBeInstanceOf(Map);
    expect(rootNode.size).toBe(2);
  });

  test('should print the graph', () => {
    const graph = new Graph(grammar, stackedRules, rootId);
    const printedGraph = graph.print(undefined, true);
    expect(typeof printedGraph).toBe('string');
    expect(printedGraph.length).toBeGreaterThan(0);
  });

  test('should iterate over pointers', () => {
    const graph = new Graph(grammar, stackedRules, rootId);
    const rules: UnresolvedRule[] = [
      new RuleChar([65, 66, 67]),
      new RuleChar([68, 69, 70]),
      new RuleChar([71, 72, 73]),
      new RuleChar([74, 75, 76]),
      new RuleCharExclude([1]),
      new RuleEnd(),
    ];
    const mockPointers = new Pointers(
      ...rules.map((rule, idx) => new GraphPointer(
        new GraphNode(rule, { stackId: idx, pathId: idx, stepId: idx }),
      )),
    );

    const result = [...internals(graph).iterateOverPointers(mockPointers)];
    expect(result).toHaveLength(6);
    const allPointers = [...mockPointers];
    for (const [rule, pointers] of result) {
      expect(isRule(rule)).toBe(true);
      expect(pointers.length).toBeGreaterThanOrEqual(1);
      for (const pointer of pointers) {
        expect(allPointers).toContain(pointer);
      }
    }
  });

  test('should raise error on reference rule', () => {
    const graph = new Graph(grammar, stackedRules, rootId);
    const mockPointers = [
      new GraphPointer(
        new GraphNode(new RuleRef(0), { stackId: 0, pathId: 0, stepId: 0 }),
      ),
    ];

    expect(() => [...internals(graph).iterateOverPointers(mockPointers)])
      .toThrow('Encountered a reference rule in the graph');
  });
});
