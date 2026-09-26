import assert from "node:assert/strict";
import { describe, it } from "node:test";

import { Color, colorize } from "../src/grammar-graph/colorize.ts";
import { getInputAsCodePoints } from "../src/grammar-graph/get-input-as-code-points.ts";
import { getParentStackId } from "../src/grammar-graph/get-parent-stack-id.ts";
import {
  getSerializedRuleKey,
  KEY_TRANSLATION,
} from "../src/grammar-graph/get-serialized-rule-key.ts";
import {
  RuleChar,
  RuleCharExclude,
  RuleEnd,
} from "../src/grammar-graph/grammar-graph-types.ts";
import { GraphNode } from "../src/grammar-graph/graph-node.ts";
import { GraphPointer } from "../src/grammar-graph/graph-pointer.ts";
import { Pointers } from "../src/grammar-graph/pointers.ts";
import { getChar, printGraphNode, printGraphPointer } from "../src/grammar-graph/print.ts";
import { RuleRef } from "../src/grammar-graph/rule-ref.ts";
import {
  isGraphPointerRuleChar,
  isGraphPointerRuleCharExclude,
  isGraphPointerRuleEnd,
  isGraphPointerRuleRef,
  isRange,
  isRule,
  isRuleChar,
  isRuleCharExclude,
  isRuleEnd,
  isRuleRef,
} from "../src/grammar-graph/type-guards.ts";

const meta = { stackId: 1, pathId: 2, stepId: 3 };

describe("colorize", () => {
  it("colorizes strings", () => {
    assert.equal(colorize("hello", Color.BLUE), "\x1b[34mhello");
    assert.equal(colorize("test", Color.CYAN), "\x1b[36mtest");
    assert.equal(colorize("example", Color.GREEN), "\x1b[32mexample");
  });

  it("colorizes numbers", () => {
    assert.equal(colorize(123, Color.RED), "\x1b[31m123");
    assert.equal(colorize(456, Color.GRAY), "\x1b[90m456");
    assert.equal(colorize(789, Color.YELLOW), "\x1b[33m789");
  });
});

describe("getInputAsCodePoints", () => {
  it("returns code points for a string", () => {
    assert.deepEqual(getInputAsCodePoints("abc"), [97, 98, 99]);
  });

  it("returns code points for a number", () => {
    assert.deepEqual(getInputAsCodePoints(99), [99]);
  });

  it("returns code points for an array of numbers", () => {
    assert.deepEqual(getInputAsCodePoints([99, 100, 101]), [99, 100, 101]);
  });

  it("returns a single code point for astral characters", () => {
    assert.deepEqual(getInputAsCodePoints("💩"), [128169]);
  });
});

describe("RuleRef", () => {
  it("initializes with a given value", () => {
    assert.equal(new RuleRef(123).value, 123);
  });

  it("allows setting and getting nodes", () => {
    const ruleRef = new RuleRef(1);
    const mockNodes = new Set([new GraphNode(new RuleEnd(), meta)]);
    ruleRef.nodes = mockNodes;
    assert.equal(ruleRef.nodes, mockNodes);
  });

  it("throws an error if getting nodes before setting them", () => {
    assert.throws(() => new RuleRef(123).nodes, { message: "Nodes are not set" });
  });
});

describe("getSerializedRuleKey", () => {
  it("returns the type for end rules", () => {
    assert.equal(getSerializedRuleKey(new RuleEnd()), `${KEY_TRANSLATION.RuleEnd}`);
  });

  it("returns the type and value for character rules", () => {
    assert.equal(
      getSerializedRuleKey(new RuleChar([97])),
      `${KEY_TRANSLATION.RuleChar}-[97]`,
    );
  });

  it("returns the type and value for character exclude rules", () => {
    assert.equal(
      getSerializedRuleKey(new RuleCharExclude([97])),
      `${KEY_TRANSLATION.RuleCharExclude}-[97]`,
    );
  });

  it("returns the ref type with value for reference rules", () => {
    assert.equal(getSerializedRuleKey(new RuleRef(99)), "3-99");
  });

  it("distinguishes ranges from single code points", () => {
    assert.notEqual(
      getSerializedRuleKey(new RuleChar([[97, 122]])),
      getSerializedRuleKey(new RuleChar([97, 122])),
    );
  });

  it("throws an error for unknown rule types", () => {
    assert.throws(
      () => getSerializedRuleKey({ type: "UNKNOWN", value: "something" } as never),
      /Unknown rule type/,
    );
  });
});

