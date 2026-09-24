# One whitelist per gbnf package, mirroring packages/gbnf/{python,javascript}.
# Colocated tests are withheld under every condition; a tests flag mounts the
# generated suite under tests/ and nothing else.
PATTERNS = {
    "python": [
        "/.gitignore",
        "/Makefile",
        "/MANIFEST.in",
        "/README.md",
        "/gbnf/**/*.py",
        "/pyproject.toml",
        "/requirements.txt",
        "/uv.lock",
        "!**/*_test.py",
    ],
    # dev/ is browser and node demo apps, not named. src/builder/ is a
    # grammar-authoring DSL with no counterpart to port.
    "typescript": [
        "/.eslintrc.cjs",
        "/.gitignore",
        "/.npmignore",
        "/README.md",
        "/package.json",
        "/src/**/*.ts",
        "!/src/builder/**",
        "/tsconfig.json",
        "/tsconfig.test.json",
        "/vite.config*.ts",
        "/vitest.config*.ts",
        "!**/*.test.ts",
    ],
}

# The generated suites under the prepared tests/, one pattern per language.
TEST_PATTERNS = {
    "python": "/python/**",
    "typescript": "/typescript/**",
}
