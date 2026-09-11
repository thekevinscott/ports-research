import assert from "node:assert/strict";
import { describe, it } from "node:test";

import { codePointLength, toCodePoints } from "../src/utils/code-points.ts";
import { isPointInRange } from "../src/utils/is-point-in-range.ts";
import { validateNonEmpty } from "../src/utils/validate-non-empty.ts";

describe("isPointInRange", () => {
  const cases: [number, [number, number], boolean][] = [
    [96, [97, 122], false],
    [97, [97, 122], true],
    [98, [97, 122], true],
    [122, [97, 122], true],
    [123, [97, 122], false],
  ];

  for (const [point, range, expectation] of cases) {
    it(`checks if ${point} is in [${range}]`, () => {
      assert.equal(isPointInRange(point, range), expectation);
    });
  }

  it("throws if the point is not an integer", () => {
    assert.throws(() => isPointInRange(1.5, [0, 10]), {
      message: "point must be an integer",
    });
  });
});

describe("validateNonEmpty", () => {
  it("returns the value when non-empty", () => {
    assert.deepEqual(validateNonEmpty([1, 2]), [1, 2]);
  });

  it("throws when empty", () => {
    assert.throws(() => validateNonEmpty([]), { message: "Value cannot be empty." });
  });
});

describe("code points", () => {
  it("splits astral characters as single code points", () => {
    assert.deepEqual(toCodePoints("a💩b"), ["a", "💩", "b"]);
    assert.equal(codePointLength("a💩b"), 3);
  });
});
