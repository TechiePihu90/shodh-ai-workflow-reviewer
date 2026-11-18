
import json

from src.model.prompt_builder import build_review_prompt


def test_prompt_contains_review_instructions():
    prompt = build_review_prompt(
        requirements=[],
        specification={},
        workflow={}
    )

    assert "requirements" in prompt
    assert "workflow" in prompt
    assert "INCOMPLETE" in prompt


def test_prompt_contains_requirement_data():
    requirements = [
        {
            "rule_id": "R1",
            "action": "manual_review"
        }
    ]

    prompt = build_review_prompt(
        requirements=requirements,
        specification={},
        workflow={}
    )

    assert "R1" in prompt
    assert "manual_review" in prompt


def test_prompt_contains_code_snippets():
    snippets = [
        {
            "snippet_id": "S1",
            "rule_id": "R1",
            "code": "result = 'manual_review'"
        }
    ]

    prompt = build_review_prompt(
        requirements=[],
        specification={},
        workflow={},
        code_snippets=snippets
    )

    assert "manual_review" in prompt


def test_prompt_contains_valid_json_data():
    requirements = [
        {"rule_id": "R2", "action": "priority_queue"}
    ]

    prompt = build_review_prompt(
        requirements=requirements,
        specification={},
        workflow={}
    )

    assert json.dumps(
        requirements,
        indent=2,
        ensure_ascii=False
    ) in prompt
