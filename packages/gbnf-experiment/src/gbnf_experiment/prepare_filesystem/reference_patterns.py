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
    "javascript": [
        "/source/javascript/.eslintrc.cjs",
        "/source/javascript/.gitignore",
        "/source/javascript/.npmignore",
        "/source/javascript/README.md",
        "/source/javascript/package.json",
        "/source/javascript/src/**/*.ts",
        "!/source/javascript/src/builder/**",
        "/source/javascript/tsconfig.json",
        "/source/javascript/tsconfig.test.json",
        "/source/javascript/vite.config*.ts",
        "/source/javascript/vitest.config*.ts",
        "!/source/javascript/**/*.test.ts",
    ],
}


def reference_patterns(
    source_language: str, *, include_javascript_tests: bool, include_python_tests: bool
) -> list[str]:
    suites = {"javascript": include_javascript_tests, "python": include_python_tests}
    return [
        *SOURCE[source_language],
        *(f"/tests/{language}/**" for language, wanted in suites.items() if wanted),
    ]
