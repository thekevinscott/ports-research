# One whitelist per gbnf package, rooted at the prepared tree: reference_implementation/<language>
# holds packages/gbnf/{python,javascript}, tests/<language> the generated suites.
# Colocated tests are withheld under every condition; a tests flag adds one
# suite and nothing else.
SOURCE = {
    "python": [
        "/reference_implementation/python/.gitignore",
        "/reference_implementation/python/Makefile",
        "/reference_implementation/python/MANIFEST.in",
        "/reference_implementation/python/README.md",
        "/reference_implementation/python/gbnf/**/*.py",
        "/reference_implementation/python/pyproject.toml",
        "/reference_implementation/python/requirements.txt",
        "/reference_implementation/python/uv.lock",
        "!/reference_implementation/python/**/*_test.py",
    ],
    # dev/ is browser and node demo apps, not named. src/builder/ is a
    # grammar-authoring DSL with no counterpart to port.
    "typescript": [
        "/reference_implementation/typescript/.eslintrc.cjs",
        "/reference_implementation/typescript/.gitignore",
        "/reference_implementation/typescript/.npmignore",
        "/reference_implementation/typescript/README.md",
        "/reference_implementation/typescript/package.json",
        "/reference_implementation/typescript/src/**/*.ts",
        "!/reference_implementation/typescript/src/builder/**",
        "/reference_implementation/typescript/tsconfig.json",
        "/reference_implementation/typescript/tsconfig.test.json",
        "/reference_implementation/typescript/vite.config*.ts",
        "/reference_implementation/typescript/vitest.config*.ts",
        "!/reference_implementation/typescript/**/*.test.ts",
    ],
}


def reference_patterns(
    source_language: str, *, include_typescript_tests: bool, include_python_tests: bool
) -> list[str]:
    suites = {"typescript": include_typescript_tests, "python": include_python_tests}
    return [
        *SOURCE[source_language],
        *(f"/tests/{language}/**" for language, wanted in suites.items() if wanted),
    ]
