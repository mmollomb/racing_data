import argparse
import csv
import sys
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = Path("data/examples/runner_features.csv")
DEFAULT_OUTPUT = Path("data/examples/race_rankings.csv")
LEAKAGE_COLUMNS = [
    "starting_price",
    "result",
    "current_performance_profit",
]
# The ranking score is a simple arithmetic mean of transparent, pre-race-safe
# historical features. This is a local baseline for pipeline validation only.
SCORING_COLUMNS = [
    "career_win_pct",
    "career_roi",
    "last_10_win_pct",
    "last_10_place_pct",
    "on_track_win_pct",
    "at_distance_win_pct",
    "with_jockey_win_pct",
]
REQUIRED_COLUMNS = [
    "race_key",
    "runner_id",
    "horse_name",
    "race_date",
    "race_track",
    "race_distance",
] + SCORING_COLUMNS
OUTPUT_COLUMNS = [
    "race_key",
    "rank",
    "runner_id",
    "horse_name",
    "race_date",
    "race_track",
    "race_distance",
    "score",
]


class InputValidationError(Exception):
    """Raised when the ranking input CSV does not meet the local CLI contract."""


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description="Rank runners within each race from a local feature table."
    )
    parser.add_argument(
        "--input",
        default=str(DEFAULT_INPUT),
        help="Input CSV path, relative to the repository root unless absolute.",
    )
    parser.add_argument(
        "--output",
        default=str(DEFAULT_OUTPUT),
        help="Output CSV path, relative to the repository root unless absolute.",
    )
    return parser.parse_args(argv)


def resolve_repo_path(path_value):
    path = Path(path_value)
    return path if path.is_absolute() else ROOT / path


def validate_input_path(input_path):
    if not input_path.exists():
        raise InputValidationError(f"Input file does not exist: {input_path}")

    if not input_path.is_file():
        raise InputValidationError(f"Input path is not a file: {input_path}")


def validate_csv_headers(fieldnames, input_path):
    if fieldnames is None:
        raise InputValidationError(f"Input CSV must include a header row: {input_path}")

    missing_columns = [column for column in REQUIRED_COLUMNS if column not in fieldnames]
    if missing_columns:
        missing_list = ", ".join(missing_columns)
        raise InputValidationError(
            f"Input CSV is missing required columns: {missing_list}"
        )


def load_feature_rows(input_path):
    validate_input_path(input_path)

    with input_path.open(newline="", encoding="utf-8") as input_file:
        reader = csv.DictReader(input_file)
        validate_csv_headers(reader.fieldnames, input_path)
        rows = list(reader)

    if not rows:
        raise InputValidationError(f"Input CSV contains no data rows: {input_path}")

    return rows


def parse_optional_number(value):
    if value == "":
        return None

    return float(value)


def format_value(value):
    if value is None:
        return ""

    if isinstance(value, float):
        return f"{value:.6f}".rstrip("0").rstrip(".")

    return str(value)


def calculate_score(row):
    values = [
        parse_optional_number(row[column])
        for column in SCORING_COLUMNS
        if row.get(column, "") != ""
    ]

    if not values:
        return None

    return round(sum(values) / len(values), 6)


def build_rankings(rows):
    grouped_rows = defaultdict(list)

    for row in rows:
        grouped_rows[row["race_key"]].append(row)

    ranked_rows = []
    for race_key in sorted(grouped_rows):
        race_rows = []
        for row in grouped_rows[race_key]:
            race_rows.append(
                {
                    "race_key": row["race_key"],
                    "runner_id": row["runner_id"],
                    "horse_name": row["horse_name"],
                    "race_date": row["race_date"],
                    "race_track": row["race_track"],
                    "race_distance": row["race_distance"],
                    "score": calculate_score(row),
                }
            )

        race_rows.sort(
            key=lambda row: (
                row["score"] is None,
                0 if row["score"] is None else -row["score"],
                row["runner_id"],
            )
        )

        for index, row in enumerate(race_rows, start=1):
            row["rank"] = index

        ranked_rows.extend(race_rows)

    return ranked_rows


def write_rankings(ranked_rows, output_path):
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", newline="", encoding="utf-8") as output_file:
        writer = csv.DictWriter(output_file, fieldnames=OUTPUT_COLUMNS)
        writer.writeheader()
        for row in ranked_rows:
            writer.writerow({key: format_value(row.get(key)) for key in OUTPUT_COLUMNS})


def main(argv=None):
    args = parse_args(argv)
    input_path = resolve_repo_path(args.input)
    output_path = resolve_repo_path(args.output)
    rows = load_feature_rows(input_path)
    ranked_rows = build_rankings(rows)
    write_rankings(ranked_rows, output_path)
    print(f"Wrote {len(ranked_rows)} ranked runners to {output_path}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except InputValidationError as error:
        print(f"Error: {error}", file=sys.stderr)
        raise SystemExit(1)
