// The alias is absolute because vitest rejects relative ones.
export default {
  test: {
    include: [
      'tests/**/*.test.ts',
    ],
    watchExclude: [
      'tmp/**/*',
    ],
    globals: true,
  },
  resolve: {
    alias: {
      two_number_adder: '/workspace/ported_implementation/src/index.ts',
    },
  },
};
