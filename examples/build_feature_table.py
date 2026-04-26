import argparse
import csv
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

from racing_data import Horse, Meet, Performance, PerformanceList, Race, Runner


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = Path("data/examples/sample_runner_history.csv")
DEFAULT_OUTPUT = Path("data/examples/runner_features.csv")
REQUIRED_COLUMNS = [
    "runner_id",
    "race_date",
    "race_track",
    "race_distance",
    "race_track_condition",
    "race_track_circ",
    "race_track_straight",
    "race_start_time",
    "race_number",
    "runner_number",
    "horse_name",
    "horse_url",
    "runner_jockey_url",
    "runner_weight",
    "runner_jockey_claiming",
    "runner_barrier",
    "performance_date",
    "performance_track",
    "performance_jockey_url",
    "performance_result",
    "performance_starting_price",
    "performance_prize_pool",
    "performance_prize_money",
    "performance_starters",
    "performance_distance",
    "performance_track_condition",
    "performance_barrier",
    "performance_lengths",
    "performance_carried",
    "performance_weight",
    "performance_winning_time",
]


class InputValidationError(Exception):
    """Raised when the input CSV does not meet the feature-generator contract."""


class DummyScraper:
    def is_compatible_with(self, scraper_version):
        return True


class LocalFileProvider:
    local_timezone = timezone.utc
    scraper = DummyScraper()

    def get_horse_by_performance(self, performance):
        return None

    def get_horse_by_runner(self, runner):
        return None

    def get_jockey_by_performance(self, performance):
        return None

    def get_jockey_by_runner(self, runner):
        return None

    def get_meet_by_race(self, race):
        return None

    def get_performances_by_horse(self, horse):
        return PerformanceList()

    def get_race_by_runner(self, runner):
        return None

    def get_races_by_meet(self, meet):
        return []

    def get_runners_by_race(self, race):
        return []

    def get_trainer_by_runner(self, runner):
        return None


def parse_datetime(value):
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def parse_optional_float(value):
    return None if value == "" else float(value)


def parse_optional_int(value):
    return None if value == "" else int(value)


def format_value(value):
    if value is None:
        return ""

    if isinstance(value, float):
        return f"{value:.6f}".rstrip("0").rstrip(".")

    return str(value)


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description="Build a local feature table from runner history CSV data."
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


def load_runner_groups(input_path):
    validate_input_path(input_path)

    groups = defaultdict(list)

    with input_path.open(newline="", encoding="utf-8") as input_file:
        reader = csv.DictReader(input_file)
        validate_csv_headers(reader.fieldnames, input_path)

        for row in reader:
            groups[row["runner_id"]].append(row)

    if not groups:
        raise InputValidationError(f"Input CSV contains no data rows: {input_path}")

    return groups


def build_runner(provider, runner_id, rows):
    base_row = rows[0]

    meet = Meet(
        provider,
        None,
        {
            "date": parse_datetime(base_row["race_date"]),
            "track": base_row["race_track"],
            "scraper_version": "file-example",
        },
    )

    race = Race(
        provider,
        {"meet": meet},
        {
            "number": parse_optional_int(base_row["race_number"]),
            "distance": parse_optional_int(base_row["race_distance"]),
            "track": base_row["race_track"],
            "track_condition": base_row["race_track_condition"],
            "track_circ": parse_optional_float(base_row["race_track_circ"]),
            "track_straight": parse_optional_float(base_row["race_track_straight"]),
            "start_time": parse_datetime(base_row["race_start_time"]),
            "scraper_version": "file-example",
        },
    )

    performances = PerformanceList()
    for row in rows:
        performances.append(
            Performance(
                provider,
                None,
                {
                    "date": parse_datetime(row["performance_date"]),
                    "track": row["performance_track"],
                    "horse_url": base_row["horse_url"],
                    "jockey_url": row["performance_jockey_url"],
                    "result": parse_optional_int(row["performance_result"]),
                    "starting_price": parse_optional_float(row["performance_starting_price"]),
                    "prize_pool": parse_optional_float(row["performance_prize_pool"]),
                    "prize_money": parse_optional_float(row["performance_prize_money"]),
                    "starters": parse_optional_int(row["performance_starters"]),
                    "distance": parse_optional_int(row["performance_distance"]),
                    "track_condition": row["performance_track_condition"],
                    "barrier": parse_optional_int(row["performance_barrier"]),
                    "lengths": parse_optional_float(row["performance_lengths"]),
                    "carried": parse_optional_float(row["performance_carried"]),
                    "weight": parse_optional_float(row["performance_weight"]),
                    "winning_time": parse_optional_float(row["performance_winning_time"]),
                    "scraper_version": "file-example",
                },
            )
        )

    horse = Horse(
        provider,
        {"performances": performances},
        {
            "name": base_row["horse_name"],
            "url": base_row["horse_url"],
            "scraper_version": "file-example",
        },
    )

    for performance in performances:
        performance.property_cache["horse"] = horse

    runner = Runner(
        provider,
        {"race": race, "horse": horse},
        {
            "runner_id": runner_id,
            "number": parse_optional_int(base_row["runner_number"]),
            "horse_url": base_row["horse_url"],
            "jockey_url": base_row["runner_jockey_url"],
            "weight": parse_optional_float(base_row["runner_weight"]),
            "jockey_claiming": parse_optional_float(base_row["runner_jockey_claiming"]),
            "barrier": parse_optional_int(base_row["runner_barrier"]),
            "scraper_version": "file-example",
        },
    )

    return runner


