import assert from 'node:assert/strict';
import { describe, it } from 'node:test';

import { Graph } from '../src/grammarGraph/graph.ts';
import {
  RuleChar,
  RuleCharExclude,
  RuleEnd,
} from '../src/grammarGraph/grammarGraphTypes.ts';
import type { UnresolvedRule } from '../src/grammarGraph/grammarGraphTypes.ts';
import { GraphNode } from '../src/grammarGraph/graphNode.ts';
import { GraphPointer } from '../src/grammarGraph/graphPointer.ts';
import { Pointers } from '../src/grammarGraph/pointers.ts';
import { RuleRef } from '../src/grammarGraph/ruleRef.ts';
import { isRule } from '../src/grammarGraph/typeGuards.ts';

describe('Graph', () => {
  const grammar = 'example-grammar';
  const stackedRules: UnresolvedRule[][][] = [
    [[new RuleChar([65, 66, 67])], [new RuleChar([68, 69, 70])]],
    [[new RuleChar([71, 72, 73])], [new RuleChar([74, 75, 76])]],
  ];
  const rootId = 0;

  it('creates a Graph instance', () => {
    const graph = new Graph(grammar, stackedRules, rootId);
    assert.ok(graph instanceof Graph);
    assert.equal(graph.grammar, grammar);
  });

  it('gets the root node', () => {
    const graph = new Graph(grammar, stackedRules, rootId);
    const rootNode = graph.getRootNode(rootId);
    assert.ok(rootNode instanceof Map);
    assert.equal(rootNode.size, 2);
  });

  it('throws when asked for a root node that does not exist', () => {
    const graph = new Graph(grammar, stackedRules, rootId);
    assert.throws(() => graph.getRootNode(99), /Root node not found for value: 99/u);
  });

  it('gets the initial pointers', () => {
    const graph = new Graph(grammar, stackedRules, rootId);
    const pointers = graph.getInitialPointers();
    assert.equal(pointers.size, 2);
    for (const pointer of pointers) {
      assert.ok(isRule(pointer.rule));
    }
  });

  it('prints the graph', () => {
    const graph = new Graph(grammar, stackedRules, rootId);
    const printedGraph = graph.print(null, true);
    assert.equal(typeof printedGraph, 'string');
    assert.ok(printedGraph.length > 0);
  });

  it('iterates over pointers', () => {
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
      ...rules.map(
        (rule, idx) => new GraphPointer(new GraphNode(rule, { stackId: idx, pathId: 0, stepId: 0 })),
      ),
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

  it('raises an error on a reference rule', () => {
    const graph = new Graph(grammar, stackedRules, rootId);
    const mockPointers = [
      new GraphPointer(new GraphNode(new RuleRef(0), { stackId: 0, pathId: 0, stepId: 0 })),
    ];
    assert.throws(
      () => [...graph.iterateOverPointers(mockPointers)],
      /Encountered a reference rule in the graph/u,
    );
  });

  it('rejects non-string input in add', () => {
    const graph = new Graph(grammar, stackedRules, rootId);
    assert.throws(
      () => graph.add(65 as unknown as string),
      /src must be a string in graph\.add/u,
    );
  });
});
