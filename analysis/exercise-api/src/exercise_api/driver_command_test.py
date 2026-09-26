import sys
from pathlib import Path

from exercise_api.driver_command import driver_command

TARGET = Path("/data/run/ported_implementation")


def describe_driver_command():
    def it_runs_the_python_driver_with_the_current_interpreter():
        command = driver_command(language="python", target=TARGET, adapt=False)
        assert command[0] == sys.executable
        assert command[1].endswith("scripts/driver.py")

    def it_runs_the_typescript_driver_through_pnpm_dlx_tsx():
        command = driver_command(language="typescript", target=TARGET, adapt=False)
        assert command[:2] == ["pnpm", "dlx"]
        assert command[2].startswith("tsx@")
        assert command[3].endswith("scripts/driver.ts")

    def it_passes_the_target():
        command = driver_command(language="python", target=TARGET, adapt=False)
        assert command[command.index("--target") + 1] == str(TARGET)

    def it_omits_adapt_by_default():
        assert "--adapt" not in driver_command(language="typescript", target=TARGET, adapt=False)

    def it_passes_adapt_when_asked():
        assert "--adapt" in driver_command(language="python", target=TARGET, adapt=True)

    def it_omits_repeat_and_warmup_at_their_defaults():
        command = driver_command(language="python", target=TARGET, adapt=False)
        assert "--repeat" not in command
        assert "--warmup" not in command

    def it_passes_repeat_and_warmup_when_asked():
        command = driver_command(language="python", target=TARGET, adapt=False, repeat=30, warmup=3)
        assert command[command.index("--repeat") + 1] == "30"
        assert command[command.index("--warmup") + 1] == "3"
