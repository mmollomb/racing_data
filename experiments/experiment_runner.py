from racing_data.runner import Runner
from racing_data.race import Race


class DummyProvider:
    def get_race_by_runner(self, runner):
        return None


provider = DummyProvider()

race = Race(
    provider,
    None,
    {
        "distance": 1200,
        "track_circ": None,
        "track_straight": None,
        "scraper_version": "test",
    },
)

runner = Runner(
    provider,
    {"race": race},
    {
        "number": 1,
        "weight": 56.5,
        "jockey_claiming": 1.5,
        "barrier": 4,
        "scraper_version": "test",
    },
)

print("carrying:", runner.carrying)
print("actual_weight:", runner.actual_weight)
print("actual_distance:", runner.actual_distance)