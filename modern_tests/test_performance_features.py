from modern_tests.helpers import build_runner_form_graph


def get_first_performance():
    runner = build_runner_form_graph()
    return runner.horse.performances[0]


def get_second_performance():
    runner = build_runner_form_graph()
    return runner.horse.performances[1]


def get_third_performance():
    runner = build_runner_form_graph()
    return runner.horse.performances[2]


def test_performance_profit_for_winner():
    performance = get_first_performance()

    assert performance.profit == 4.0


def test_performance_profit_for_loser():
    performance = get_second_performance()

    assert performance.profit == -1.0


def test_performance_actual_weight():
    performance = get_first_performance()

    assert performance.actual_weight == 626.5


def test_performance_actual_distance_for_winner():
    performance = get_first_performance()

    assert round(performance.actual_distance, 6) == round(1200.0016666655093, 6)


def test_performance_actual_distance_adjusts_for_lengths_behind():
    performance = get_second_performance()

    assert round(performance.actual_distance, 6) == round(1395.2089285429577, 6)


def test_performance_speed():
    performance = get_first_performance()

    assert round(performance.speed, 6) == round(17.14288095236442, 6)


def test_performance_momentum():
    performance = get_first_performance()

    assert round(performance.momentum, 6) == round(10740.014916656308, 6)


def test_performance_spell_and_up():
    third = get_third_performance()
    second = get_second_performance()
    first = get_first_performance()

    assert third.spell is None
    assert third.up == 1
    assert second.spell == 90
    assert second.up == 1
    assert first.spell == 31
    assert first.up == 2