describe("GraphNode", () => {
  it("constructs with a rule and meta", () => {
    const rule = new RuleRef(1);
    const node = new GraphNode(rule, meta);
    assert.equal(node.rule, rule);
    assert.deepEqual(node.meta, meta);
    assert.equal(node.next, null);
  });

  it("throws if meta is undefined", () => {
    assert.throws(() => new GraphNode(new RuleRef(1), undefined), {
      message: "Meta is undefined",
    });
  });

  it("calculates and caches its id", () => {
    const node = new GraphNode(new RuleRef(1), meta);
    assert.equal(node.id, "1,2,3");
    assert.equal(node.id, "1,2,3");
  });

  it("handles next node linkage", () => {
    const nextNode = new GraphNode(new RuleRef(43), meta);
    const node = new GraphNode(new RuleRef(1), meta, nextNode);
    assert.equal(node.next, nextNode);
  });

  it("delegates print to printGraphNode", () => {
    const node = new GraphNode(new RuleChar([65]), meta);
    assert.equal(
      node.print({ colorize: (s) => `${s}`, showPosition: false }),
      "[A]",
    );
  });
});

describe("GraphPointer", () => {
  it("initializes with a node", () => {
    const node = new GraphNode(new RuleEnd(), meta);
    const pointer = new GraphPointer(node);
    assert.equal(pointer.node, node);
    assert.equal(pointer.id, "1,2,3");
    assert.equal(pointer.parent, null);
    assert.equal(pointer.valid, null);
  });

  it("raises an error if the node is undefined", () => {
    assert.throws(() => new GraphPointer(undefined as never), {
      message: "Node is undefined",
    });
  });

  it("initializes correctly with a node and a parent", () => {
    const parentPointer = new GraphPointer(new GraphNode(new RuleEnd(), meta));
    const childPointer = new GraphPointer(
      new GraphNode(new RuleChar([97]), { stackId: 4, pathId: 5, stepId: 6 }),
      parentPointer,
    );
    assert.equal(childPointer.parent, parentPointer);
    assert.equal(childPointer.id, "1,2,3-4,5,6");
  });

  describe("resolve", () => {
    it("yields a char rule", () => {
      const pointer = new GraphPointer(new GraphNode(new RuleChar([97]), meta));
      assert.deepEqual([...pointer.resolve()], [pointer]);
    });

    it("yields a char excluded rule", () => {
      const pointer = new GraphPointer(new GraphNode(new RuleCharExclude([97]), meta));
      assert.deepEqual([...pointer.resolve()], [pointer]);
    });

    it("yields an end rule without a parent", () => {
      const pointer = new GraphPointer(new GraphNode(new RuleEnd(), meta));
      assert.deepEqual([...pointer.resolve()], [pointer]);
    });

    it("resolves through a rule ref to the referenced nodes", () => {
      const referenced = new GraphNode(new RuleChar([97]), {
        stackId: 9,
        pathId: 9,
        stepId: 9,
      });
      const ruleRef = new RuleRef(9);
      ruleRef.nodes = new Set([referenced]);
      const pointer = new GraphPointer(new GraphNode(ruleRef, meta));
      const resolved = [...pointer.resolve()];
      assert.equal(resolved.length, 1);
      assert.equal(resolved[0].node, referenced);
      assert.equal(resolved[0].parent, pointer);
    });

    it("raises an error on unknown rule types", () => {
      const pointer = new GraphPointer(new GraphNode({ type: "UNKNOWN" } as never, meta));
      assert.throws(() => [...pointer.resolve()], /Unknown rule/);
    });
  });

  describe("fetchNext", () => {
    it("yields nothing when the pointer is not valid", () => {
      const pointer = new GraphPointer(new GraphNode(new RuleChar([97]), meta));
      assert.deepEqual([...pointer.fetchNext()], []);
    });

    it("yields the next node once the pointer is valid", () => {
      const next = new GraphNode(new RuleChar([98]), { stackId: 1, pathId: 2, stepId: 4 });
      const pointer = new GraphPointer(new GraphNode(new RuleChar([97]), meta, next));
      pointer.valid = true;
      const fetched = [...pointer.fetchNext()];
      assert.equal(fetched.length, 1);
      assert.equal(fetched[0].node, next);
    });

    it("yields nothing for a valid end rule without a parent", () => {
      const pointer = new GraphPointer(new GraphNode(new RuleEnd(), meta));
      pointer.valid = true;
      assert.deepEqual([...pointer.fetchNext()], []);
    });

    it("throws when there is no next node", () => {
      const pointer = new GraphPointer(new GraphNode(new RuleChar([97]), meta));
      pointer.valid = true;
      assert.throws(() => [...pointer.fetchNext()], /No next node/);
    });
  });
});

