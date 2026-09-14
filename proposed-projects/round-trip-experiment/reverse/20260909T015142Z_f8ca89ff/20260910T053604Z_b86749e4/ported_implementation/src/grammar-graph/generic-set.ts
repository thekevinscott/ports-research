/**
 * A set that dedupes on a derived key while preserving object identity.
 *
 * The `Map` holds the canonical element for each key; the `Set` answers
 * membership by reference.
 */
export class GenericSet<T, K> {
  private keys = new Map<K, T>();
  private set = new Set<T>();

  constructor(public getKey: (el: T) => K) {}

  public add(el: T): void {
    const key = this.getKey(el);
    if (!this.keys.has(key)) {
      this.keys.set(key, el);
      this.set.add(el);
    }
  }

  public delete(el: T): void {
    const key = this.getKey(el);
    const ref = this.keys.get(key);
    if (ref === undefined) {
      throw new Error('Could not get ref');
    }
    this.keys.delete(key);
    this.set.delete(ref);
  }

  public has(el: T): boolean {
    return this.set.has(el);
  }

  public get(el: T): T | undefined {
    return this.keys.get(this.getKey(el));
  }

  public [Symbol.iterator](): IterableIterator<T> {
    return this.set.values();
  }

  public get size(): number {
    return this.set.size;
  }
}
