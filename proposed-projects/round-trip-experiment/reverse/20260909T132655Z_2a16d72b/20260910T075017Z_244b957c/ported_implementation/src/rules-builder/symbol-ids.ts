export class SymbolIds {
  // we don't need to delete, just preserve relationships
  private _map = new Map<string, number>();
  private _pos = new Map<string, number>();
  private _reverseMap = new Map<number, string>();

  get size(): number {
    return this._map.size;
  }

  keys(): IterableIterator<string> {
    return this._map.keys();
  }

  has(key: string): boolean {
    return this._map.has(key);
  }

  get(key: string): number {
    if (!this._map.has(key)) {
      throw new Error(`SymbolIds does not contain key: ${key}`);
    }
    return this._map.get(key) as number;
  }

  getOrUndefined(key: string): number | undefined {
    return this._map.get(key);
  }

  reverseGet(key: number): string {
    if (!this._reverseMap.has(key)) {
      throw new Error(`SymbolIds does not contain value: ${key}`);
    }
    return this._reverseMap.get(key) as string;
  }

  getPos(key: string): number {
    if (!this._pos.has(key)) {
      throw new Error(`SymbolIds does not contain key: ${key}`);
    }
    return this._pos.get(key) as number;
  }

  set(key: string, value: number, pos: number): void {
    this._map.set(key, value);
    this._pos.set(key, pos);
    this._reverseMap.set(value, key);
  }

  *[Symbol.iterator](): IterableIterator<[string, number]> {
    yield* [...this._map.entries()];
  }
}
