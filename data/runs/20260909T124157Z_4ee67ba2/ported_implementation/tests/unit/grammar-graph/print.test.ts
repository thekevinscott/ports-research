import assert from 'node:assert/strict';
import { describe, test } from 'node:test';
import { RuleChar } from '../../../src/grammar-graph/grammar-graph-types.ts';
import {
  printGraphNode,
  printGraphPointer,
  type PrintableNode,
} from '../../../src/grammar-graph/print.ts';
import { RuleRef } from '../../../src/grammar-graph/rule-ref.ts';

const COLORS: Record<string, string> = {
  '\x1b[34m': 'BLUE',
  '\x1b[36m': 'CYAN',
  '\x1b[32m': 'GREEN',
  '\x1b[31m': 'RED',
  '\x1b[90m': 'GRAY',
  '\x1b[33m': 'YELLOW',
};

const mockColorize = (text: string | number, color: string): string => {
  if (!(color in COLORS)) {
    throw new Error(`Invalid color: ${color}`);
  }
  return `[${COLORS[color]}]:${text}`;
};

const createMockNode = (id: number, rule: unknown, next: PrintableNode | null = null) => ({
  id,
  rule,
  next,
  print: (_opts: unknown) => `Node(${id})`,
});

const createMockGraphPointer = (node: ReturnType<typeof createMockNode>) => ({
  node,
  parent: null,
  print: (_opts: unknown) => `Pointer to ${node.id}`,
});

describe('print', () => {
  describe('print graph pointer', () => {
    // The reference test patches get_parent_stack_id to return "foo"; the real
    // function returns "" for a parentless pointer, which is what is asserted here.
    test('it prints graph pointer details correctly', () => {
      const mockNode = createMockNode(1, new RuleRef(100));
      const mockPointer = createMockGraphPointer(mockNode);
      const result = printGraphPointer(mockPointer as never)({
        colorize: mockColorize,
        show_position: false,
      });
      assert.equal(result, '[RED]:*');
    });
  });

  describe('print graph node', () => {
    test('it prints graph node with a character rule', () => {
      const mockNode = createMockNode(1, new RuleChar([65]));
      const result = printGraphNode(mockNode as never)({
        colorize: mockColorize,
        show_position: false,
      });
      assert.equal(result, '[GRAY]:[[YELLOW]:A[GRAY]:]');
    });

    test('it prints graph node with a rule reference', () => {
      const mockNode = createMockNode(1, new RuleRef(200));
      const result = printGraphNode(mockNode as never)({
        colorize: mockColorize,
        show_position: true,
      });
      assert.equal(result, '[BLUE]:{[GRAY]:1[BLUE]:}[GRAY]:Ref([GREEN]:200[GRAY]:)');
    });
  });
});
