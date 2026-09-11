# Generated Python test suite

Copy the suite into the ported implementation, then run it:

```sh
cd /workspace/ported_implementation
cp -r /workspace/tests/python tests
uv run --offline --no-project --with pytest==9.1.1 --with pytest-describe==3.2.0 python -m pytest tests
```

Run it as written. `python -m pytest` puts the working directory on `sys.path`, so `import
gbnf` resolves from the port root. Set `PYTHONPATH` if your package lives somewhere else.

A `pytest` is also on `PATH`, but running it directly leaves the working directory off
`sys.path`, and `pytest tests` fails to import the package under test. The bare `python` has
no pytest of its own — `uv run` is what supplies it.

The versions are pinned to what the image's uv cache holds. `--offline` reads only that
cache, so changing either pin makes the command fail to resolve.