describe("Pointers", () => {
  it("de-duplicates pointers by id", () => {
    const node = new GraphNode(new RuleChar([97]), meta);
    const pointers = new Pointers(new GraphPointer(node), new GraphPointer(node));
    assert.equal(pointers.size, 1);
  });

  it("iterates over its pointers", () => {
    const first = new GraphPointer(new GraphNode(new RuleChar([97]), meta));
    const second = new GraphPointer(
      new GraphNode(new RuleChar([98]), { stackId: 2, pathId: 2, stepId: 2 }),
    );
    const pointers = new Pointers(first, second);
    assert.deepEqual([...pointers], [first, second]);
    assert.equal(pointers.size, 2);
  });
});

describe("type guards", () => {
  const pointerFor = (rule: RuleChar | RuleCharExclude | RuleEnd | RuleRef) =>
    new GraphPointer(new GraphNode(rule, meta));

  it("isGraphPointerRuleRef", () => {
    assert.ok(isGraphPointerRuleRef(pointerFor(new RuleRef(1))));
    assert.ok(!isGraphPointerRuleRef(pointerFor(new RuleEnd())));
  });

  it("isGraphPointerRuleEnd", () => {
    assert.ok(isGraphPointerRuleEnd(pointerFor(new RuleEnd())));
    assert.ok(!isGraphPointerRuleEnd(pointerFor(new RuleRef(1))));
  });

  it("isGraphPointerRuleChar", () => {
    assert.ok(isGraphPointerRuleChar(pointerFor(new RuleChar([97]))));
    assert.ok(!isGraphPointerRuleChar(pointerFor(new RuleEnd())));
  });

  it("isGraphPointerRuleCharExclude", () => {
    assert.ok(isGraphPointerRuleCharExclude(pointerFor(new RuleCharExclude([97]))));
    assert.ok(!isGraphPointerRuleCharExclude(pointerFor(new RuleChar([97]))));
  });

  it("isRule", () => {
    assert.ok(!isRule(null));
    assert.ok(!isRule({ type: "invalid", value: "invalid" }));
    assert.ok(isRule(new RuleChar([65])));
    assert.ok(isRule(new RuleChar([66, 67])));
    assert.ok(isRule(new RuleEnd()));
    assert.ok(isRule(new RuleRef(1)));
  });

  it("isRuleRef", () => {
    assert.ok(isRuleRef(new RuleRef(1)));
    assert.ok(!isRuleRef(new RuleChar([65])));
  });

  it("isRuleEnd", () => {
    assert.ok(isRuleEnd(new RuleEnd()));
    assert.ok(!isRuleEnd(new RuleChar([65])));
  });

  it("isRuleChar", () => {
    assert.ok(isRuleChar(new RuleChar([65])));
    assert.ok(!isRuleChar(new RuleCharExclude([65])));
  });

  it("isRuleCharExclude", () => {
    assert.ok(isRuleCharExclude(new RuleCharExclude([65])));
    assert.ok(!isRuleCharExclude(new RuleChar([65])));
  });

  it("isRange", () => {
    assert.ok(isRange([1, 1]));
    assert.ok(isRange([97, 122]));
    assert.ok(!isRange("10"));
    assert.ok(!isRange([1]));
    assert.ok(!isRange([1, 2, 3]));
    assert.ok(!isRange([1, "2"]));
    assert.ok(!isRange([1.5, 2]));
    assert.ok(!isRange(null));
  });
});

