/**
 * Raised when the parser hits an internal invariant violation.
 */
export class GBNFError extends Error {
  override name = 'GBNFError';
}
