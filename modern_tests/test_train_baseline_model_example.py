import csv
import importlib.util
import json
import subprocess
import sys
from pathlib import Path
from uuid import uuid4


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "examples" / "train_baseline_model.py"
SAMPLE_INPUT = REPO_ROOT / "data" / "examples" / "runner_features.csv"

SPEC = importlib.util.spec_from_file_location("train_baseline_model", SCRIPT_PATH)
MODEL_SCRIPT = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODEL_SCRIPT)


def run_model_builder(*args):
    return subprocess.run(
        [sys.executable, str(SCRIPT_PATH), *args],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
    )


def write_csv(path, fieldnames, rows=None):
    rows = rows or []

    with path.open("w", newline="", encoding="utf-8") as output_file:
        writer = csv.DictWriter(output_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def make_temp_path(stem, suffix):
    return REPO_ROOT / "modern_tests" / f"_{stem}_{uuid4().hex}{suffix}"


def cleanup_paths(*paths):
    for path in paths:
        if path.exists():
            path.unlink()


def test_train_baseline_model_generates_readiness_report():
    output_path = make_temp_path("model_report", ".json")

    try:
        result = run_model_builder(
            "--input",
            str(SAMPLE_INPUT),
            "--output",
            str(output_path),
        )

        assert result.returncode == 0, result.stderr
        assert f"Wrote model readiness report to {output_path}" in result.stdout
        assert output_path.exists()

        with output_path.open(encoding="utf-8") as input_file:
            report = json.load(input_file)

        assert report["generated_at_utc"].endswith("Z")
        assert report["input_path"] == str(SAMPLE_INPUT)
        assert report["total_rows"] == 6
        assert report["race_count"] == 1
        assert (
            report["safe_numeric_feature_count"]
            == len(report["safe_numeric_features"])
        )
        assert "career_roi" in report["safe_numeric_features"]
        assert "starting_price" not in report["safe_numeric_features"]
        assert report["leakage_columns_excluded"] == MODEL_SCRIPT.LEAKAGE_COLUMNS
        assert (
            report["identifier_context_columns_excluded"]
            == MODEL_SCRIPT.IDENTIFIER_CONTEXT_COLUMNS
        )
        assert report["outcome_target_columns_available"] == MODEL_SCRIPT.LEAKAGE_COLUMNS
        assert "too small for real modelling" in report["warning"]
        assert "not a production model" in report["baseline_warning"]
        assert report["score_features_used"] == MODEL_SCRIPT.BASELINE_SCORE_COLUMNS
        assert len(report["races"]) == 1
        race_report = report["races"][0]
        assert race_report["race_key"] == "2026-06-20_Ascot_1400"
        assert race_report["number_of_runners"] == 6
        assert race_report["winner_runner_id"] == "runner-004"
        assert race_report["winner_rank"] == 1
        assert race_report["winner_in_top_1"] is True
        assert race_report["winner_in_top_2"] is True
        assert race_report["winner_in_top_3"] is True
        ranking_rows = race_report["baseline_ranking"]
        assert len(ranking_rows) == 6
        assert ranking_rows[0]["rank"] == 1
        assert ranking_rows[0]["baseline_score"] >= ranking_rows[-1]["baseline_score"]
        assert [row["runner_id"] for row in ranking_rows] == [
            "runner-004",
            "runner-001",
            "runner-006",
            "runner-005",
            "runner-002",
            "runner-003",
        ]
        assert {row["runner_id"] for row in ranking_rows} >= {
            "runner-001",
            "runner-004",
            "runner-006",
        }
        assert all("runner_number" in row for row in ranking_rows)
        assert all("horse_name" in row for row in ranking_rows)
        assert all("result" in row for row in ranking_rows)
        assert [row["rank"] for row in ranking_rows] == list(
            range(1, len(ranking_rows) + 1)
        )
        assert report["evaluation_summary"] == {
            "race_count": 1,
            "races_with_results": 1,
            "winners_in_top_1": 1,
            "winners_in_top_2": 1,
            "winners_in_top_3": 1,
            "top_1_hit_rate": 1.0,
            "top_2_hit_rate": 1.0,
            "top_3_hit_rate": 1.0,
        }
    finally:
        cleanup_paths(output_path)


def test_train_baseline_model_fails_for_missing_input_file():
    input_path = make_temp_path("missing_runner_features", ".csv")
    output_path = make_temp_path("model_report", ".json")

    try:
        result = run_model_builder(
            "--input",
            str(input_path),
            "--output",
            str(output_path),
        )

        assert result.returncode != 0
        assert f"Error: Input file does not exist: {input_path}" in result.stderr
        assert not output_path.exists()
    finally:
        cleanup_paths(output_path)


def test_train_baseline_model_fails_for_empty_csv():
    input_path = make_temp_path("empty_runner_features", ".csv")
    output_path = make_temp_path("model_report", ".json")

    try:
        input_path.write_text("", encoding="utf-8")

        result = run_model_builder(
            "--input",
            str(input_path),
            "--output",
            str(output_path),
        )

        assert result.returncode != 0
        assert f"Error: Input CSV must include a header row: {input_path}" in result.stderr
        assert not output_path.exists()
    finally:
        cleanup_paths(input_path, output_path)


def test_train_baseline_model_fails_for_missing_required_column():
    input_path = make_temp_path("missing_model_column", ".csv")
    output_path = make_temp_path("model_report", ".json")

    try:
        fieldnames = [
            column
            for column in MODEL_SCRIPT.REQUIRED_COLUMNS
            if column != "runner_id"
        ]
        write_csv(input_path, fieldnames)

        result = run_model_builder(
            "--input",
            str(input_path),
            "--output",
            str(output_path),
        )

        assert result.returncode != 0
        assert "Error: Input CSV is missing required columns: runner_id" in result.stderr
        assert not output_path.exists()
    finally:
        cleanup_paths(input_path, output_path)
