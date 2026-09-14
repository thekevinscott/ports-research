import type { UserConfig } from 'vitest/config';

// Declared as a plain object rather than via `defineConfig` so the config can be
// loaded without `vitest` being resolvable from this directory (it may be
// installed globally).
const config: UserConfig = {
  test: {
    include: ['tests/**/*.test.ts', 'src/**/*.test.ts'],
    environment: 'node',
  },
};

export default config;
