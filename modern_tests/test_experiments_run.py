import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def run_experiment(script_name):
    result = subprocess.run(
        [sys.executable, str(REPO_ROOT / "experiments" / script_name)],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    return result.stdout


def test_runner_experiment_runs():
    output = run_experiment("experiment_runner.py")

    assert "carrying: 55.0" in output
    assert "actual_weight: 625.0" in output
    assert "actual_distance: 1200.0066666481482" in output


def test_horse_form_experiment_runs():
    output = run_experiment("experiment_horse_form.py")

    assert "horse: horse Test Horse" in output
    assert "starts: 2" in output
    assert "wins: 1" in output
    assert "places: 2" in output
    assert "roi: 1.5" in output


def test_runner_form_experiment_runs():
    output = run_experiment("experiment_runner_form.py")

    assert "career starts: 3" in output
    assert "career wins: 1" in output
    assert "last_10 starts: 3" in output
    assert "at_distance starts: 2" in output
    assert "on_track starts: 2" in output
    assert "with_jockey starts: 2" in output
    assert "spell: 25" in output
    assert "up: 3" in output