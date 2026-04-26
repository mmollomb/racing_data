import math

from modern_tests.helpers import DummyProvider
from racing_data.constants import BARRIER_WIDTH, HORSE_WEIGHT
from racing_data.race import Race
from racing_data.runner import Runner


def build_runner_with_race(runner_data, race_data):
    provider = DummyProvider()

    race_defaults = {
        "distance": 1200,
        "track": "Albany",
        "track_condition": "GOOD",
        "track_circ": None,
        "track_straight": None,
        "scraper_version": "test",
    }

    runner_defaults = {
        "number": 1,
        "horse_url": "horse/test",
        "jockey_url": "jockey/a",
        "weight": 56.5,
        "jockey_claiming": 1.5,
        "barrier": 4,
        "scraper_version": "test",
    }

    race_defaults.update(race_data)
    runner_defaults.update(runner_data)

    race = Race(provider, None, race_defaults)
    return Runner(provider, {"race": race}, runner_defaults)


def test_runner_carrying_subtracts_jockey_claim():
    runner = build_runner_with_race(
        {"weight": 56.5, "jockey_claiming": 1.5},
        {},
    )

    assert runner.carrying == 55.0


def test_runner_carrying_uses_weight_when_no_jockey_claim():
    runner = build_runner_with_race(
        {"weight": 56.5, "jockey_claiming": None},
        {},
    )

    assert runner.carrying == 56.5


def test_runner_carrying_is_none_when_weight_is_none():
    runner = build_runner_with_race(
        {"weight": None, "jockey_claiming": 1.5},
        {},
    )

    assert runner.carrying is None


def test_runner_actual_weight_uses_numeric_carrying():
    runner = build_runner_with_race(
        {"weight": 56.5, "jockey_claiming": 1.5},
        {},
    )

    assert runner.actual_weight == HORSE_WEIGHT + 55.0


def test_runner_actual_weight_falls_back_to_horse_weight_when_carrying_is_none():
    runner = build_runner_with_race(
        {"weight": None, "jockey_claiming": 1.5},
        {},
    )

    assert runner.actual_weight == HORSE_WEIGHT


def test_runner_actual_distance_adjusts_for_barrier_when_present():
    runner = build_runner_with_race(
        {"barrier": 4},
        {"distance": 1200},
    )

    expected_distance = math.sqrt((1200**2) + ((4 * BARRIER_WIDTH) ** 2))

    assert math.isclose(runner.actual_distance, expected_distance)


def test_runner_actual_distance_uses_race_distance_when_barrier_is_none():
    runner = build_runner_with_race(
        {"barrier": None},
        {"distance": 1200},
    )

    assert runner.actual_distance == 1200


def test_runner_actual_distance_is_none_when_race_distance_is_none():
    runner = build_runner_with_race(
        {"barrier": 4},
        {"distance": None},
    )

    assert runner.actual_distance is None
