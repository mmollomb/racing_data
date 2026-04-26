import argparse
import csv
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = Path("data/examples/runner_features.csv")
DEFAULT_OUTPUT = Path("data/examples/model_report.json")
REQUIRED_COLUMNS = [
    "runner_id",
    "horse_name",
    "race_date",
    "race_track",
    "runner_number",
    "starting_price",
    "result",
    "current_performance_profit",
]
LEAKAGE_COLUMNS = [
    "starting_price",
    "result",
    "current_performance_profit",
]
IDENTIFIER_CONTEXT_COLUMNS = [
    "runner_id",
]
REVIEW_BEFORE_MODELLING_COLUMNS = [
    "horse_name",
    "race_date",
    "race_track",
    "runner_number",
]
BASELINE_SCORE_COLUMNS = [
    "career_win_pct",
    "career_roi",
    "last_10_win_pct",
    "last_10_place_pct",
    "on_track_win_pct",
    "at_distance_win_pct",
    "with_jockey_win_pct",
]


class InputValidationError(Exception):
    """Raised when the feature table does not meet the modelling example contract."""


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description="Build a lightweight model-readiness report from runner features."
    )
    parser.add_argument(
        "--input",
        default=str(DEFAULT_INPUT),
        help="Input CSV path, relative to the repository root unless absolute.",
    )
    parser.add_argument(
        "--output",
        default=str(DEFAULT_OUTPUT),
        help="Output JSON path, relative to the repository root unless absolute.",
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

    assert reader.fieldnames is not None
    return reader.fieldnames, rows


def is_numeric_column(rows, column):
    saw_value = False

    for row in rows:
        value = row.get(column, "")
        if value == "":
            continue

        try:
            float(value)
        except ValueError:
            return False

        saw_value = True

    return saw_value


def identify_safe_feature_columns(fieldnames, rows):
    excluded_columns = set(
        LEAKAGE_COLUMNS
        + IDENTIFIER_CONTEXT_COLUMNS
        + REVIEW_BEFORE_MODELLING_COLUMNS
    )
    return [
        column
        for column in fieldnames
        if column not in excluded_columns and is_numeric_column(rows, column)
    ]


def build_baseline_ranking(rows, safe_feature_columns):
    score_columns = [
        column for column in BASELINE_SCORE_COLUMNS if column in safe_feature_columns
    ]
    ranked_rows = []

    for row in rows:
        values = [
            float(row[column])
            for column in score_columns
            if row.get(column, "") != ""
        ]
        baseline_score = round(sum(values) / len(values), 6) if values else None
        ranked_rows.append(
            {
                "runner_id": row["runner_id"],
                "horse_name": row["horse_name"],
                "baseline_score": baseline_score,
            }
        )

    ranked_rows.sort(
        key=lambda item: (
            item["baseline_score"] is None,
            0 if item["baseline_score"] is None else -item["baseline_score"],
        )
    )

    for index, row in enumerate(ranked_rows, start=1):
        row["rank"] = index

    return {
        "warning": (
            "Toy baseline ranking for pipeline validation only. "
            "This is not a production model."
        ),
        "score_features_used": score_columns,
        "rows": ranked_rows,
    }


def build_model_report(fieldnames, rows):
    safe_feature_columns = identify_safe_feature_columns(fieldnames, rows)
    excluded_leakage_columns = [
        column for column in LEAKAGE_COLUMNS if column in fieldnames
    ]
    identifier_context_columns_excluded = [
        column for column in IDENTIFIER_CONTEXT_COLUMNS if column in fieldnames
    ]
    review_before_modelling_columns_excluded = [
        column for column in REVIEW_BEFORE_MODELLING_COLUMNS if column in fieldnames
    ]

    return {
        "row_count": len(rows),
        "feature_count": len(safe_feature_columns),
        "safe_feature_columns": safe_feature_columns,
        "excluded_leakage_columns": excluded_leakage_columns,
        "identifier_context_columns_excluded": identifier_context_columns_excluded,
        "review_before_modelling_columns_excluded": review_before_modelling_columns_excluded,
        "outcome_target_columns_available": excluded_leakage_columns,
        "warning": (
            "Sample data is too small for real modelling. "
            "This report is only a baseline readiness check."
        ),
        "baseline_ranking": build_baseline_ranking(
            rows, safe_feature_columns
        ),
    }


def write_report(report, output_path):
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", encoding="utf-8") as output_file:
        json.dump(report, output_file, indent=2)
        output_file.write("\n")


def main(argv=None):
    args = parse_args(argv)
    input_path = resolve_repo_path(args.input)
    output_path = resolve_repo_path(args.output)
    fieldnames, rows = load_feature_rows(input_path)
    report = build_model_report(fieldnames, rows)
    write_report(report, output_path)
    print(f"Wrote model readiness report to {output_path}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except InputValidationError as error:
        print(f"Error: {error}", file=sys.stderr)
        raise SystemExit(1)
