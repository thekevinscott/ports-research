/** A set keyed by a derived key, preserving insertion order. */
export class GenericSet<T, K> {
  private getKey: (el: T) => K;
  private keys = new Map<K, T>();

  constructor(getKey: (el: T) => K) {
    this.getKey = getKey;
  }

  add(el: T): void {
    const key = this.getKey(el);
    if (!this.keys.has(key)) {
      this.keys.set(key, el);
    }
  }

  delete(el: T): void {
    const key = this.getKey(el);
    if (!this.keys.has(key)) {
      throw new Error('Could not get ref');
    }
    this.keys.delete(key);
  }

  has(el: T): boolean {
    const key = this.getKey(el);
    return this.keys.has(key) && this.keys.get(key) === el;
  }

  get(el: T): T | undefined {
    return this.keys.get(this.getKey(el));
  }

  *[Symbol.iterator](): IterableIterator<T> {
    // iterate over a snapshot, mirroring the reference's separate Set
    yield* [...this.keys.values()];
  }

  get size(): number {
    return this.keys.size;
  }
}
