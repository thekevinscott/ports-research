/** A set of elements deduplicated by a derived key, preserving insertion order. */
export class GenericSet<T, K> {
  getKey: (el: T) => K;
  #keys = new Map<K, T>();

  constructor(getKey: (el: T) => K) {
    this.getKey = getKey;
  }

  add(el: T): void {
    const key = this.getKey(el);
    if (!this.#keys.has(key)) {
      this.#keys.set(key, el);
    }
  }

  delete(el: T): void {
    const key = this.getKey(el);
    if (!this.#keys.has(key)) {
      throw new Error('Could not get ref');
    }
    this.#keys.delete(key);
  }

  has(el: T): boolean {
    for (const existing of this.#keys.values()) {
      if (existing === el) {
        return true;
      }
    }
    return false;
  }

  get(el: T): T | undefined {
    return this.#keys.get(this.getKey(el));
  }

  *[Symbol.iterator](): Generator<T> {
    yield* [...this.#keys.values()];
  }

  get size(): number {
    return this.#keys.size;
  }
}
