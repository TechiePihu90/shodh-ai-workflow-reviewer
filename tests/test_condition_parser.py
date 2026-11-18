import pytest

from src.parser.condition_parser import (
    evaluate_condition,
    ConditionError
)


def test_greater_than_equal():

    ticket = {"waiting_minutes": 30}

    assert evaluate_condition(
        "waiting_minutes >= 30",
        ticket
    ) is True


def test_greater_than():

    ticket = {"waiting_minutes": 35}

    assert evaluate_condition(
        "waiting_minutes > 30",
        ticket
    ) is True


def test_less_than():

    ticket = {"waiting_minutes": 20}

    assert evaluate_condition(
        "waiting_minutes < 30",
        ticket
    ) is True


def test_equality():

    ticket = {"urgent": True}

    assert evaluate_condition(
        "urgent == True",
        ticket
    ) is True


def test_missing_value():

    ticket = {}

    assert evaluate_condition(
        "category is missing",
        ticket
    ) is True


def test_and_condition():

    ticket = {
        "urgent": True,
        "waiting_minutes": 35
    }

    assert evaluate_condition(
        "urgent == True and waiting_minutes >= 30",
        ticket
    ) is True


def test_or_condition():

    ticket = {
        "urgent": False,
        "waiting_minutes": 35
    }

    assert evaluate_condition(
        "urgent == True or waiting_minutes >= 30",
        ticket
    ) is True


def test_not_condition():

    ticket = {"urgent": False}

    assert evaluate_condition(
        "not urgent",
        ticket
    ) is True


def test_nested_condition():

    ticket = {
        "urgent": False,
        "waiting_minutes": 35,
        "category": "billing"
    }

    assert evaluate_condition(
        "(urgent == True or waiting_minutes >= 30) and category == 'billing'",
        ticket
    ) is True


def test_missing_field_comparison():

    ticket = {}

    assert evaluate_condition(
        "waiting_minutes >= 30",
        ticket
    ) is False


def test_invalid_python_is_rejected():

    with pytest.raises(ConditionError):
        evaluate_condition(
            "__import__('os').system('whoami')",
            {}
        )