from datetime import datetime

import pytz

from racing_data.entity import Entity


class CompatibleScraper:
    def is_compatible_with(self, scraper_version):
        return scraper_version == "test"


class IncompatibleScraper:
    def is_compatible_with(self, scraper_version):
        return False


class DummyProvider:
    def __init__(self, scraper):
        self.scraper = scraper


def test_entity_adds_created_and_updated_timestamps():
    entity = Entity(
        DummyProvider(CompatibleScraper()),
        None,
        {"scraper_version": "test"},
    )

    assert "created_at" in entity
    assert "updated_at" in entity
    assert entity["created_at"].tzinfo is not None
    assert entity["updated_at"].tzinfo is not None


def test_entity_localizes_naive_datetime_values_to_utc():
    entity = Entity(
        DummyProvider(CompatibleScraper()),
        None,
        {
            "scraper_version": "test",
            "date": datetime(2026, 4, 26),
        },
    )

    assert entity["date"].tzinfo == pytz.utc


def test_entity_keeps_aware_datetime_values():
    aware_date = datetime(2026, 4, 26, tzinfo=pytz.utc)

    entity = Entity(
        DummyProvider(CompatibleScraper()),
        None,
        {
            "scraper_version": "test",
            "date": aware_date,
        },
    )

    assert entity["date"] == aware_date


def test_entity_has_expired_uses_scraper_compatibility():
    compatible_entity = Entity(
        DummyProvider(CompatibleScraper()),
        None,
        {"scraper_version": "test"},
    )

    incompatible_entity = Entity(
        DummyProvider(IncompatibleScraper()),
        None,
        {"scraper_version": "test"},
    )

    assert compatible_entity.has_expired is False
    assert incompatible_entity.has_expired is True


def test_get_cached_property_returns_existing_value_without_calling_source():
    entity = Entity(
        DummyProvider(CompatibleScraper()),
        {"answer": 42},
        {"scraper_version": "test"},
    )

    def source_method():
        raise AssertionError("source_method should not be called")

    assert entity.get_cached_property("answer", source_method) == 42


def test_get_cached_property_calls_source_once_and_caches_value():
    entity = Entity(
        DummyProvider(CompatibleScraper()),
        None,
        {"scraper_version": "test"},
    )

    calls = {"count": 0}

    def source_method():
        calls["count"] += 1
        return "calculated"

    assert entity.get_cached_property("answer", source_method) == "calculated"
    assert entity.get_cached_property("answer", source_method) == "calculated"
    assert calls["count"] == 1