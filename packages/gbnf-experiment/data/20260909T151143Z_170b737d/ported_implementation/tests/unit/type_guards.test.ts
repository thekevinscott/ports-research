import assert from "node:assert/strict";
import { describe, it } from "node:test";

import {
  RuleChar,
  RuleCharExclude,
  RuleEnd,
} from "../../src/grammar_graph/grammar_graph_types.ts";
import { GraphNode } from "../../src/grammar_graph/graph_node.ts";
import { GraphPointer } from "../../src/grammar_graph/graph_pointer.ts";
import { RuleRef } from "../../src/grammar_graph/rule_ref.ts";
import {
  is_graph_pointer_rule_char,
  is_graph_pointer_rule_char_exclude,
  is_graph_pointer_rule_end,
  is_graph_pointer_rule_ref,
  is_range,
  is_rule,
  is_rule_char,
  is_rule_char_exclude,
  is_rule_end,
  is_rule_ref,
} from "../../src/grammar_graph/type_guards.ts";

const meta = { stackId: 1, pathId: 2, stepId: 3 };
const pointer_for = (rule: RuleChar | RuleCharExclude | RuleEnd | RuleRef): GraphPointer =>
  new GraphPointer(new GraphNode(rule, meta));

describe("is_graph_pointer_rule_ref", () => {
  it("returns true for a ref pointer", () => {
    assert.ok(is_graph_pointer_rule_ref(pointer_for(new RuleRef(1))));
  });

  it("returns false otherwise", () => {
    assert.ok(!is_graph_pointer_rule_ref(pointer_for(new RuleEnd())));
  });
});

describe("is_graph_pointer_rule_end", () => {
  it("returns false for a ref pointer", () => {
    assert.ok(!is_graph_pointer_rule_end(pointer_for(new RuleRef(1))));
  });

  it("returns true for an end pointer", () => {
    assert.ok(is_graph_pointer_rule_end(pointer_for(new RuleEnd())));
  });
});

describe("is_graph_pointer_rule_char", () => {
  it("returns true for a char pointer", () => {
    assert.ok(is_graph_pointer_rule_char(pointer_for(new RuleChar([97]))));
  });

  it("returns false otherwise", () => {
    assert.ok(!is_graph_pointer_rule_char(pointer_for(new RuleEnd())));
  });
});

describe("is_graph_pointer_rule_char_exclude", () => {
  it("returns true for a char-exclude pointer", () => {
    assert.ok(is_graph_pointer_rule_char_exclude(pointer_for(new RuleCharExclude([97]))));
  });

  it("returns false for a char pointer", () => {
    assert.ok(!is_graph_pointer_rule_char_exclude(pointer_for(new RuleChar([97]))));
  });
});

describe("is_rule", () => {
  it("returns false for null and undefined", () => {
    assert.ok(!is_rule(null));
    assert.ok(!is_rule(undefined));
  });

  it("returns false for a non-rule", () => {
    assert.ok(!is_rule({ type: "invalid", value: [] }));
  });

  it("returns true for valid rule objects", () => {
    assert.ok(is_rule(new RuleChar([65, 66, 67])));
    assert.ok(is_rule(new RuleCharExclude([65])));
    assert.ok(is_rule(new RuleEnd()));
    assert.ok(is_rule(new RuleRef(1)));
  });
});

describe("is_rule_ref", () => {
  it("returns true for valid rule refs", () => {
    assert.ok(is_rule_ref(new RuleRef(1)));
  });

  it("returns false for invalid rule refs", () => {
    assert.ok(!is_rule_ref(new RuleChar([65])));
  });
});

describe("is_rule_end", () => {
  it("returns true for valid rule ends", () => {
    assert.ok(is_rule_end(new RuleEnd()));
  });

  it("returns false for invalid rule ends", () => {
    assert.ok(!is_rule_end(new RuleChar([65])));
  });
});

describe("is_rule_char", () => {
  it("returns true for valid rule chars", () => {
    assert.ok(is_rule_char(new RuleChar([65])));
  });

  it("returns false for a char-exclude rule", () => {
    assert.ok(!is_rule_char(new RuleCharExclude([65])));
  });
});

describe("is_rule_char_exclude", () => {
  it("returns true for valid char-exclude rules", () => {
    assert.ok(is_rule_char_exclude(new RuleCharExclude([65])));
  });

  it("returns false for a char rule", () => {
    assert.ok(!is_rule_char_exclude(new RuleChar([65])));
  });
});

describe("is_range", () => {
  it("returns true for valid ranges", () => {
    assert.ok(is_range([1, 10]));
  });

  it("returns false for invalid ranges", () => {
    for (const value of [[1], [1, 2, 3], 1, "a", null, undefined, [1, "a"], []]) {
      assert.ok(!is_range(value), JSON.stringify(value ?? null));
    }
  });
});
