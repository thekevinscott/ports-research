/** A set that dedupes by a derived key while preserving insertion order. */
export class GenericSet<T, K> {
  getKey: (el: T) => K;
  private _keys = new Map<K, T>();

  constructor(getKey: (el: T) => K) {
    this.getKey = getKey;
  }

  add(el: T): void {
    const key = this.getKey(el);
    if (!this._keys.has(key)) {
      this._keys.set(key, el);
    }
  }

  delete(el: T): void {
    const key = this.getKey(el);
    if (!this._keys.has(key)) {
      throw new Error('Could not get ref');
    }
    this._keys.delete(key);
  }

  has(el: T): boolean {
    const key = this.getKey(el);
    return this._keys.has(key) && this._keys.get(key) === el;
  }

  get(el: T): T | undefined {
    return this._keys.get(this.getKey(el));
  }

  *[Symbol.iterator](): IterableIterator<T> {
    yield* [...this._keys.values()];
  }

  get size(): number {
    return this._keys.size;
  }
}
