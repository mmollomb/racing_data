import inspect

from racing_data import Horse, Jockey, Trainer, Meet, Race, Runner
from racing_data.entity import Entity
from racing_data.performance import Performance
from racing_data.performance_list import PerformanceList
from racing_data.provider import Provider

classes = [
    Entity,
    Provider,
    Meet,
    Race,
    Runner,
    Horse,
    Jockey,
    Trainer,
    Performance,
    PerformanceList,
]

for cls in classes:
    print("\n" + "=" * 80)
    print(cls.__name__)
    print("=" * 80)

    try:
        print("Signature:", inspect.signature(cls))
    except Exception as exc:
        print("Signature unavailable:", exc)

    print("\nProperties:")
    for name, member in inspect.getmembers(cls):
        if isinstance(member, property):
            print("  -", name)

    print("\nMethods:")
    for name, member in inspect.getmembers(cls, inspect.isfunction):
        if not name.startswith("__"):
            print("  -", name)