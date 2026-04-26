from datetime import datetime

import pytz

from racing_data.horse import Horse
from racing_data.meet import Meet
from racing_data.performance import Performance
from racing_data.performance_list import PerformanceList
from racing_data.race import Race
from racing_data.runner import Runner


class DummyScraper:
    def is_compatible_with(self, scraper_version):
        return True


class DummyProvider:
    local_timezone = pytz.timezone("Australia/Sydney")
    scraper = DummyScraper()

    def get_race_by_runner(self, runner):
        return None

    def get_meet_by_race(self, race):
        return None

    def get_horse_by_runner(self, runner):
        return None

    def get_jockey_by_runner(self, runner):
        return None

    def get_trainer_by_runner(self, runner):
        return None

    def get_performances_by_horse(self, horse):
        return PerformanceList()

    def get_horse_by_performance(self, performance):
        return None

    def get_jockey_by_performance(self, performance):
        return None


def build_runner_form_graph():
    provider = DummyProvider()

    meet = Meet(
        provider,
        None,
        {
            "date": datetime(2026, 4, 26, tzinfo=pytz.utc),
            "track": "Albany",
            "scraper_version": "test",
        },
    )

    race = Race(
        provider,
        {"meet": meet},
        {
            "distance": 1200,
            "track": "Albany",
            "track_condition": "GOOD",
            "track_circ": None,
            "track_straight": None,
            "start_time": datetime(2026, 4, 26, 5, 0, tzinfo=pytz.utc),
            "scraper_version": "test",
        },
    )

    performances = PerformanceList(
        [
            Performance(
                provider,
                None,
                {
                    "date": datetime(2026, 4, 1, tzinfo=pytz.utc),
                    "track": "Albany",
                    "horse_url": "horse/test",
                    "jockey_url": "jockey/a",
                    "result": 1,
                    "starting_price": 5.0,
                    "prize_pool": 1000,
                    "prize_money": 500,
                    "starters": 10,
                    "distance": 1200,
                    "track_condition": "GOOD",
                    "barrier": 2,
                    "lengths": 0,
                    "carried": 56.5,
                    "weight": 56.5,
                    "winning_time": 70.0,
                    "scraper_version": "test",
                },
            ),
            Performance(
                provider,
                None,
                {
                    "date": datetime(2026, 3, 1, tzinfo=pytz.utc),
                    "track": "Albany",
                    "horse_url": "horse/test",
                    "jockey_url": "jockey/b",
                    "result": 3,
                    "starting_price": 8.0,
                    "prize_pool": 1000,
                    "prize_money": 100,
                    "starters": 10,
                    "distance": 1400,
                    "track_condition": "SOFT",
                    "barrier": 5,
                    "lengths": 2.0,
                    "carried": 57.0,
                    "weight": 57.0,
                    "winning_time": 82.0,
                    "scraper_version": "test",
                },
            ),
            Performance(
                provider,
                None,
                {
                    "date": datetime(2025, 12, 1, tzinfo=pytz.utc),
                    "track": "Bunbury",
                    "horse_url": "horse/test",
                    "jockey_url": "jockey/a",
                    "result": 5,
                    "starting_price": 10.0,
                    "prize_pool": 1000,
                    "prize_money": 0,
                    "starters": 10,
                    "distance": 1200,
                    "track_condition": "GOOD",
                    "barrier": 6,
                    "lengths": 5,
                    "carried": 55.0,
                    "weight": 55.0,
                    "winning_time": 71.0,
                    "scraper_version": "test",
                },
            ),
        ]
    )

    horse = Horse(
        provider,
        {"performances": performances},
        {
            "name": "Test Horse",
            "url": "horse/test",
            "scraper_version": "test",
        },
    )

    for performance in performances:
        performance.property_cache["horse"] = horse

    runner = Runner(
        provider,
        {"race": race, "horse": horse},
        {
            "number": 1,
            "horse_url": "horse/test",
            "jockey_url": "jockey/a",
            "weight": 56.5,
            "jockey_claiming": 1.5,
            "barrier": 4,
            "scraper_version": "test",
        },
    )

    return runner


def test_runner_weight_and_distance_features():
    runner = build_runner_form_graph()

    assert runner.carrying == 55.0
    assert runner.actual_weight == 625.0
    assert round(runner.actual_distance, 6) == round(1200.0066666481482, 6)


def test_runner_career_features():
    runner = build_runner_form_graph()

    assert runner.career.starts == 3
    assert runner.career.wins == 1
    assert runner.career.places == 2
    assert runner.career.win_pct == 1 / 3


def test_runner_recent_and_contextual_features():
    runner = build_runner_form_graph()

    assert runner.last_10.starts == 3
    assert runner.last_12_months.starts == 3
    assert runner.at_distance.starts == 2
    assert runner.on_track.starts == 2
    assert runner.on_good.starts == 2
    assert runner.on_soft.starts == 1
    assert runner.with_jockey.starts == 2


def test_runner_spell_and_up_features():
    runner = build_runner_form_graph()

    assert runner.spell == 25
    assert runner.up == 3