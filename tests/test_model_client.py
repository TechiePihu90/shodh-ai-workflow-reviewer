
import pytest

from src.model.model_client import FakeModelClient


def test_fake_model_returns_default_response():
    client = FakeModelClient()

    result = client.review("Review these requirements.")

    assert result["status"] == "PASS"
    assert result["findings"] == []


def test_fake_model_returns_custom_response():
    response = {
        "status": "CHANGES_REQUIRED",
        "findings": [{"type": "TEST_ERROR"}],
        "summary": "An issue was detected."
    }

    client = FakeModelClient(response)

    result = client.review("Check this workflow.")

    assert result == response


def test_fake_model_rejects_empty_prompt():
    client = FakeModelClient()

    with pytest.raises(ValueError):
        client.review("")


def test_fake_model_rejects_non_string_prompt():
    client = FakeModelClient()

    with pytest.raises(ValueError):
        client.review(None)
