from dataclasses import dataclass


@dataclass(frozen=True)
class CoverageResult:
    """How much of the port's own source one suite run executed.

    Branch counts come free from both tools — coverage.py in branch mode, the v8
    provider always — but a source that never branches has no branch percentage,
    so `branch_pct` is None there rather than zero. A run that measured no lines ran
    none of the port, so `line_pct` is zero there.
    """

    covered_lines: int
    total_lines: int
    covered_branches: int
    total_branches: int

    @property
    def line_pct(self) -> float:
        if not self.total_lines:
            return 0.0
        return 100 * self.covered_lines / self.total_lines

    @property
    def branch_pct(self) -> float | None:
        if not self.total_branches:
            return None
        return 100 * self.covered_branches / self.total_branches
