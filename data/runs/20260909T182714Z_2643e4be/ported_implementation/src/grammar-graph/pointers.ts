import type { GraphPointer } from "./graph-pointer.js";

export class Pointers {
  #pointers: Map<string, GraphPointer> = new Map();

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

  toString(): string {
    return `<Pointers [${[...this].map((p) => p.node.rule).join(", ")}]>`;
  }
}