def build_feature_row(runner_id, runner):
    current_performance = runner.current_performance
    previous_performance = runner.previous_performance
    race_date = runner.race.meet["date"].date().isoformat()
    race_track = runner.race.meet["track"]
    race_distance = runner.race["distance"]

    return {
        "runner_id": runner_id,
        "horse_name": runner.horse["name"],
        "race_date": race_date,
        "race_track": race_track,
        "race_distance": race_distance,
        "race_key": f"{race_date}_{race_track}_{race_distance}",
        "runner_number": runner["number"],
        "carrying": runner.carrying,
        "actual_weight": runner.actual_weight,
        "actual_distance": runner.actual_distance,
        "career_starts": runner.career.starts,
        "career_wins": runner.career.wins,
        "career_places": runner.career.places,
        "career_win_pct": runner.career.win_pct,
        "career_second_pct": runner.career.second_pct,
        "career_third_pct": runner.career.third_pct,
        "career_roi": runner.career.roi,
        "career_earnings": runner.career.earnings,
        "career_earnings_potential": runner.career.earnings_potential,
        "career_result_potential": runner.career.result_potential,
        "last_10_wins": runner.last_10.wins,
        "last_10_places": runner.last_10.places,
        "last_10_win_pct": runner.last_10.win_pct,
        "last_10_place_pct": runner.last_10.place_pct,
        "last_10_starts": runner.last_10.starts,
        "last_12_months_starts": runner.last_12_months.starts,
        "at_distance_starts": runner.at_distance.starts,
        "at_distance_win_pct": runner.at_distance.win_pct,
        "on_track_starts": runner.on_track.starts,
        "on_track_win_pct": runner.on_track.win_pct,
        "on_good_starts": runner.on_good.starts,
        "on_good_win_pct": runner.on_good.win_pct,
        "on_soft_starts": runner.on_soft.starts,
        "on_soft_win_pct": runner.on_soft.win_pct,
        "with_jockey_starts": runner.with_jockey.starts,
        "with_jockey_win_pct": runner.with_jockey.win_pct,
        "starting_price": runner.starting_price,
        "result": runner.result,
        "current_performance_profit": current_performance.profit if current_performance is not None else None,
        "previous_performance_result": previous_performance.get("result") if previous_performance is not None else None,
        "previous_performance_starting_price": previous_performance.get("starting_price") if previous_performance is not None else None,
        "spell_days": runner.spell,
        "up": runner.up,
    }


def write_feature_table(feature_rows, output_path):
    output_path.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = list(feature_rows[0].keys())
    with output_path.open("w", newline="", encoding="utf-8") as output_file:
        writer = csv.DictWriter(output_file, fieldnames=fieldnames)
        writer.writeheader()
        for row in feature_rows:
            writer.writerow({key: format_value(value) for key, value in row.items()})


def main(argv=None):
    args = parse_args(argv)
    provider = LocalFileProvider()
    input_path = resolve_repo_path(args.input)
    output_path = resolve_repo_path(args.output)
    groups = load_runner_groups(input_path)

    feature_rows = []
    for runner_id, rows in sorted(groups.items()):
        runner = build_runner(provider, runner_id, rows)
        feature_rows.append(build_feature_row(runner_id, runner))

    write_feature_table(feature_rows, output_path)
    print(f"Wrote {len(feature_rows)} feature rows to {output_path}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except InputValidationError as error:
        print(f"Error: {error}", file=sys.stderr)
        raise SystemExit(1)
