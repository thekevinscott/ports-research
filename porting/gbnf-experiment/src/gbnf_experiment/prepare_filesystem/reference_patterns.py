# One whitelist per gbnf package, rooted at the prepared tree: source/<language>
# holds packages/gbnf/{python,javascript}, tests/<language> the generated suites.
# Colocated tests are withheld under every condition; a tests flag adds one
# suite and nothing else.
SOURCE = {
    "python": [
        "/source/python/.gitignore",
        "/source/python/Makefile",
        "/source/python/MANIFEST.in",
        "/source/python/README.md",
        "/source/python/gbnf/**/*.py",
        "/source/python/pyproject.toml",
        "/source/python/requirements.txt",
        "/source/python/uv.lock",
        "!/source/python/**/*_test.py",
    ],
    # dev/ is browser and node demo apps, not named. src/builder/ is a
    # grammar-authoring DSL with no counterpart to port.
    "typescript": [
        "/source/typescript/.eslintrc.cjs",
        "/source/typescript/.gitignore",
        "/source/typescript/.npmignore",
        "/source/typescript/README.md",
        "/source/typescript/package.json",
        "/source/typescript/src/**/*.ts",
        "!/source/typescript/src/builder/**",
        "/source/typescript/tsconfig.json",
        "/source/typescript/tsconfig.test.json",
        "/source/typescript/vite.config*.ts",
        "/source/typescript/vitest.config*.ts",
        "!/source/typescript/**/*.test.ts",
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
