import type { GraphPointer, GraphPointerKey } from './graph-pointer.js';

export class Pointers {
  #pointers = new Map<GraphPointerKey, GraphPointer>();

  constructor(...pointers: GraphPointer[]) {
    for (const pointer of pointers) {
      this.add(pointer);
    }
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
