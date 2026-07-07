import csv
import io
import subprocess
import sys
from pathlib import Path
import pytest

# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def run_cli():
    """
    Helper fixture to execute the CLI script.
    Since we do not import src/logsum.py directly, we run it as a subprocess
    to rigorously test the CLI invocation, inputs, outputs, and exit codes.
    """
    def _run(args, stdin=None):
        cli_path = Path(__file__).parent.parent / "src" / "logsum.py"
        # Run using the same python interpreter
        result = subprocess.run(
            [sys.executable, str(cli_path)] + args,
            input=stdin,
            capture_output=True,
            text=True
        )
        return result
    return _run


@pytest.fixture
def temp_csv_factory(tmp_path):
    """Factory fixture to create temporary CSV files easily."""
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


# ============================================================================
# Tests: Normalization and Grouping
# ============================================================================

def test_successful_normalization_and_grouping(temp_csv_factory, tmp_path, run_cli):
    """
    Verifies that:
    - Whitespace is trimmed from fields.
    - 'level' is converted to uppercase.
    - 'service' is converted to lowercase.
    - 'message' is ignored during grouping.
    - Matches are grouped, counts calculated, and min/max timestamps tracked.
    """
    input_rows = [
        # Match 1: different cases & whitespace, same target level/service
        ["2026-07-07T14:30:00Z", "  info  ", "  auth-service  ", "User login successful"],
        ["2026-07-07T14:35:00Z", "INFO", "Auth-Service", "User logged out"],
        ["2026-07-07T14:20:00Z", "Info", "auth-service", "Different message"],
        # Match 2: distinct group
        ["2026-07-07T15:00:00Z", "ERROR", "db-service", "Connection timeout"],
        # Match 3: duplicate row counted independently
        ["2026-07-07T16:00:00Z", "WARN", "api", "Rate limit"],
        ["2026-07-07T16:00:00Z", "WARN", "api", "Rate limit"],
    ]

    input_file = temp_csv_factory("events.csv", input_rows)
    output_file = tmp_path / "summary.csv"

    # Invoke CLI: python src/logsum.py <input> <output>
    # Note: Adjust CLI argument layout as required by your CLI parser (e.g. --input/--output or positional).
    # Assuming standard positional arguments: logsum.py [input_file] [output_file]
    result = run_cli([str(input_file), str(output_file)])

    assert result.returncode == 0, f"CLI execution failed: {result.stderr}"
    assert output_file.exists()

    # Parse output summary
    with open(output_file, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    # Check output headers
    assert reader.fieldnames == ["level", "service", "count", "first_seen", "last_seen"]
    assert len(rows) == 3

    # Map results by (level, service) for order-independent assertions
    summary_map = {(row["level"], row["service"]): row for row in rows}

    # Assert Group 1: INFO / auth-service
    assert ("INFO", "auth-service") in summary_map
    group_1 = summary_map[("INFO", "auth-service")]
    assert group_1["count"] == "3"
    assert group_1["first_seen"] == "2026-07-07T14:20:00Z"  # Chronologically earliest
    assert group_1["last_seen"] == "2026-07-07T14:35:00Z"   # Chronologically latest

    # Assert Group 2: ERROR / db-service
    assert ("ERROR", "db-service") in summary_map
    group_2 = summary_map[("ERROR", "db-service")]
    assert group_2["count"] == "1"
    assert group_2["first_seen"] == "2026-07-07T15:00:00Z"
    assert group_2["last_seen"] == "2026-07-07T15:00:00Z"

    # Assert Group 3: WARN / api
    assert ("WARN", "api") in summary_map
    group_3 = summary_map[("WARN", "api")]
    assert group_3["count"] == "2"
    assert group_3["first_seen"] == "2026-07-07T16:00:00Z"
    assert group_3["last_seen"] == "2026-07-07T16:00:00Z"


# ============================================================================
# Tests: Validation & Error Handling (Non-zero exit codes)
# ============================================================================

def test_empty_input_file(temp_csv_factory, tmp_path, run_cli):
    """An empty input file or input with only headers should exit gracefully or raise an error."""
    # Scenario A: Completely empty file
    empty_file = tmp_path / "empty.csv"
    empty_file.write_text("", encoding="utf-8")
    output_file = tmp_path / "summary.csv"

    result = run_cli([str(empty_file), str(output_file)])
    assert result.returncode != 0, "Expected non-zero exit code for completely empty input file."


def test_missing_header_row(temp_csv_factory, tmp_path, run_cli):
    """Input lacking the required CSV headers should fail."""
    bad_headers = ["time", "severity", "app", "msg"] # Incorrect column names
    rows = [["2026-07-07T14:30:00Z", "INFO", "auth", "hello"]]

    input_file = temp_csv_factory("bad_headers.csv", rows, headers=bad_headers)
    output_file = tmp_path / "summary.csv"

    result = run_cli([str(input_file), str(output_file)])
    assert result.returncode != 0, "Expected non-zero exit code for missing/incorrect header columns."


def test_missing_required_field_value(temp_csv_factory, tmp_path, run_cli):
    """Empty level/service values are normalised to UNKNOWN/unknown per spec (not an error)."""
    rows = [
        ["2026-07-07T14:30:00Z", "", "auth-service", "Level is missing"],  # empty level → UNKNOWN
    ]
    input_file = temp_csv_factory("missing_fields.csv", rows)
    output_file = tmp_path / "summary.csv"

    result = run_cli([str(input_file), str(output_file)])
    assert result.returncode == 0, f"Expected success when level is blank (normalised to UNKNOWN): {result.stderr}"
    assert output_file.exists()

    with open(output_file, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows_out = list(reader)

    assert len(rows_out) == 1
    assert rows_out[0]["level"] == "UNKNOWN"
    assert rows_out[0]["service"] == "auth-service"


@pytest.mark.parametrize("invalid_timestamp", [
    "07/07/2026 14:30:00",       # Completely wrong format
    "2026-07-07T25:30:00Z",      # Out of bounds hour
    "not-a-timestamp",           # Plain text garbage
    "",                          # Empty string
])
def test_malformed_timestamps(temp_csv_factory, tmp_path, run_cli, invalid_timestamp):
    """Timestamps must be valid ISO 8601 values. If not, exit with error."""
    rows = [
        [invalid_timestamp, "INFO", "web", "Request received"]
    ]
    input_file = temp_csv_factory("bad_timestamp.csv", rows)
    output_file = tmp_path / "summary.csv"

    result = run_cli([str(input_file), str(output_file)])
    assert result.returncode != 0, f"Expected non-zero exit code for invalid timestamp format: '{invalid_timestamp}'"


# ============================================================================
# Tests: CLI Invocations and Arguments
# ============================================================================

def test_missing_command_line_arguments(run_cli):
    """Running the CLI without required input/output arguments should exit with a non-zero code."""
    result = run_cli([])
    assert result.returncode != 0


def test_nonexistent_input_file(tmp_path, run_cli):
    """Passing a non-existent input file path should lead to a clean error exit."""
    bad_input_path = tmp_path / "does_not_exist.csv"
    output_file = tmp_path / "summary.csv"

    result = run_cli([str(bad_input_path), str(output_file)])
    assert result.returncode != 0