from measure_transcript.split_command import split_command


def words(command, cwd="/target"):
    return [s["words"] for s in split_command(command, cwd)["segments"]]


def describe_split_command():
    def it_splits_on_separators_and_newlines():
        assert words("a 1; b && c || d | e\nf") == [["a", "1"], ["b"], ["c"], ["d"], ["e"], ["f"]]

    def it_keeps_a_quoted_multiline_argument_as_one_word():
        assert words('python3 -c "a\nb" && x') == [["python3", "-c", "a\nb"], ["x"]]

    def it_strips_heredoc_bodies_and_returns_them():
        result = split_command("cat > a.py <<'EOF'\nprint(1)\nEOF\nls", "/target")
        assert [s["words"] for s in result["segments"]] == [["cat"], ["ls"]]
        assert result["heredocs"] == ["print(1)\n"]

    def it_tracks_cd_within_the_command():
        result = split_command("cd /input; cat x && cd python && ls", "/target")
        assert [s["cwd"] for s in result["segments"]] == ["/input", "/input", "/input/python", "/input/python"]

    def it_resolves_write_redirects_and_drops_them_from_the_words():
        result = split_command("pytest > out.txt 2>&1; echo a >> /tmp/log; ls 2>/dev/null", "/target")
        assert [s["words"] for s in result["segments"]] == [["pytest"], ["echo", "a"], ["ls"]]
        assert [s["writes"] for s in result["segments"]] == [["/target/out.txt"], ["/tmp/log"], []]

    def it_counts_tee_arguments_as_writes():
        result = split_command("echo x | tee -a a.txt", "/target/src")
        assert result["segments"][1]["writes"] == ["/target/src/a.txt"]

    def it_drops_input_redirects():
        assert words("python3 - < script.py") == [["python3", "-"]]

    def it_splits_out_a_command_substitution_and_keeps_its_place():
        assert words("ln -s $(npm root -g)/vitest /target/vitest") == [["npm", "root", "-g"], ["ln", "-s", "$(...)/vitest", "/target/vitest"]]

    def it_falls_back_to_whitespace_on_unbalanced_quotes():
        assert words("echo 'a b") == [["echo", "'a", "b"]]

    def it_unrolls_a_for_loop_over_its_words():
        assert words('cd /x; for f in a b/*.py; do echo "= $f"; cat ${f}; done | head') == [
            ["cd", "/x"], ["echo", "= a"], ["cat", "a"], ["echo", "= b/*.py"], ["cat", "b/*.py"], ["head"],
        ]

    def it_unrolls_nested_loops():
        assert words("for a in 1 2; do for b in x; do echo $a$b; done; done") == [["echo", "1x"], ["echo", "2x"]]

    def it_expands_a_find_substitution_from_the_reference_listing():
        files = {"/input/python/gbnf/b.py", "/input/python/gbnf/a.py", "/input/python/README.md"}
        result = split_command("cd /input/python; for f in $(find gbnf -name '*.py' | sort); do cat $f; done", "/target", files)
        assert [s["words"] for s in result["segments"]][-2:] == [["cat", "gbnf/a.py"], ["cat", "gbnf/b.py"]]
        assert split_command("cat $(find /target -name '*.ts')", "/target", files)["segments"][-1]["words"] == ["cat", "$(...)"]
