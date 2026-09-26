import { beforeEach, describe, expect, test, vi } from 'vitest';
import { getParentStackId } from '../../../src/grammar-graph/get-parent-stack-id.ts';
import { RuleChar } from '../../../src/grammar-graph/grammar-graph-types.ts';
import type { GraphNode } from '../../../src/grammar-graph/graph-node.ts';
import type { GraphPointer } from '../../../src/grammar-graph/graph-pointer.ts';
import { printGraphNode, printGraphPointer } from '../../../src/grammar-graph/print.ts';
import { RuleRef } from '../../../src/grammar-graph/rule-ref.ts';

vi.mock('../../../src/grammar-graph/get-parent-stack-id.ts', () => ({
  getParentStackId: vi.fn(() => ''),
}));

const COLORS: Record<string, string> = {
  '\x1b[34m': 'BLUE',
  '\x1b[36m': 'CYAN',
  '\x1b[32m': 'GREEN',
  '\x1b[31m': 'RED',
  '\x1b[90m': 'GRAY',
  '\x1b[33m': 'YELLOW',
};

const mockColorize = (text: string | number, color: string): string => {
  if (!Object.hasOwn(COLORS, color)) {
    throw new Error(`Invalid color: ${color}`);
  }
  return `[${COLORS[color]}]:${text}`;
};

const createMockNode = (
  id: number,
  rule: unknown,
  next: GraphNode | null = null,
): GraphNode => ({
  id: String(id),
  rule,
  next,
  meta: { stackId: id, pathId: id, stepId: id },
  print: () => `Node(${id})`,
} as unknown as GraphNode);

const createMockGraphPointer = (node: GraphNode): GraphPointer => ({
  node,
  parent: null,
  print: () => `Pointer to ${node.id}`,
} as unknown as GraphPointer);

beforeEach(() => {
  vi.mocked(getParentStackId).mockReturnValue('');
});

describe('print', () => {
  describe('print_graph_pointer', () => {
    test('it prints graph pointer details correctly', () => {
      const mockNode = createMockNode(1, new RuleRef(100));
      const mockPointer = createMockGraphPointer(mockNode);
      vi.mocked(getParentStackId).mockReturnValue('foo');
      const result = printGraphPointer(mockPointer)({
        colorize: mockColorize,
        pointers: undefined,
        show_position: false,
      });
      expect(result).toBe('[RED]:*foo');
    });
  });

  describe('print_graph_node', () => {
    test('it prints graph node with a character rule', () => {
      const mockNode = createMockNode(1, new RuleChar([65]));
      const result = printGraphNode(mockNode)({
        colorize: mockColorize,
        show_position: false,
        pointers: undefined,
      });
      expect(result).toBe('[GRAY]:[[YELLOW]:A[GRAY]:]');
    });

    test('it prints graph node with a rule reference', () => {
      const mockNode = createMockNode(1, new RuleRef(200));
      const result = printGraphNode(mockNode)({
        colorize: mockColorize,
        show_position: true,
        pointers: undefined,
      });
      expect(result).toBe('[BLUE]:{[GRAY]:1[BLUE]:}[GRAY]:Ref([GREEN]:200[GRAY]:)');
    });
  });
});
