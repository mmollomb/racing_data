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

        assert report["row_count"] == 2
        assert report["feature_count"] == len(report["safe_feature_columns"])
        assert "career_roi" in report["safe_feature_columns"]
        assert "starting_price" not in report["safe_feature_columns"]
        assert report["excluded_leakage_columns"] == MODEL_SCRIPT.LEAKAGE_COLUMNS
        assert (
            report["identifier_context_columns_excluded"]
            == MODEL_SCRIPT.IDENTIFIER_CONTEXT_COLUMNS
        )
        assert report["outcome_target_columns_available"] == MODEL_SCRIPT.LEAKAGE_COLUMNS
        assert "too small for real modelling" in report["warning"]
        assert "not a production model" in report["baseline_ranking"]["warning"]
        assert (
            report["baseline_ranking"]["score_features_used"]
            == MODEL_SCRIPT.BASELINE_SCORE_COLUMNS
        )
        assert report["baseline_ranking"]["rows"][0]["runner_id"] == "runner-001"
        assert report["baseline_ranking"]["rows"][0]["horse_name"] == "Test Horse"
        assert report["baseline_ranking"]["rows"][0]["rank"] == 1
        assert report["baseline_ranking"]["rows"][0]["baseline_score"] > 0
        assert report["baseline_ranking"]["rows"][1]["rank"] == 2
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
