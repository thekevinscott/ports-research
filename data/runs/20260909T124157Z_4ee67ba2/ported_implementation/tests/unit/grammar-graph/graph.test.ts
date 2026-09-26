import assert from 'node:assert/strict';
import { describe, test } from 'node:test';
import {
  RuleChar,
  RuleCharExclude,
  RuleEnd,
  type UnresolvedRule,
} from '../../../src/grammar-graph/grammar-graph-types.ts';
import { Graph } from '../../../src/grammar-graph/graph.ts';
import { GraphNode } from '../../../src/grammar-graph/graph-node.ts';
import { GraphPointer } from '../../../src/grammar-graph/graph-pointer.ts';
import { Pointers } from '../../../src/grammar-graph/pointers.ts';
import { RuleRef } from '../../../src/grammar-graph/rule-ref.ts';
import { isRule } from '../../../src/grammar-graph/type-guards.ts';

const grammar = 'example-grammar';
const stackedRules: UnresolvedRule[][][] = [
  [[new RuleChar([65, 66, 67])], [new RuleChar([68, 69, 70])]],
  [[new RuleChar([71, 72, 73])], [new RuleChar([74, 75, 76])]],
];
const rootId = 0;

const META = { stackId: 1, pathId: 1, stepId: 1 };

describe('graph', () => {
  test('should create a graph instance', () => {
    const graph = new Graph(grammar, stackedRules, rootId);
    assert.ok(graph instanceof Graph);
    assert.equal(graph.grammar, grammar);
  });

  test('should get the root node', () => {
    const graph = new Graph(grammar, stackedRules, rootId);
    const rootNode = graph.getRootNode(rootId);
    assert.ok(rootNode instanceof Map);
    assert.equal(rootNode.size, 2);
  });

  test('should get the initial pointers', () => {
    const graph = new Graph(grammar, stackedRules, rootId);
    const rootNode = graph.getRootNode(rootId);
    assert.ok(rootNode instanceof Map);
    assert.equal(rootNode.size, 2);
  });

  test('should print the graph', () => {
    const graph = new Graph(grammar, stackedRules, rootId);
    const printedGraph = graph.print(null, true);
    assert.equal(typeof printedGraph, 'string');
    assert.ok(printedGraph.length > 0);
  });

  test('should iterate over pointers', () => {
    const graph = new Graph(grammar, stackedRules, rootId);
    const mockPointers = new Pointers(
      ...(
        [
          new RuleChar([65, 66, 67]),
          new RuleChar([68, 69, 70]),
          new RuleChar([71, 72, 73]),
          new RuleChar([74, 75, 76]),
          new RuleCharExclude([1]),
          new RuleEnd(),
        ] as UnresolvedRule[]
      ).map((rule, index) => new GraphPointer(new GraphNode(rule, { ...META, stepId: index }))),
    );

    const result = [...graph.iterateOverPointers(mockPointers)];
    assert.equal(result.length, 6);
    for (const [rule, pointers] of result) {
      assert.ok(isRule(rule));
      assert.ok(pointers.length >= 1);
      for (const pointer of pointers) {
        assert.ok([...mockPointers].includes(pointer));
      }
    }
  });

  test('should raise error on reference rule', () => {
    const graph = new Graph(grammar, stackedRules, rootId);
    const mockPointers = [new GraphPointer(new GraphNode(new RuleRef(0), META))];

    assert.throws(
      () => [...graph.iterateOverPointers(mockPointers)],
      /Encountered a reference rule in the graph/,
    );
  });
});
