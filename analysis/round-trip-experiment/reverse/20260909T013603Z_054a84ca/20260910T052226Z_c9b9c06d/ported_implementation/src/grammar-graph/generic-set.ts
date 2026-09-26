/** An insertion-ordered set keyed by a derived key rather than by identity. */
export class GenericSet<T, K> {
  private getKey: (el: T) => K;
  private keys = new Map<K, T>();
  private set = new Set<T>();

  constructor(getKey: (el: T) => K) {
    this.getKey = getKey;
  }

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

  *[Symbol.iterator](): IterableIterator<T> {
    yield* [...this.set];
  }

  get size(): number {
    return this.set.size;
  }
}
