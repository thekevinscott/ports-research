import assert from "node:assert/strict";
import { describe, it } from "node:test";

import { RuleChar } from "../../src/grammar_graph/grammar_graph_types.ts";
import type {
  PrintableNode,
  PrintablePointer,
  PrintOpts,
  UnresolvedRule,
} from "../../src/grammar_graph/grammar_graph_types.ts";
import { GraphNode } from "../../src/grammar_graph/graph_node.ts";
import { GraphPointer } from "../../src/grammar_graph/graph_pointer.ts";
import { print_graph_node, print_graph_pointer } from "../../src/grammar_graph/print.ts";
import { RuleRef } from "../../src/grammar_graph/rule_ref.ts";

const COLORS: Record<string, string> = {
  "\x1b[34m": "BLUE",
  "\x1b[36m": "CYAN",
  "\x1b[32m": "GREEN",
  "\x1b[31m": "RED",
  "\x1b[90m": "GRAY",
  "\x1b[33m": "YELLOW",
};

const mock_colorize = (text: string | number, color: string): string => {
  if (!(color in COLORS)) {
    throw new Error(`Invalid color: ${color}`);
  }
  return `[${COLORS[color]}]:${text}`;
};

const create_mock_node = (
  id: string,
  rule: UnresolvedRule,
  next: PrintableNode | null = null,
): PrintableNode => ({
  id,
  rule,
  next,
  print: () => `Node(${id})`,
});

const create_mock_graph_pointer = (node: PrintableNode): PrintablePointer => ({
  node,
  print: () => `Pointer to ${node.id}`,
});

describe("print_graph_pointer", () => {
  it("prints graph pointer details", () => {
    // A pointer whose parent chain is 1,1,1 renders that id between the marker.
    const parent = new GraphPointer(
      new GraphNode(new RuleChar([97]), { stackId: 1, pathId: 1, stepId: 1 }),
    );
    const pointer = new GraphPointer(
      new GraphNode(new RuleChar([98]), { stackId: 2, pathId: 2, stepId: 2 }),
      parent,
    );

    const result = print_graph_pointer(pointer)({
      colorize: mock_colorize,
      pointers: [],
      show_position: false,
    });

    assert.equal(result, "[RED]:*[RED]:1,1,1");
  });

  it("prints just the marker when there is no parent", () => {
    const pointer = new GraphPointer(
      new GraphNode(new RuleChar([97]), { stackId: 1, pathId: 1, stepId: 1 }),
    );
    assert.equal(
      print_graph_pointer(pointer)({ colorize: mock_colorize }),
      "[RED]:*",
    );
  });
});

describe("print_graph_node", () => {
  it("prints a graph node with a character rule", () => {
    const mock_node = create_mock_node("1", new RuleChar([65]));
    const result = print_graph_node(mock_node)({
      colorize: mock_colorize,
      show_position: false,
      pointers: [],
    });
    assert.equal(result, "[GRAY]:[[YELLOW]:A[GRAY]:]");
  });

  it("prints a graph node with a rule reference", () => {
    const mock_node = create_mock_node("1", new RuleRef(200));
    const result = print_graph_node(mock_node)({
      colorize: mock_colorize,
      show_position: true,
      pointers: [],
    });
    assert.equal(result, "[BLUE]:{[GRAY]:1[BLUE]:}[GRAY]:Ref([GREEN]:200[GRAY]:)");
  });

  it("renders ranges and newlines", () => {
    const mock_node = create_mock_node("1", new RuleChar([[97, 122], 10]));
    const result = print_graph_node(mock_node)({
      colorize: mock_colorize,
      show_position: false,
    });
    assert.equal(result, "[GRAY]:[[YELLOW]:[YELLOW]:a[YELLOW]:z\\n[GRAY]:]");
  });

  it("appends the next node after an arrow", () => {
    const next = create_mock_node("2", new RuleChar([66]));
    const mock_node = create_mock_node("1", new RuleChar([65]), next);
    const opts: PrintOpts = { colorize: mock_colorize, show_position: false };
    assert.equal(
      print_graph_node(mock_node)(opts),
      "[GRAY]:[[YELLOW]:A[GRAY]:][GRAY]:-> Node(2)",
    );
  });

  it("annotates pointers that sit on the node", () => {
    const mock_node = create_mock_node("1", new RuleChar([65]));
    const result = print_graph_node(mock_node)({
      colorize: mock_colorize,
      show_position: false,
      pointers: [create_mock_graph_pointer(mock_node)],
    });
    assert.equal(
      result,
      "[GRAY]:[[YELLOW]:A[GRAY]:][GRAY]:[[YELLOW]:Pointer to 1[GRAY]:]",
    );
  });
});
