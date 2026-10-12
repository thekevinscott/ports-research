from measure_transcript.text_runtimes import text_runtimes


def describe_text_runtimes():
    def it_finds_a_runtime_named_as_a_string():
        assert text_runtimes('subprocess.run(["node", "x.mjs"])') == {"node"}
        assert text_runtimes("execSync('python3 gen.py')") == {"python"}

    def it_finds_a_runtime_at_the_start_of_a_line():
        assert text_runtimes("set -e\npython3 a.py\n  npx tsx b.ts\n") == {"python", "node"}

    def it_finds_a_shebang():
        assert text_runtimes("#!/usr/bin/env node\nconsole.log(1)") == {"node"}

    def it_ignores_node_builtin_imports_and_identifiers():
        assert text_runtimes("import fs from 'node:fs';\nconst node = graph.node;\n") == set()
