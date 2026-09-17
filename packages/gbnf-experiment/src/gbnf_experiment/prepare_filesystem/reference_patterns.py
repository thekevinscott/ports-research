PATTERNS = {
    "python": (
        "/.gitignore",
        "/Makefile",
        "/MANIFEST.in",
        "/README.md",
        "/dev-deps/**",
        "/gbnf/**/*.py",
        "/pyproject.toml",
        "/requirements.txt",
        "/upgrade-dev-dependencies.sh",
        "/uv.lock",
    ),
    # dev/ is browser and node demo apps and src/builder/ is a grammar-authoring
    # DSL with no counterpart to port; neither is named, so neither is shown.
    "typescript": (
        "/.eslintrc.cjs",
        "/.gitignore",
        "/.npmignore",
        "/Makefile",
        "/README.md",
        "/integration-tests/**",
        "/package.json",
        "/src/*.ts",
        "/src/grammar-graph/**",
        "/src/grammar-parser/**",
        "/src/rules-builder/**",
        "/src/utils/**",
        "/tsconfig.json",
        "/tsconfig.test.json",
        "/vite.config*.ts",
        "/vitest.config*.ts",
    ),
}

WITHHELD_COLOCATED_TESTS = {"typescript": "!**/*.test.ts", "python": "!**/*_test.py"}


def reference_patterns(
    *,
    source_language: str,
    include_typescript_tests: bool,
    include_python_tests: bool,
) -> list[str]:
    """The whitelist admitting one language's reference into the container.

    Default deny: the tree is whatever these name. The only conditional is the
    withheld language's colocated tests, excluded whichever way the port runs.
    """
    included = {
        "typescript": include_typescript_tests,
        "python": include_python_tests,
    }
    return [
        *PATTERNS[source_language],
        *(
            WITHHELD_COLOCATED_TESTS[language]
            for language, wanted in included.items()
            if not wanted
        ),
    ]
