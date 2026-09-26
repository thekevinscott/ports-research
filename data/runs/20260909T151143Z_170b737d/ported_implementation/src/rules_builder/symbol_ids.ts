import { KeyError } from "../utils/python_compat.ts";

export class SymbolIds {
  private __map__: Map<string, number>;
  private __pos__: Map<string, number>;
  private __reverse_map__: Map<number, string>;

  constructor() {
    this.__map__ = new Map();
    this.__pos__ = new Map();
    this.__reverse_map__ = new Map();
  }

  items(): IterableIterator<[string, number]> {
    return this.__map__.entries();
  }

  [Symbol.iterator](): IterableIterator<[string, number]> {
    return this.__map__.entries();
  }

  get length(): number {
    return this.__map__.size;
  }

  /** Equivalent of `symbol_ids[key]`; raises like Python's `dict.__getitem__`. */
  getItem(key: string): number {
    const value = this.__map__.get(key);
    if (value === undefined) {
      throw new KeyError(key);
    }
    return value;
  }

  set(key: string, value: number, pos: number): void {
    this.__map__.set(key, value);
    this.__reverse_map__.set(value, key);
    this.__pos__.set(key, pos);
  }

  has(key: string): boolean {
    return this.__map__.has(key);
  }

  reverse_get(key: number): string {
    const val = this.__reverse_map__.get(key);
    if (val === undefined) {
      throw new Error(`SymbolIds does not contain value: ${key}`);
    }
    return val;
  }

  get_pos(key: string): number {
    const val = this.__pos__.get(key);
    if (val === undefined) {
      throw new Error(`SymbolIds does not contain key: ${key}`);
    }
    return val;
  }
}
