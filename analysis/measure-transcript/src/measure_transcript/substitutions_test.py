from measure_transcript.substitutions import PLACEHOLDER, substitutions


def describe_substitutions():
    def it_replaces_each_substitution_and_returns_its_command():
        assert substitutions("ln -s $(npm root -g)/vitest x") == (f"ln -s {PLACEHOLDER}/vitest x", ["npm root -g"])

    def it_keeps_nested_parentheses_inside_one_substitution():
        assert substitutions("echo $(dirname $(which node))") == (f"echo {PLACEHOLDER}", ["dirname $(which node)"])

    def it_leaves_single_quoted_text_alone():
        assert substitutions("echo '$(x)'") == ("echo '$(x)'", [])
