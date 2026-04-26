import csv
import importlib.util
import json
import shutil
import subprocess
import sys
from pathlib import Path
from uuid import uuid4


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "examples" / "run_local_ranking_workflow.py"
SAMPLE_INPUT = REPO_ROOT / "data" / "examples" / "sample_runner_history.csv"

SPEC = importlib.util.spec_from_file_location(
    "run_local_ranking_workflow", SCRIPT_PATH
)
WORKFLOW = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(WORKFLOW)


def run_workflow(*args):
    return subprocess.run(
        [sys.executable, str(SCRIPT_PATH), *args],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
    )


def make_temp_dir(stem):
    return REPO_ROOT / "modern_tests" / f"_{stem}_{uuid4().hex}"


def read_csv_rows(path):
    with path.open(newline="", encoding="utf-8") as input_file:
        reader = csv.DictReader(input_file)
        return reader.fieldnames, list(reader)


def cleanup_paths(*paths):
    for path in paths:
        if path.is_dir():
            shutil.rmtree(path, ignore_errors=True)
        elif path.exists():
            path.unlink()


def test_local_ranking_workflow_default_command_succeeds(monkeypatch, capsys):
    output_dir = make_temp_dir("workflow_default")
    features_output = output_dir / "runner_features.csv"
    rankings_output = output_dir / "race_rankings.csv"
    report_output = output_dir / "model_report.json"

    try:
        monkeypatch.setattr(WORKFLOW, "DEFAULT_INPUT", SAMPLE_INPUT)
        monkeypatch.setattr(WORKFLOW, "DEFAULT_FEATURES_OUTPUT", features_output)
        monkeypatch.setattr(WORKFLOW, "DEFAULT_RANKINGS_OUTPUT", rankings_output)
        monkeypatch.setattr(WORKFLOW, "DEFAULT_REPORT_OUTPUT", report_output)

        exit_code = WORKFLOW.main([])
        captured = capsys.readouterr()

        assert exit_code == 0
        assert "Feature rows written: 6" in captured.out
        assert "Ranking rows written: 6" in captured.out
        assert "Races ranked: 1" in captured.out
        assert (
            "- 2026-06-20_Ascot_1400: runner-004 / Desert Echo (score 0.880953)"
            in captured.out
        )
        assert f"Report output: {report_output}" in captured.out
        assert features_output.exists()
        assert rankings_output.exists()
        assert report_output.exists()

        _, ranking_rows = read_csv_rows(rankings_output)
        assert len(ranking_rows) == 6

        with report_output.open(encoding="utf-8") as input_file:
            report = json.load(input_file)

        assert report["leakage_columns_excluded"] == [
            "starting_price",
            "result",
            "current_performance_profit",
        ]
    finally:
        cleanup_paths(output_dir)


def test_local_ranking_workflow_explicit_paths_succeed():
    output_dir = make_temp_dir("workflow_explicit")
    features_output = output_dir / "runner_features.csv"
    rankings_output = output_dir / "race_rankings.csv"
    report_output = output_dir / "model_report.json"

    try:
        result = run_workflow(
            "--input",
            str(SAMPLE_INPUT),
            "--features-output",
            str(features_output),
            "--rankings-output",
            str(rankings_output),
            "--report-output",
            str(report_output),
        )

        assert result.returncode == 0, result.stderr
        assert "Feature rows written: 6" in result.stdout
        assert "Ranking rows written: 6" in result.stdout
        assert "Races ranked: 1" in result.stdout
        assert features_output.exists()
        assert rankings_output.exists()
        assert report_output.exists()

        _, ranking_rows = read_csv_rows(rankings_output)
        assert len(ranking_rows) == 6
        assert ranking_rows[0]["rank"] == "1"
        assert ranking_rows[0]["runner_id"] == "runner-004"

        with report_output.open(encoding="utf-8") as input_file:
            report = json.load(input_file)

        assert report["race_count"] == 1
        assert len(report["races"]) == 1
        assert report["races"][0]["number_of_runners"] == 6
        assert report["leakage_columns_excluded"] == [
            "starting_price",
            "result",
            "current_performance_profit",
        ]
    finally:
        cleanup_paths(output_dir)
