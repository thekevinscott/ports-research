import type { GraphPointer } from './graph-pointer.ts';

export class Pointers {
  #pointers: Map<string, GraphPointer>;

  constructor(...pointers: GraphPointer[]) {
    this.#pointers = new Map();
    for (const pointer of pointers) {
      this.add(pointer);
    }
  }

  add(pointer: GraphPointer): void {
    this.#pointers.set(pointer.id, pointer);
  }

  [Symbol.iterator](): IterableIterator<GraphPointer> {
    return this.#pointers.values();
  }

  get size(): number {
    return this.#pointers.size;
  }

  toString(): string {
    return `<Pointers ${[...this].map(p => String(p.node.rule)).join(', ')}>`;
  }
}
