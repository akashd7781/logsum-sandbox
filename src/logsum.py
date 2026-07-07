import csv
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path


REQUIRED_COLUMNS = {"timestamp", "level", "service", "message"}


def normalise_level(value):
    value = (value or "").strip()
    return value.upper() if value else "UNKNOWN"


def normalise_service(value):
    value = (value or "").strip()
    return value.lower() if value else "unknown"


def parse_timestamp(value):
    value = value.strip()

    # Convert ISO 8601 UTC suffix into Python-compatible format
    if value.endswith("Z"):
        value = value[:-1] + "+00:00"

    return datetime.fromisoformat(value)


def format_timestamp(value):
    return value.isoformat().replace("+00:00", "Z")


def process(input_path, output_path, min_count=None):
    groups = defaultdict(
        lambda: {
            "count": 0,
            "first_seen": None,
            "last_seen": None,
        }
    )

    malformed_timestamps = 0

    with open(input_path, "r", encoding="utf-8", newline="") as infile:
        reader = csv.DictReader(infile)

        if not REQUIRED_COLUMNS.issubset(set(reader.fieldnames or [])):
            raise ValueError("Missing required columns")

        for row in reader:
            try:
                timestamp = parse_timestamp(row["timestamp"])
            except (ValueError, TypeError):
                malformed_timestamps += 1
                continue

            level = normalise_level(row.get("level"))
            service = normalise_service(row.get("service"))

            group = groups[(level, service)]
            group["count"] += 1

            if group["first_seen"] is None or timestamp < group["first_seen"]:
                group["first_seen"] = timestamp

            if group["last_seen"] is None or timestamp > group["last_seen"]:
                group["last_seen"] = timestamp

    with open(output_path, "w", encoding="utf-8", newline="") as outfile:
        writer = csv.writer(outfile)

        writer.writerow(["level", "service", "count", "first_seen", "last_seen"])

        # Deterministic output ordering: level, then service
        for (level, service), values in sorted(groups.items()):
            if min_count is not None and values["count"] < min_count:
                continue

            writer.writerow(
                [
                    level,
                    service,
                    values["count"],
                    format_timestamp(values["first_seen"]),
                    format_timestamp(values["last_seen"]),
                ]
            )

    return 3 if malformed_timestamps else 0


def parse_arguments(argv):
    input_output_args = []
    min_count = None
    index = 0

    while index < len(argv):
        argument = argv[index]

        if argument == "--min-count":
            if index + 1 >= len(argv):
                return None

            try:
                min_count = int(argv[index + 1])
            except ValueError:
                return None

            index += 2
            continue

        input_output_args.append(argument)
        index += 1

    if len(input_output_args) != 2:
        return None

    return input_output_args[0], input_output_args[1], min_count


def main(argv=None):
    argv = argv or sys.argv[1:]

    parsed_args = parse_arguments(argv)
    if parsed_args is None:
        print("Usage: python -m src.logsum [--min-count N] <input.csv> <output.csv>")
        return 1

    input_path = Path(parsed_args[0])
    output_path = Path(parsed_args[1])
    min_count = parsed_args[2]

    if not input_path.exists():
        print(f"Input file not found: {input_path}")
        return 1

    try:
        return process(input_path, output_path, min_count=min_count)
    except ValueError as exc:
        print(str(exc))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())