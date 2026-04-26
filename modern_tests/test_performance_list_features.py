from modern_tests.helpers import build_runner_form_graph


def get_performances():
    runner = build_runner_form_graph()
    return runner.horse.performances


def test_performance_list_basic_counts():
    performances = get_performances()

    assert performances.starts == 3
    assert performances.wins == 1
    assert performances.seconds == 0
    assert performances.thirds == 1
    assert performances.fourths == 0
    assert performances.places == 2


def test_performance_list_percentages():
    performances = get_performances()

    assert performances.win_pct == 1 / 3
    assert performances.second_pct == 0
    assert performances.third_pct == 1 / 3
    assert performances.fourth_pct == 0
    assert performances.place_pct == 2 / 3


def test_performance_list_earnings_features():
    performances = get_performances()

    assert performances.earnings == 600
    assert performances.earnings_potential == 0.2


def test_performance_list_starting_price_features():
    performances = get_performances()

    assert performances.starting_prices == (5.0, 10.0, 7.666666666666667)


def test_performance_list_roi_feature():
    performances = get_performances()

    assert performances.roi == 2 / 3


def test_performance_list_momentum_features():
    performances = get_performances()

    assert len(performances.momentums) == 3
    assert round(performances.momentums[0], 6) == round(10457.878520301507, 6)
    assert round(performances.momentums[1], 6) == round(10740.014916656308, 6)
    assert round(performances.momentums[2], 6) == round(10622.045772467378, 6)