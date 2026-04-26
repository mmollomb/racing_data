from modern_tests.helpers import build_runner_form_graph


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