describe("getParentStackId", () => {
  const mockColorize = (text: string | number, color: string): string => {
    const name = Object.entries(Color).find(([, value]) => value === color)?.[0];
    return `[${name}]:${text}`;
  };
  const red = "[RED]:";
  const gray = "[GRAY]:";

  const createMockPointer = (
    stackId: number,
    pathId: number,
    stepId: number,
    parent: GraphPointer | null = null,
  ): GraphPointer =>
    new GraphPointer(new GraphNode(new RuleEnd(), { stackId, pathId, stepId }), parent);

  it("returns an empty string if there are no parents", () => {
    assert.equal(getParentStackId(createMockPointer(1, 1, 1), mockColorize), "");
  });

  it("returns a single parent id, colored correctly", () => {
    const parent = createMockPointer(1, 1, 1);
    const pointer = createMockPointer(2, 2, 2, parent);
    assert.equal(getParentStackId(pointer, mockColorize), `${red}1,1,1`);
  });

  it("returns multiple parent ids separated by colored arrows", () => {
    const grandParent = createMockPointer(0, 0, 0);
    const parent = createMockPointer(1, 1, 1, grandParent);
    const pointer = createMockPointer(2, 2, 2, parent);
    assert.equal(
      getParentStackId(pointer, mockColorize),
      `${red}1,1,1${gray}<-${red}0,0,0`,
    );
  });

  it("handles deep nesting of pointers", () => {
    const great = createMockPointer(0, 0, 0);
    const grandParent = createMockPointer(1, 1, 1, great);
    const parent = createMockPointer(2, 2, 2, grandParent);
    const pointer = createMockPointer(3, 3, 3, parent);
    assert.equal(
      getParentStackId(pointer, mockColorize),
      `${red}2,2,2${gray}<-${red}1,1,1${gray}<-${red}0,0,0`,
    );
  });
});

describe("print", () => {
  const mockColorize = (text: string | number, color: string): string => {
    const name = Object.entries(Color).find(([, value]) => value === color)?.[0];
    if (name === undefined) {
      throw new Error(`Invalid color: ${color}`);
    }
    return `[${name}]:${text}`;
  };

  it("prints graph pointer details correctly", () => {
    const node = new GraphNode(new RuleRef(1), meta);
    const pointer = new GraphPointer(node);
    assert.equal(
      printGraphPointer(pointer)({ colorize: mockColorize, showPosition: false }),
      "[RED]:*",
    );
  });

  it("prints a graph node with a character rule", () => {
    const node = new GraphNode(new RuleChar([65]), meta);
    assert.equal(
      printGraphNode(node)({ colorize: mockColorize, showPosition: false }),
      "[GRAY]:[[YELLOW]:A[GRAY]:]",
    );
  });

  it("prints a graph node with a rule reference", () => {
    const node = new GraphNode(new RuleRef(200), { stackId: 1, pathId: 1, stepId: 1 });
    assert.equal(
      printGraphNode(node)({ colorize: mockColorize, showPosition: true }),
      "[BLUE]:{[GRAY]:1,1,1[BLUE]:}[GRAY]:Ref([GREEN]:200[GRAY]:)",
    );
  });

  it("prints a graph node with an end rule", () => {
    const node = new GraphNode(new RuleEnd(), meta);
    assert.equal(
      printGraphNode(node)({ colorize: mockColorize, showPosition: false }),
      "[YELLOW]:RuleEnd",
    );
  });

  it("prints ranges", () => {
    const node = new GraphNode(new RuleChar([[97, 122]]), meta);
    assert.equal(
      printGraphNode(node)({ colorize: (s) => `${s}`, showPosition: false }),
      "[az]",
    );
  });

  it("accepts the reference implementation's show_position spelling", () => {
    const node = new GraphNode(new RuleChar([65]), meta);
    assert.equal(
      printGraphNode(node)({ colorize: (s) => `${s}`, show_position: true }),
      "{1,2,3}[A]",
    );
  });

  it("prints linked nodes and pointers", () => {
    const next = new GraphNode(new RuleEnd(), { stackId: 1, pathId: 2, stepId: 4 });
    const node = new GraphNode(new RuleChar([97]), meta, next);
    const pointers = new Pointers(new GraphPointer(node));
    assert.equal(
      printGraphNode(node)({ colorize: (s) => `${s}`, pointers, showPosition: false }),
      "[a][*]-> RuleEnd",
    );
  });

  it("escapes newlines", () => {
    assert.equal(getChar(10), "\\n");
    assert.equal(getChar(97), "a");
  });
});
