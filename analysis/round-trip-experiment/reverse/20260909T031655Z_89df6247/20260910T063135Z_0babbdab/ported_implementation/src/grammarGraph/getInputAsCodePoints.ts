export type CodePointSource = string | number | number[];

export const getInputAsCodePoints = (src: CodePointSource): number[] => {
  if (typeof src !== 'string') {
    return Array.isArray(src) ? [...src] : [src];
  }

  return [...src].map((char) => char.codePointAt(0) as number);
};
