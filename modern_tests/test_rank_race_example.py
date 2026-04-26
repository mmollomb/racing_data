import csv
import importlib.util
import subprocess
import sys
from pathlib import Path
from uuid import uuid4


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "examples" / "rank_race.py"
SAMPLE_INPUT = REPO_ROOT / "data" / "examples" / "runner_features.csv"

SPEC = importlib.util.spec_from_file_location("rank_race", SCRIPT_PATH)
RANK_RACE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(RANK_RACE)


def run_ranker(*args):
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


def make_temp_path(stem):
    return REPO_ROOT / "modern_tests" / f"_{stem}_{uuid4().hex}.csv"


def cleanup_paths(*paths):
    for path in paths:
        if path.exists():
            path.unlink()


def test_rank_race_example_generates_rankings_from_sample_csv():
    output_path = make_temp_path("race_rankings")

    try:
        result = run_ranker(
            "--input",
            str(SAMPLE_INPUT),
            "--output",
            str(output_path),
        )

        assert result.returncode == 0, result.stderr
        assert f"Wrote 6 ranked runners to {output_path}" in result.stdout
        assert output_path.exists()

        with output_path.open(newline="", encoding="utf-8") as input_file:
            reader = csv.DictReader(input_file)
            rows = list(reader)

        assert reader.fieldnames == RANK_RACE.OUTPUT_COLUMNS
        assert len(rows) == 6
        assert {row["race_key"] for row in rows} == {"2026-06-20_Ascot_1400"}
        assert rows[0]["rank"] == "1"
        assert rows[0]["runner_id"] == "runner-004"
        assert rows[0]["horse_name"] == "Desert Echo"
        assert rows[-1]["rank"] == "6"
    finally:
        cleanup_paths(output_path)


def test_rank_race_example_does_not_use_leakage_columns_for_scoring():
    base_row = {
        "race_key": "2026-06-20_Ascot_1400",
        "runner_id": "runner-a",
        "horse_name": "Runner A",
        "race_date": "2026-06-20",
        "race_track": "Ascot",
        "race_distance": "1400",
        "career_win_pct": "0.5",
        "career_roi": "0.4",
        "last_10_win_pct": "0.3",
        "last_10_place_pct": "0.6",
        "on_track_win_pct": "0.2",
        "at_distance_win_pct": "0.1",
        "with_jockey_win_pct": "0.7",
        "starting_price": "4.0",
        "result": "1",
        "current_performance_profit": "3.0",
    }
    other_row = dict(base_row)
    other_row["runner_id"] = "runner-b"
    other_row["horse_name"] = "Runner B"
    other_row["starting_price"] = "99.0"
    other_row["result"] = "8"
    other_row["current_performance_profit"] = "-1.0"

    ranked_rows = RANK_RACE.build_rankings([other_row, base_row])

    assert set(RANK_RACE.SCORING_COLUMNS).isdisjoint(set(RANK_RACE.LEAKAGE_COLUMNS))
    assert ranked_rows[0]["runner_id"] == "runner-a"
    assert ranked_rows[1]["runner_id"] == "runner-b"
    assert ranked_rows[0]["score"] == ranked_rows[1]["score"]


def test_rank_race_example_fails_for_missing_input_file():
    input_path = make_temp_path("missing_runner_features")
    output_path = make_temp_path("race_rankings")

    try:
        result = run_ranker(
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


def test_rank_race_example_fails_for_empty_csv():
    input_path = make_temp_path("empty_runner_features")
    output_path = make_temp_path("race_rankings")

    try:
        input_path.write_text("", encoding="utf-8")

        result = run_ranker(
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


def test_rank_race_example_fails_for_missing_required_column():
    input_path = make_temp_path("missing_race_key")
    output_path = make_temp_path("race_rankings")

    try:
        fieldnames = [
            column
            for column in RANK_RACE.REQUIRED_COLUMNS
            if column != "race_key"
        ]
        write_csv(input_path, fieldnames)

        result = run_ranker(
            "--input",
            str(input_path),
            "--output",
            str(output_path),
        )

        assert result.returncode != 0
        assert "Error: Input CSV is missing required columns: race_key" in result.stderr
        assert not output_path.exists()
    finally:
        cleanup_paths(input_path, output_path)
