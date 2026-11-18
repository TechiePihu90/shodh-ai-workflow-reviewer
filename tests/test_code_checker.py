
from src.schemas.code_snippet import CodeSnippet
from src.schemas.requirement import Requirement
from src.reviewer.code_checker import check_code_snippet


def make_requirement(rule_id="R1", condition=None, action="manual_review"):
    return Requirement(
        rule_id=rule_id,
        description="Test requirement",
        condition=condition or {"expression": "category is None"},
        action=action,
        source_location="policy.txt:R1"
    )


def test_valid_python_code():
    snippet = CodeSnippet(
        snippet_id="S1",
        rule_id="R1",
        code="if category is None:\n    result = 'manual_review'",
        source_location="router.py:1"
    )

    requirement = make_requirement()

    result = check_code_snippet(snippet, requirement)

    assert result["valid"] is True
    assert result["findings"] == []


def test_invalid_python_syntax():
    snippet = CodeSnippet(
        snippet_id="S2",
        rule_id="R2",
        code="if urgent == True print('priority')",
        source_location="router.py:5"
    )

    result = check_code_snippet(snippet)

    assert result["valid"] is False
    assert result["findings"][0]["type"] == "SYNTAX_ERROR"


def test_empty_code():
    snippet = CodeSnippet(
        snippet_id="S3",
        rule_id="R3",
        code="",
        source_location="router.py:10"
    )

    result = check_code_snippet(snippet)

    assert result["valid"] is False
    assert result["findings"][0]["type"] == "EMPTY_CODE"


def test_unsupported_language():
    snippet = CodeSnippet(
        snippet_id="S4",
        rule_id="R4",
        language="javascript",
        code="console.log('hello')",
        source_location="app.js:1"
    )

    result = check_code_snippet(snippet)

    assert result["valid"] is False
    assert result["findings"][0]["type"] == "UNSUPPORTED_LANGUAGE"


def test_wrong_action_detected():
    snippet = CodeSnippet(
        snippet_id="S5",
        rule_id="R1",
        code="result = 'priority_queue'",
        source_location="router.py:15"
    )

    requirement = make_requirement()

    result = check_code_snippet(snippet, requirement)

    assert result["valid"] is False
    assert any(
        item["type"] == "CODE_ACTION_MISMATCH"
        for item in result["findings"]
    )


def test_wrong_rule_action_detected():
    snippet = CodeSnippet(
        snippet_id="S6",
        rule_id="R2",
        code="if urgent == True:\n    result = 'manual_review'",
        source_location="router.py:20"
    )

    requirement = make_requirement(
        rule_id="R2",
        condition={"expression": "urgent == True"},
        action="priority_queue"
    )

    result = check_code_snippet(snippet, requirement)

    assert result["valid"] is False
    assert any(
        item["type"] == "CODE_ACTION_MISMATCH"
        for item in result["findings"]
    )


def test_wrong_condition_detected():
    snippet = CodeSnippet(
        snippet_id="S7",
        rule_id="R1",
        code="if urgent == True:\n    result = 'manual_review'",
        source_location="router.py:25"
    )

    requirement = make_requirement()

    result = check_code_snippet(snippet, requirement)

    assert result["valid"] is False
    assert any(
        item["type"] == "CODE_CONDITION_MISMATCH"
        for item in result["findings"]
    )


def test_dynamic_requirement_for_r3():
    snippet = CodeSnippet(
        snippet_id="S8",
        rule_id="R3",
        code="if waiting_minutes >= 30:\n    result = 'escalation'",
        source_location="router.py:30"
    )

    requirement = make_requirement(
        rule_id="R3",
        condition={"expression": "waiting_minutes >= 30"},
        action="escalation"
    )

    result = check_code_snippet(snippet, requirement)

    assert result["valid"] is True
    assert result["findings"] == []
