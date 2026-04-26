import csv
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

from racing_data import Horse, Meet, Performance, PerformanceList, Race, Runner


ROOT = Path(__file__).resolve().parents[1]
INPUT_PATH = ROOT / "data" / "examples" / "sample_runner_history.csv"
OUTPUT_PATH = ROOT / "data" / "examples" / "runner_features.csv"


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


def load_runner_groups(input_path):
    groups = defaultdict(list)

    with input_path.open(newline="", encoding="utf-8") as input_file:
        for row in csv.DictReader(input_file):
            groups[row["runner_id"]].append(row)

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
    return {
        "runner_id": runner_id,
        "horse_name": runner.horse["name"],
        "race_date": runner.race.meet["date"].date().isoformat(),
        "race_track": runner.race.meet["track"],
        "race_distance": runner.race["distance"],
        "runner_number": runner["number"],
        "carrying": runner.carrying,
        "actual_weight": runner.actual_weight,
        "actual_distance": runner.actual_distance,
        "career_starts": runner.career.starts,
        "career_wins": runner.career.wins,
        "career_places": runner.career.places,
        "career_win_pct": runner.career.win_pct,
        "last_10_starts": runner.last_10.starts,
        "last_12_months_starts": runner.last_12_months.starts,
        "at_distance_starts": runner.at_distance.starts,
        "on_track_starts": runner.on_track.starts,
        "on_good_starts": runner.on_good.starts,
        "on_soft_starts": runner.on_soft.starts,
        "with_jockey_starts": runner.with_jockey.starts,
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


def main():
    provider = LocalFileProvider()
    groups = load_runner_groups(INPUT_PATH)

    feature_rows = []
    for runner_id, rows in sorted(groups.items()):
        runner = build_runner(provider, runner_id, rows)
        feature_rows.append(build_feature_row(runner_id, runner))

    write_feature_table(feature_rows, OUTPUT_PATH)
    print(f"Wrote {len(feature_rows)} feature rows to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
