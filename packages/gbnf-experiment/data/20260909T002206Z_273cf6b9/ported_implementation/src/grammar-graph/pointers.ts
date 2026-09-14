import type { GraphPointer } from './graph-pointer.ts';

export class Pointers implements Iterable<GraphPointer> {
  #pointers = new Map<string, GraphPointer>();

  constructor(...pointers: GraphPointer[]) {
    for (const pointer of pointers) {
      this.add(pointer);
    }
  }

  toString(): string {
    return `<Pointers ${[...this].map(p => String(p.node.rule)).join(', ')}>`;
  }

  add(pointer: GraphPointer): void {
    this.#pointers.set(pointer.id, pointer);
  }

  *[Symbol.iterator](): Generator<GraphPointer> {
    yield* this.#pointers.values();
  }

  get size(): number {
    return this.#pointers.size;
  }
}
