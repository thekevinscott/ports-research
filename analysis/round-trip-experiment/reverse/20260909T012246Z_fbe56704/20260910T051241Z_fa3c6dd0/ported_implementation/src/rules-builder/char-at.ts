/** Indexing a string out of bounds yields undefined; here it yields ''. */
export const charAt = (src: string, pos: number): string =>
  pos >= 0 && pos < src.length ? src[pos] : '';
