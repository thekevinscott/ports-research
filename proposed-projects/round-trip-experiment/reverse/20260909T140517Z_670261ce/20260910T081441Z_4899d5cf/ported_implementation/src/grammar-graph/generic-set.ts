/**
 * A set that dedupes on a derived key while keeping identity semantics for
 * membership: `add` ignores an element whose key is already present, `has` asks
 * whether this very object is held, and `get` returns whichever object won the
 * key.
 */
export class GenericSet<T, K> {
  private readonly getKey: (el: T) => K;
  private readonly keys = new Map<K, T>();
  private readonly set = new Set<T>();

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
