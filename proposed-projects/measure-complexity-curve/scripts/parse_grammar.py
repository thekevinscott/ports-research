import argparse
import sys
from pathlib import Path

# Not a package module: a subprocess entry point hyperfine shells out to, so it
# is exempt from the one-function-per-file/colocated-test gate that governs
# src/. Mirrors execute-test-suite's own host-subprocess execution strategy
# (PYTHONPATH-style sys.path insertion, then a bare `import gbnf`) rather than
# inventing a second one.


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", type=Path, required=True)
    parser.add_argument("--grammar-file", type=Path, required=True)
    parser.add_argument("--iterations", type=int, required=True)
    args = parser.parse_args()

    sys.path.insert(0, str(args.target))
    import gbnf

    grammar = args.grammar_file.read_text()
    for _ in range(args.iterations):
        gbnf.GBNF(grammar)


if __name__ == "__main__":
    main()
