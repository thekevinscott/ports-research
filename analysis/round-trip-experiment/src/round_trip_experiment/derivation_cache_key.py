from gbnf_experiment.config import compute_prepare_cache_key, settings
from gbnf_experiment.prepare_filesystem.assemble_whitelist.assemble_whitelist import assemble_whitelist


def derivation_cache_key(source_language: str) -> str:
    """gbnf_experiment keys each prepared tree by what it copied. A reverse leg carries
    every suite, so it stages under the key of the tree holding every test for its source.
    """
    return compute_prepare_cache_key(
        settings.gbnf_commit,
        settings.prepare_docker_directory,
        assemble_whitelist(
            source_language,
            include_unit_tests=True,
            include_source_integration_tests=True,
            include_target_integration_tests=True,
        ),
    )
