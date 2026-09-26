/** A set of elements deduplicated by a derived key, preserving insertion order. */
export class GenericSet<T, K> {
  private keys = new Map<K, T>();
  private set = new Set<T>();

  constructor(private getKey: (el: T) => K) {}

  add(el: T): void {
    const key = this.getKey(el);
    if (!this.keys.has(key)) {
      this.keys.set(key, el);
      this.set.add(el);
    }
  }

  delete(el: T): void {
    const key = this.getKey(el);
    const ref = this.keys.get(key);
    if (ref === undefined) {
      throw new Error('Could not get ref');
    }
    this.keys.delete(key);
    this.set.delete(ref);
  }

  has(el: T): boolean {
    return this.set.has(el);
  }

  get(el: T): T | undefined {
    return this.keys.get(this.getKey(el));
  }

  [Symbol.iterator](): IterableIterator<T> {
    return this.set.values();
  }

  get size(): number {
    return this.set.size;
  }
}
