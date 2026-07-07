"""Independent spec-derived tests for logsum, generated in isolation tier 2."""

import csv
import subprocess
import sys
from pathlib import Path

import pytest


@pytest.fixture
def run_cli():
    def _run(args, stdin=None):
        cli_path = Path(__file__).parent.parent / "src" / "logsum.py"
        result = subprocess.run(
            [sys.executable, str(cli_path)] + args,
            input=stdin,
            capture_output=True,
            text=True,
        )
        return result

    return _run


@pytest.fixture
def temp_csv_factory(tmp_path):
    def _create_file(filename, data_rows, headers=None):
        file_path = tmp_path / filename
        if headers is None:
            headers = ["timestamp", "level", "service", "message"]

        with open(file_path, mode="w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            writer.writerows(data_rows)
        return file_path

    return _create_file


def test_successful_normalization_and_grouping(temp_csv_factory, tmp_path, run_cli):
    input_rows = [
        ["2026-07-07T14:30:00Z", "  info  ", "  auth-service  ", "User login successful"],
        ["2026-07-07T14:35:00Z", "INFO", "Auth-Service", "User logged out"],
        ["2026-07-07T14:20:00Z", "Info", "auth-service", "Different message"],
        ["2026-07-07T15:00:00Z", "ERROR", "db-service", "Connection timeout"],
        ["2026-07-07T16:00:00Z", "WARN", "api", "Rate limit"],
        ["2026-07-07T16:00:00Z", "WARN", "api", "Rate limit"],
    ]

    input_file = temp_csv_factory("events.csv", input_rows)
    output_file = tmp_path / "summary.csv"

    result = run_cli([str(input_file), str(output_file)])

    assert result.returncode == 0, f"CLI execution failed: {result.stderr}"
    assert output_file.exists()

    with open(output_file, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    assert reader.fieldnames == ["level", "service", "count", "first_seen", "last_seen"]
    assert len(rows) == 3

    summary_map = {(row["level"], row["service"]): row for row in rows}

    assert ("INFO", "auth-service") in summary_map
    group_1 = summary_map[("INFO", "auth-service")]
    assert group_1["count"] == "3"
    assert group_1["first_seen"] == "2026-07-07T14:20:00Z"
    assert group_1["last_seen"] == "2026-07-07T14:35:00Z"

    assert ("ERROR", "db-service") in summary_map
    group_2 = summary_map[("ERROR", "db-service")]
    assert group_2["count"] == "1"
    assert group_2["first_seen"] == "2026-07-07T15:00:00Z"
    assert group_2["last_seen"] == "2026-07-07T15:00:00Z"

    assert ("WARN", "api") in summary_map
    group_3 = summary_map[("WARN", "api")]
    assert group_3["count"] == "2"
    assert group_3["first_seen"] == "2026-07-07T16:00:00Z"
    assert group_3["last_seen"] == "2026-07-07T16:00:00Z"


def test_min_count_filters_groups(temp_csv_factory, tmp_path, run_cli):
    input_rows = [
        ["2026-07-07T14:30:00Z", "  info  ", "  auth-service  ", "User login successful"],
        ["2026-07-07T14:35:00Z", "INFO", "Auth-Service", "User logged out"],
        ["2026-07-07T14:20:00Z", "Info", "auth-service", "Different message"],
        ["2026-07-07T15:00:00Z", "ERROR", "db-service", "Connection timeout"],
        ["2026-07-07T16:00:00Z", "WARN", "api", "Rate limit"],
        ["2026-07-07T16:00:00Z", "WARN", "api", "Rate limit"],
    ]

    input_file = temp_csv_factory("events.csv", input_rows)
    output_file = tmp_path / "summary.csv"

    result = run_cli(["--min-count", "2", str(input_file), str(output_file)])

    assert result.returncode == 0, f"CLI execution failed: {result.stderr}"

    with open(output_file, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    assert reader.fieldnames == ["level", "service", "count", "first_seen", "last_seen"]
    assert len(rows) == 2

    summary_map = {(row["level"], row["service"]): row for row in rows}

    assert ("INFO", "auth-service") in summary_map
    assert summary_map[("INFO", "auth-service")]["count"] == "3"

    assert ("WARN", "api") in summary_map
    assert summary_map[("WARN", "api")]["count"] == "2"
    assert ("ERROR", "db-service") not in summary_map


def test_empty_input_file(temp_csv_factory, tmp_path, run_cli):
    empty_file = tmp_path / "empty.csv"
    empty_file.write_text("", encoding="utf-8")
    output_file = tmp_path / "summary.csv"

    result = run_cli([str(empty_file), str(output_file)])
    assert result.returncode != 0


def test_missing_header_row(temp_csv_factory, tmp_path, run_cli):
    bad_headers = ["time", "severity", "app", "msg"]
    rows = [["2026-07-07T14:30:00Z", "INFO", "auth", "hello"]]

    input_file = temp_csv_factory("bad_headers.csv", rows, headers=bad_headers)
    output_file = tmp_path / "summary.csv"

    result = run_cli([str(input_file), str(output_file)])
    assert result.returncode != 0


def test_missing_required_field_value(temp_csv_factory, tmp_path, run_cli):
    rows = [
        ["2026-07-07T14:30:00Z", "", "auth-service", "Level is missing"],
    ]
    input_file = temp_csv_factory("missing_fields.csv", rows)
    output_file = tmp_path / "summary.csv"

    result = run_cli([str(input_file), str(output_file)])
    assert result.returncode == 0, result.stderr
    assert output_file.exists()

    with open(output_file, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows_out = list(reader)

    assert len(rows_out) == 1
    assert rows_out[0]["level"] == "UNKNOWN"
    assert rows_out[0]["service"] == "auth-service"


@pytest.mark.parametrize("invalid_timestamp", [
    "07/07/2026 14:30:00",
    "2026-07-07T25:30:00Z",
    "not-a-timestamp",
    "",
])
def test_malformed_timestamps(temp_csv_factory, tmp_path, run_cli, invalid_timestamp):
    rows = [
        [invalid_timestamp, "INFO", "web", "Request received"],
    ]
    input_file = temp_csv_factory("bad_timestamp.csv", rows)
    output_file = tmp_path / "summary.csv"

    result = run_cli([str(input_file), str(output_file)])
    assert result.returncode != 0, invalid_timestamp


def test_missing_command_line_arguments(run_cli):
    result = run_cli([])
    assert result.returncode != 0


def test_nonexistent_input_file(tmp_path, run_cli):
    bad_input_path = tmp_path / "does_not_exist.csv"
    output_file = tmp_path / "summary.csv"

    result = run_cli([str(bad_input_path), str(output_file)])
    assert result.returncode != 0