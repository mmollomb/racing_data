import csv
import importlib.util
import subprocess
import sys
from pathlib import Path
from uuid import uuid4


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "examples" / "build_feature_table.py"
SAMPLE_INPUT = REPO_ROOT / "data" / "examples" / "sample_runner_history.csv"

SPEC = importlib.util.spec_from_file_location("build_feature_table", SCRIPT_PATH)
FEATURE_TABLE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(FEATURE_TABLE)


def run_feature_builder(*args):
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


def make_temp_csv_path(stem):
    return REPO_ROOT / "modern_tests" / f"_{stem}_{uuid4().hex}.csv"


def cleanup_paths(*paths):
    for path in paths:
        if path.exists():
            path.unlink()


def test_feature_table_example_generates_output_from_sample_csv():
    output_path = make_temp_csv_path("runner_features")

    try:
        result = run_feature_builder(
            "--input",
            str(SAMPLE_INPUT),
            "--output",
            str(output_path),
        )

        assert result.returncode == 0, result.stderr
        assert f"Wrote 2 feature rows to {output_path}" in result.stdout
        assert output_path.exists()

        with output_path.open(newline="", encoding="utf-8") as input_file:
            rows = list(csv.DictReader(input_file))

        assert len(rows) == 2
        assert rows[0]["runner_id"] == "runner-001"
        assert rows[1]["runner_id"] == "runner-002"
        assert "career_roi" in rows[0]
        assert "previous_performance_result" in rows[0]
    finally:
        cleanup_paths(output_path)


def test_feature_table_example_fails_for_missing_input_file():
    input_path = make_temp_csv_path("missing")
    output_path = make_temp_csv_path("runner_features")

    try:
        result = run_feature_builder(
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


def test_feature_table_example_fails_for_empty_csv():
    input_path = make_temp_csv_path("empty")
    output_path = make_temp_csv_path("runner_features")

    try:
        input_path.write_text("", encoding="utf-8")

        result = run_feature_builder(
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


def test_feature_table_example_fails_for_header_only_csv():
    input_path = make_temp_csv_path("header_only")
    output_path = make_temp_csv_path("runner_features")

    try:
        write_csv(input_path, FEATURE_TABLE.REQUIRED_COLUMNS)

        result = run_feature_builder(
            "--input",
            str(input_path),
            "--output",
            str(output_path),
        )

        assert result.returncode != 0
        assert f"Error: Input CSV contains no data rows: {input_path}" in result.stderr
        assert not output_path.exists()
    finally:
        cleanup_paths(input_path, output_path)


def test_feature_table_example_fails_for_missing_required_column():
    input_path = make_temp_csv_path("missing_column")
    output_path = make_temp_csv_path("runner_features")

    try:
        fieldnames = [
            column
            for column in FEATURE_TABLE.REQUIRED_COLUMNS
            if column != "runner_id"
        ]
        write_csv(input_path, fieldnames)

        result = run_feature_builder(
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
