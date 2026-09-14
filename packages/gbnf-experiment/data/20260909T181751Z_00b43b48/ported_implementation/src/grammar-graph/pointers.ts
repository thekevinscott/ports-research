import type { GraphPointer, GraphPointerKey } from './graph-pointer.js';

export class Pointers {
  #pointers: Map<GraphPointerKey, GraphPointer>;

  constructor(...pointers: GraphPointer[]) {
    this.#pointers = new Map();
    for (const pointer of pointers) {
      this.add(pointer);
    }
  }

  add(pointer: GraphPointer): void {
    this.#pointers.set(pointer.id, pointer);
  }

  *[Symbol.iterator](): IterableIterator<GraphPointer> {
    yield* this.#pointers.values();
  }

  get size(): number {
    return this.#pointers.size;
  }
}
