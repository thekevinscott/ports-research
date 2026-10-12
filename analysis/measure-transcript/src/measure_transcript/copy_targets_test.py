from measure_transcript.copy_targets import copy_targets


def describe_copy_targets():
    def it_copies_into_a_directory_named_with_a_trailing_slash():
        assert copy_targets(["cp", "-r", "/input/python/tests/generated", "/target/tests/"], "/target", set()) == [
            ("/target/tests/generated", "/input/python/tests/generated")
        ]

    def it_copies_into_a_known_directory():
        assert copy_targets(["cp", "-r", "/input/python/tests", "dest"], "/target", {"/target/dest"}) == [
            ("/target/dest/tests", "/input/python/tests")
        ]

    def it_copies_to_a_new_name_otherwise():
        assert copy_targets(["cp", "-r", "/input/python", "/tmp/py"], "/target", set()) == [("/tmp/py", "/input/python")]

    def it_copies_several_sources_into_the_destination():
        assert copy_targets(["cp", "a.py", "b.py", "/tmp/x"], "/input/python/gbnf", set()) == [
            ("/tmp/x/a.py", "/input/python/gbnf/a.py"),
            ("/tmp/x/b.py", "/input/python/gbnf/b.py"),
        ]

    def it_maps_a_glob_or_dot_source_to_its_directory():
        assert copy_targets(["cp", "-r", "/input/python/tests/*", "/target/t"], "/target", set()) == [("/target/t", "/input/python/tests")]
        assert copy_targets(["cp", "-r", "/input/python/tests/.", "/target/t"], "/target", set()) == [("/target/t", "/input/python/tests")]

    def it_ignores_other_commands():
        assert copy_targets(["mv", "a", "b"], "/target", set()) == []
