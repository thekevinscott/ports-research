import os
import shutil
from pathlib import Path

from python_on_whales import docker

from gbnf_experiment import config
from gbnf_experiment.config import compute_prepare_cache_key
from gbnf_experiment.prepare_filesystem.assemble_whitelist.assemble_whitelist import assemble_whitelist


def prepare_reference_implementation(
    *,
    source_language: str,
    include_unit_tests: bool,
    include_source_integration_tests: bool,
    include_target_integration_tests: bool,
    debug: bool,
) -> Path:
    """Build the prepare image for one condition and return its /shared, extracted to the cache."""
    rules = assemble_whitelist(
        source_language,
        include_unit_tests=include_unit_tests,
        include_source_integration_tests=include_source_integration_tests,
        include_target_integration_tests=include_target_integration_tests,
    )
    key = compute_prepare_cache_key(config.GBNF_COMMIT, config.PREPARE_DOCKER_DIRECTORY, rules)
    output_directory = config.PREPARED_DIRECTORY / key
    if output_directory.exists():
        return output_directory
    tag = f"gbnf-prepare:{key}"
    docker.build(
        config.PREPARE_DOCKER_DIRECTORY,
        tags=tag,
        build_args={"GBNF_COMMIT": config.GBNF_COMMIT, "RULES": rules},
        progress="tty" if debug else False,
    )
    staging_directory = output_directory.with_name(output_directory.name + ".staging")
    shutil.rmtree(staging_directory, ignore_errors=True)
    staging_directory.mkdir(parents=True)
    docker.run(
        tag,
        ["cp", "-a", "/shared/.", "/prepared-output/"],
        user=f"{os.getuid()}:{os.getgid()}",
        volumes=[(str(staging_directory), "/prepared-output", "rw")],
        remove=True,
    )
    staging_directory.rename(output_directory)
    return output_directory
