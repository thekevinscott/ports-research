from pathlib import Path

from .check_staged_derivation import check_staged_derivation
from .load_run import load_run
from .reverse_command import reverse_command
from .reverse_condition import reverse_condition
from .stage_port import stage_port


def reverse_leg(
    run_directory: Path,
    *,
    derivation_cache_key: str,
    derivations_directory: Path,
    gbnf_experiment_directory: Path,
    staging_directory: Path,
    reverse_directory: Path,
) -> dict:
    """Everything a reverse leg needs short of launching it: the port staged as a derivation,
    that staging checked, and the invocation that reads it. One output root per forward run,
    so the leg is findable whatever its exit status.
    """
    loaded = load_run(run_directory)
    condition = reverse_condition(loaded["condition"])
    staged = stage_port(
        run_directory,
        source_language=condition["source_language"],
        derivation_cache_key=derivation_cache_key,
        derivations_directory=derivations_directory,
        staging_directory=staging_directory,
    )
    check_staged_derivation(staged, condition=condition)
    reverse_run_root = reverse_directory / run_directory.name
    command = reverse_command(
        condition=condition,
        staged_derivations_directory=staged.parent,
        reverse_run_root=reverse_run_root,
        gbnf_experiment_directory=gbnf_experiment_directory,
    )
    return {
        "forward": {"run_id": loaded["run_id"], "condition": loaded["condition"]},
        "condition": condition,
        "staged": str(staged),
        "reverse_root": str(reverse_run_root),
        **command,
        "estimate": loaded["estimate"],
    }
