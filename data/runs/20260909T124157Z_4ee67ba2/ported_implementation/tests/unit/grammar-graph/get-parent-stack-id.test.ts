import assert from 'node:assert/strict';
import { describe, test } from 'node:test';
import { Color } from '../../../src/grammar-graph/colorize.ts';
import { getParentStackId } from '../../../src/grammar-graph/get-parent-stack-id.ts';
import { RuleEnd } from '../../../src/grammar-graph/grammar-graph-types.ts';
import { GraphNode } from '../../../src/grammar-graph/graph-node.ts';
import { GraphPointer } from '../../../src/grammar-graph/graph-pointer.ts';

const s = (str: string): string => JSON.stringify(str);

const mockColorize = (text: string | number, color: string): string => `[${s(color)}]:${text}`;

const red = s(Color.RED);
const gray = s(Color.GRAY);

const createMockPointer = (
  stackId: number,
  pathId: number,
  stepId: number,
  parent: GraphPointer | null = null,
): GraphPointer =>
  new GraphPointer(new GraphNode(new RuleEnd(), { stackId, pathId, stepId }), parent);

describe('get parent stack id', () => {
  test('returns an empty string if no parents', () => {
    assert.equal(getParentStackId(createMockPointer(1, 1, 1), mockColorize), '');
  });

  test('returns a single parent id colored correctly', () => {
    const parentPointer = createMockPointer(1, 1, 1);
    const pointer = createMockPointer(2, 2, 2, parentPointer);
    assert.equal(getParentStackId(pointer, mockColorize), `[${red}]:1,1,1`);
  });

  test('returns multiple parent ids separated by colored arrows', () => {
    const grandparentPointer = createMockPointer(0, 0, 0);
    const parentPointer = createMockPointer(1, 1, 1, grandparentPointer);
    const pointer = createMockPointer(2, 2, 2, parentPointer);
    assert.equal(
      getParentStackId(pointer, mockColorize),
      `[${red}]:1,1,1[${gray}]:<-[${red}]:0,0,0`,
    );
  });

  test('handles deep nesting of pointers', () => {
    const greatGrandparentPointer = createMockPointer(0, 0, 0);
    const grandparentPointer = createMockPointer(1, 1, 1, greatGrandparentPointer);
    const parentPointer = createMockPointer(2, 2, 2, grandparentPointer);
    const pointer = createMockPointer(3, 3, 3, parentPointer);
    assert.equal(
      getParentStackId(pointer, mockColorize),
      `[${red}]:2,2,2[${gray}]:<-[${red}]:1,1,1[${gray}]:<-[${red}]:0,0,0`,
    );
  });
});
