# Generated Python test suite

Copy the suite into the ported implementation, then run it:

```sh
cd /workspace/ported_implementation
cp -r /workspace/tests/python tests
PYTHONPATH=src uv run --offline --no-project --with pytest==9.1.1 --with pytest-describe==3.2.0 python -m pytest tests
```

`python -m pytest` puts the working directory on `sys.path` and `PYTHONPATH=src` adds the
package root of a `src` layout, so `import two_number_adder` resolves from the port.

The versions are pinned to what the image's uv cache holds. `--offline` reads only that
cache, so changing either pin makes the command fail to resolve.
