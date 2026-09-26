import re
from datetime import UTC, datetime, timedelta, timezone
from unittest.mock import patch

import pytest

from gbnf_experiment.prepare_filesystem.run_directory_name import run_directory_name


@pytest.fixture
def token_hex():
    with patch("gbnf_experiment.prepare_filesystem.run_directory_name.token_hex", autospec=True) as m:
        m.return_value = "9f2b1c04"
        yield m


def describe_run_directory_name():
    def it_joins_the_timestamp_to_a_random_token(token_hex):
        stamp = datetime(2026, 9, 6, 14, 25, 30, tzinfo=UTC)
        assert run_directory_name(stamp) == "20260906T142530Z_9f2b1c04"

    def it_normalises_a_non_utc_timestamp(token_hex):
        stamp = datetime(2026, 9, 6, 9, 25, 30, tzinfo=timezone(timedelta(hours=-5)))
        assert run_directory_name(stamp).startswith("20260906T142530Z")

    def it_sorts_lexically_in_chronological_order(token_hex):
        earlier = run_directory_name(datetime(2026, 9, 6, 23, 59, 59, tzinfo=UTC))
        later = run_directory_name(datetime(2026, 9, 7, 0, 0, 0, tzinfo=UTC))
        assert sorted([later, earlier]) == [earlier, later]

    def it_uses_only_filesystem_safe_characters():
        name = run_directory_name(datetime(2026, 12, 31, 0, 0, 0, tzinfo=UTC))
        assert all(character.isalnum() or character in "-_" for character in name)

    def it_names_nothing_but_the_time_and_the_token():
        name = run_directory_name(datetime(2026, 9, 6, tzinfo=UTC))
        assert re.fullmatch(r"\d{8}T\d{6}Z_[0-9a-f]{8}", name)

    def it_separates_two_runs_in_the_same_second():
        stamp = datetime(2026, 9, 6, 14, 25, 30, tzinfo=UTC)
        assert run_directory_name(stamp) != run_directory_name(stamp)
