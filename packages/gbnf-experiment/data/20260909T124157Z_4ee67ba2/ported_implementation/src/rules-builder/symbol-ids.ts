export class SymbolIds {
  #map: Map<string, number>;
  #pos: Map<string, number>;
  #reverseMap: Map<number, string>;

  constructor() {
    this.#map = new Map();
    this.#pos = new Map();
    this.#reverseMap = new Map();
  }

  *items(): IterableIterator<[string, number]> {
    yield* this.#map.entries();
  }

  [Symbol.iterator](): IterableIterator<[string, number]> {
    return this.#map.entries();
  }

  get size(): number {
    return this.#map.size;
  }

  /** Mirrors `symbol_ids[key]`; returns undefined when the key is absent. */
  get(key: string): number | undefined {
    return this.#map.get(key);
  }

  set(key: string, value: number, pos: number): void {
    this.#map.set(key, value);
    this.#reverseMap.set(value, key);
    this.#pos.set(key, pos);
  }

  has(key: string): boolean {
    return this.#map.has(key);
  }

  reverseGet(key: number): string {
    const val = this.#reverseMap.get(key);
    if (val === undefined) {
      throw new Error(`SymbolIds does not contain value: ${key}`);
    }
    return val;
  }

  getPos(key: string): number {
    const val = this.#pos.get(key);
    if (val === undefined) {
      throw new Error(`SymbolIds does not contain key: ${key}`);
    }
    return val;
  }
}
