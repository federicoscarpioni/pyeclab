from types import SimpleNamespace

from pytest import fixture

from pyeclab.channel.limits import Condition, SoftwareLimitChecker


def _data_info(technique_index: int):
    return SimpleNamespace(TechniqueIndex=technique_index)


def _current_values(**kwargs):
    return SimpleNamespace(**kwargs)


@fixture
def checker():
    return SoftwareLimitChecker()


def test_no_conditions_never_triggers(checker):
    assert checker.check(_current_values(Ewe=10.0), _data_info(0)) is False


def test_add_appends_to_conditions(checker):
    condition = Condition(0, "Ewe", ">", 2.8)
    checker.add(condition)
    assert checker.conditions == [condition]


def test_greater_than_condition_met(checker):
    checker.add(Condition(0, "Ewe", ">", 2.8))
    assert checker.check(_current_values(Ewe=2.8), _data_info(0)) is True
    assert checker.check(_current_values(Ewe=3.0), _data_info(0)) is True


def test_greater_than_condition_not_met(checker):
    checker.add(Condition(0, "Ewe", ">", 2.8))
    assert checker.check(_current_values(Ewe=2.7), _data_info(0)) is False


def test_less_than_condition_met(checker):
    checker.add(Condition(0, "I", "<", 0.001))
    assert checker.check(_current_values(I=0.001), _data_info(0)) is True
    assert checker.check(_current_values(I=0.0001), _data_info(0)) is True


def test_less_than_condition_not_met(checker):
    checker.add(Condition(0, "I", "<", 0.001))
    assert checker.check(_current_values(I=0.002), _data_info(0)) is False


def test_condition_ignored_for_different_technique_index(checker):
    checker.add(Condition(1, "Ewe", ">", 2.8))
    # Same value would trigger the condition, but the running technique (0) does not match.
    assert checker.check(_current_values(Ewe=5.0), _data_info(0)) is False


def test_multiple_conditions_any_match_triggers(checker):
    checker.add(Condition(0, "Ewe", ">", 2.8))
    checker.add(Condition(0, "I", "<", 0.001))
    assert checker.check(_current_values(Ewe=0.0, I=0.0001), _data_info(0)) is True


@fixture
def checker_with_initial_conditions():
    return SoftwareLimitChecker(conditions=[Condition(0, "Ewe", ">", 2.8)])


def test_constructor_accepts_initial_conditions(checker_with_initial_conditions):
    assert checker_with_initial_conditions.check(_current_values(Ewe=3.0), _data_info(0)) is True
