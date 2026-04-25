from datetime import datetime
import pytz

from racing_data.horse import Horse
from racing_data.performance import Performance
from racing_data.performance_list import PerformanceList


class DummyScraper:
    def is_compatible_with(self, scraper_version):
        return True


class DummyProvider:
    local_timezone = pytz.timezone("Australia/Sydney")
    scraper = DummyScraper()

    def get_horse_by_performance(self, performance):
        return None

    def get_jockey_by_performance(self, performance):
        return None

    def get_performances_by_horse(self, horse):
        return PerformanceList()


provider = DummyProvider()

performances = PerformanceList(
    [
        Performance(
            provider,
            None,
            {
                "date": datetime(2026, 1, 1, tzinfo=pytz.utc),
                "track": "Albany",
                "horse_url": "horse/test",
                "result": 1,
                "starting_price": 5.0,
                "prize_pool": 1000,
                "prize_money": 500,
                "starters": 10,
                "distance": 1200,
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
                "date": datetime(2026, 2, 1, tzinfo=pytz.utc),
                "track": "Albany",
                "horse_url": "horse/test",
                "result": 3,
                "starting_price": 8.0,
                "prize_pool": 1000,
                "prize_money": 100,
                "starters": 10,
                "distance": 1400,
                "barrier": 5,
                "lengths": 2.0,
                "carried": 57.0,
                "weight": 57.0,
                "winning_time": 82.0,
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
        "scraper_version": "test",
    },
)

print("horse:", horse)
print("starts:", horse.performances.starts)
print("wins:", horse.performances.wins)
print("places:", horse.performances.places)
print("win_pct:", horse.performances.win_pct)
print("place_pct:", horse.performances.place_pct)
print("earnings:", horse.performances.earnings)
print("roi:", horse.performances.roi)
print("momentums:", horse.performances.momentums)