
import json
from pathlib import Path

from src.schemas.requirement import Requirement
from src.schemas.specification import Specification
from src.reviewer.specification_checker import check_specification


def load_fixture():
    path = (
        Path(__file__).parent.parent
        / "fixtures"
        / "valid_basic.json"
    )

    data = json.loads(path.read_text(encoding="utf-8"))

    requirements = [
        Requirement(**item)
        for item in data["requirements"]
    ]

    specification = Specification(**data["specification"])

    return requirements, specification


def test_valid_specification():
    requirements, specification = load_fixture()

    result = check_specification(requirements, specification)

    assert result["valid"] is True
    assert result["findings"] == []


def test_missing_requirement():
    requirements, specification = load_fixture()

    requirements.append(
        Requirement(
            rule_id="R4",
            description="VIP tickets go to special queue",
            condition={"expression": "vip == True"},
            action="special_queue",
            source_location="policy.txt:R4",
        )
    )

    result = check_specification(requirements, specification)

    assert result["valid"] is False
    assert any(
        finding["type"] == "MISSING_REQUIREMENT"
        for finding in result["findings"]
    )


def test_condition_mismatch():
    requirements, specification = load_fixture()

    specification.rules[2].condition = {
        "expression": "waiting_minutes >= 25"
    }

    result = check_specification(requirements, specification)

    assert any(
        finding["type"] == "CONDITION_MISMATCH"
        for finding in result["findings"]
    )


def test_action_mismatch():
    requirements, specification = load_fixture()

    specification.rules[0].action = "normal_queue"

    result = check_specification(requirements, specification)

    assert any(
        finding["type"] == "ACTION_MISMATCH"
        for finding in result["findings"]
    )


def test_precedence_mismatch():
    requirements, specification = load_fixture()

    specification.rules[0].priority = 2
    specification.rules[1].priority = 1

    result = check_specification(requirements, specification)

    assert any(
        finding["type"] == "PRECEDENCE_MISMATCH"
        for finding in result["findings"]
    )


def test_equivalent_and_condition_order():
    requirements, specification = load_fixture()

    requirements[1].condition = {
        "expression": "urgent == True and vip == True"
    }

    specification.rules[1].condition = {
        "expression": "vip == True and urgent == True"
    }

    result = check_specification(requirements, specification)

    assert not any(
        finding["type"] == "CONDITION_MISMATCH"
        for finding in result["findings"]
    )
def test_threshold_mismatch_detects_d02_defect():
    requirements, specification = load_fixture()

    specification.rules[2].condition = {
        "expression": "waiting_minutes >= 20"
    }

    result = check_specification(requirements, specification)

    assert result["valid"] is False
    assert any(
        finding["type"] == "CONDITION_MISMATCH"
        and finding["rule_id"] == "R3"
        for finding in result["findings"]
    )