# Log Summary CLI Specification

## Goal
Create a command-line tool that reads an `events.csv` file and produces a `summary.csv` file containing one row per event group. The tool provides a concise summary of recurring log events for operational analysis.

## Inputs
- Input file: `events.csv`
- CSV header (required):
    - `timestamp`
    - `level`
    - `service`
    - `message`
- UTF-8 encoded.
- First row must be the header.

## Outputs
- Output file: `summary.csv`
- One row per event group.
- Output columns:
    - `level`
    - `service`
    - `count`
    - `first_seen`
    - `last_seen`

## Command-Line Options
- `--min-count N`: only write groups whose count is greater than or equal to `N`.
- Default: omit the flag to write all groups.

## Normalisation Rules
- Trim leading and trailing whitespace from all fields.
- `level` is converted to uppercase.
- `service` is converted to lowercase.
- `message` is not used for grouping and is ignored.
- Timestamps must be valid ISO 8601 values (for example: `2026-07-07T14:30:00Z`).
- Duplicate rows are counted independently.

## Edge Cases
- Empty `level` value → treated as missing; use `UNKNOWN`.
- Empty `service` value → treated as missing; use `unknown`.

## Grouping Rule
Events are grouped using the exact key:
