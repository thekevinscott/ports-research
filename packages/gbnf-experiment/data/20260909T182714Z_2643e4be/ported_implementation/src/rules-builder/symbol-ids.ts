import { KeyError, ValueError } from "../utils/errors/python-errors.js";

export class SymbolIds {
  #map: Map<string, number> = new Map();
  #pos: Map<string, number> = new Map();
  #reverseMap: Map<number, string> = new Map();

  items(): IterableIterator<[string, number]> {
    return this.#map.entries();
  }

  [Symbol.iterator](): IterableIterator<[string, number]> {
    return this.#map.entries();
  }

  get size(): number {
    return this.#map.size;
  }

  // Equivalent of Python's `symbol_ids[key]`, which raises on a missing key.
  get(key: string): number {
    const value = this.#map.get(key);
    if (value === undefined) {
      throw new KeyError(key);
    }
    return value;
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
      throw new ValueError(`SymbolIds does not contain value: ${key}`);
    }
    return val;
  }

  getPos(key: string): number {
    const val = this.#pos.get(key);
    if (val === undefined) {
      throw new ValueError(`SymbolIds does not contain key: ${key}`);
    }
    return val;
  }
}
