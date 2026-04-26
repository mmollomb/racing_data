import argparse
import importlib.util
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = Path("data/examples/sample_runner_history.csv")
DEFAULT_FEATURES_OUTPUT = Path("data/examples/runner_features.csv")
DEFAULT_RANKINGS_OUTPUT = Path("data/examples/race_rankings.csv")
DEFAULT_REPORT_OUTPUT = Path("data/examples/model_report.json")


def load_module(module_name, relative_path):
    script_path = ROOT / relative_path
    spec = importlib.util.spec_from_file_location(module_name, script_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


BUILD_FEATURE_TABLE = load_module("build_feature_table", "examples/build_feature_table.py")
RANK_RACE = load_module("rank_race", "examples/rank_race.py")
TRAIN_BASELINE_MODEL = load_module(
    "train_baseline_model", "examples/train_baseline_model.py"
)
WORKFLOW_ERRORS = (
    BUILD_FEATURE_TABLE.InputValidationError,
    RANK_RACE.InputValidationError,
    TRAIN_BASELINE_MODEL.InputValidationError,
)


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description="Run the local ranking MVP from runner history to features, rankings, and report."
    )
    parser.add_argument(
        "--input",
        default=str(DEFAULT_INPUT),
        help="Input runner-history CSV path, relative to the repository root unless absolute.",
    )
    parser.add_argument(
        "--features-output",
        default=str(DEFAULT_FEATURES_OUTPUT),
        help="Feature-table CSV output path, relative to the repository root unless absolute.",
    )
    parser.add_argument(
        "--rankings-output",
        default=str(DEFAULT_RANKINGS_OUTPUT),
        help="Race-rankings CSV output path, relative to the repository root unless absolute.",
    )
    parser.add_argument(
        "--report-output",
        default=str(DEFAULT_REPORT_OUTPUT),
        help="Model-report JSON output path, relative to the repository root unless absolute.",
    )
    return parser.parse_args(argv)


def resolve_repo_path(path_value):
    path = Path(path_value)
    return path if path.is_absolute() else ROOT / path


def build_feature_rows(input_path):
    provider = BUILD_FEATURE_TABLE.LocalFileProvider()
    groups = BUILD_FEATURE_TABLE.load_runner_groups(input_path)

    feature_rows = []
    for runner_id, rows in sorted(groups.items()):
        runner = BUILD_FEATURE_TABLE.build_runner(provider, runner_id, rows)
        feature_rows.append(BUILD_FEATURE_TABLE.build_feature_row(runner_id, runner))

    feature_rows.sort(
        key=lambda row: (
            row["race_key"],
            float("inf") if row["runner_number"] is None else row["runner_number"],
            row["runner_id"],
        )
    )
    return feature_rows


def build_report(input_path, output_path):
    fieldnames, rows = TRAIN_BASELINE_MODEL.load_feature_rows(input_path)
    report = TRAIN_BASELINE_MODEL.build_model_report(fieldnames, rows, input_path)
    return preserve_report_timestamp(report, output_path)


def normalize_report(report):
    return {
        key: value
        for key, value in report.items()
        if key != "generated_at_utc"
    }


def preserve_report_timestamp(report, output_path):
    if not output_path.exists():
        return report

    try:
        with output_path.open(encoding="utf-8") as input_file:
            existing_report = json.load(input_file)
    except (OSError, json.JSONDecodeError):
        return report

    if normalize_report(existing_report) == normalize_report(report):
        report["generated_at_utc"] = existing_report.get(
            "generated_at_utc", report["generated_at_utc"]
        )

    return report


def format_score(value):
    if value is None:
        return "n/a"

    return f"{value:.6f}".rstrip("0").rstrip(".")


def summarize_top_ranked(report):
    summary_lines = []

    for race_report in report["races"]:
        top_runner = race_report["baseline_ranking"][0]
        summary_lines.append(
            (
                f"- {race_report['race_key']}: "
                f"{top_runner['runner_id']} / {top_runner['horse_name']} "
                f"(score {format_score(top_runner['baseline_score'])})"
            )
        )

    return summary_lines


def main(argv=None):
    args = parse_args(argv)
    input_path = resolve_repo_path(args.input)
    features_output_path = resolve_repo_path(args.features_output)
    rankings_output_path = resolve_repo_path(args.rankings_output)
    report_output_path = resolve_repo_path(args.report_output)

    feature_rows = build_feature_rows(input_path)
    BUILD_FEATURE_TABLE.write_feature_table(feature_rows, features_output_path)

    ranking_rows = RANK_RACE.build_rankings(
        RANK_RACE.load_feature_rows(features_output_path)
    )
    RANK_RACE.write_rankings(ranking_rows, rankings_output_path)

    report = build_report(features_output_path, report_output_path)
    TRAIN_BASELINE_MODEL.write_report(report, report_output_path)

    print(f"Feature rows written: {len(feature_rows)}")
    print(f"Ranking rows written: {len(ranking_rows)}")
    print(f"Races ranked: {len(report['races'])}")
    print("Top-ranked runners:")
    for line in summarize_top_ranked(report):
        print(line)
    print(f"Report output: {report_output_path}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except WORKFLOW_ERRORS as error:
        print(f"Error: {error}", file=sys.stderr)
        raise SystemExit(1)
