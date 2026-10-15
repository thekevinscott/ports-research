# 2026-10-15T03:20Z — Dockerfiles replace the sandbox sentences; image runs reference suites unmodified

Kevin on the three sandbox sentences from the 02:58Z entry: "a keen observer could point out that the prompt is biasing the model. But information about the environment is valid. This is why I suggested providing the docker file." Decision: both Dockerfiles (botbox's agent image, then port_codebase's) go into port_codebase's prompt verbatim, read from disk at each call. gbnf_experiment's prompt is task plus suites only. V2's "uv, pytest, pnpm and vitest are installed" line is gone.

Probe (Sonnet 5.5, medium, a tree with both gbnf sources and all suites, asked to run every suite): pytest took two tries (`python -m pytest` found no pytest), vitest four (ESM config cannot resolve the global vitest, `.vite` cache write, missing parent tsconfig). Kevin: "I don't think it is fair to unnecessarily complicate the agents lives so I'm inclined to fix the dockerfile ... we're not testing an agents ability to debug its environment but rather its ability to port code."

Image changed: pytest and pytest-describe installed into the default interpreter with `pytest` on PATH; a `/node_modules` of symlinks to the global npm packages, which ESM resolution walks up to. A model-free e2e test runs `vitest run`, `pytest` and `python -m pytest` from a copy of an ESM package and a python package: red before, green after.

Probe on the rebuilt image: pytest first try, 190 passed. vitest first try fails on the gbnf-source `tsconfig.json` extending `../../../tsconfig.json`, which the prepared tree does not carry; with a stub parent, 200 unit tests pass, one file fails on a missing `./builder/template-tags.js`, and the six integration files fail because the `gbnf` package is not built. All three are gbnf source, left alone.

Branch `sandbox-prompt`, commits 5997cc1, ab0eb3c, then the two above. Study not launched.
