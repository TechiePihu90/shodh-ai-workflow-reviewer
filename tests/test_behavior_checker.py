
import json
from pathlib import Path

from src.schemas.workflow import Workflow
from src.workflow.behavior_checker import route_ticket


def load_workflow():
    fixture_path = (
        Path(__file__).parent.parent
        / "fixtures"
        / "valid_basic.json"
    )

    with open(fixture_path, encoding="utf-8") as file:
        data = json.load(file)

    return Workflow.model_validate(data["workflow"])


def test_missing_category_goes_to_manual_review():
    result = route_ticket(load_workflow(), {
        "urgent": True,
        "waiting_minutes": 40
    })
    assert result == "manual_review"


def test_urgent_ticket_goes_to_priority_queue():
    result = route_ticket(load_workflow(), {
        "category": "billing",
        "urgent": True,
        "waiting_minutes": 10
    })
    assert result == "priority_queue"


def test_waiting_30_minutes_goes_to_escalation():
    result = route_ticket(load_workflow(), {
        "category": "billing",
        "urgent": False,
        "waiting_minutes": 30
    })
    assert result == "escalation"


def test_normal_ticket_goes_to_normal_queue():
    result = route_ticket(load_workflow(), {
        "category": "billing",
        "urgent": False,
        "waiting_minutes": 10
    })
    assert result == "normal_queue"


def test_missing_category_has_priority_over_urgent():
    result = route_ticket(load_workflow(), {
        "urgent": True,
        "waiting_minutes": 60
    })
    assert result == "manual_review"
