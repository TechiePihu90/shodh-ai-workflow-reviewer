
import argparse
import json
import sys
from pathlib import Path

from src.reviewer.review_engine import run_full_review
from src.model.model_client import FakeModelClient

from src.schemas.requirement import Requirement
from src.schemas.specification import Specification
from src.schemas.workflow import Workflow
from src.schemas.code_snippet import CodeSnippet
from src.schemas.approval import ApprovalRecord


def load_bundle(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        bundle = json.load(file)

    requirements = [
        Requirement.model_validate(item)
        for item in bundle["requirements"]
    ]

    specification = Specification.model_validate(
        bundle["specification"]
    )

    workflow = Workflow.model_validate(
        bundle["workflow"]
    )

    code_snippets = [
        CodeSnippet.model_validate(item)
        for item in bundle.get("code_snippets", [])
    ]

    approvals = [
        ApprovalRecord.model_validate(item)
        for item in bundle.get("approvals", [])
    ]

    return requirements, specification, workflow, code_snippets, approvals


def main():
    parser = argparse.ArgumentParser(
        description="SHODH AI Workflow Reviewer"
    )

    parser.add_argument("input", help="JSON review bundle path")

    parser.add_argument(
        "--output",
        default="reports/review_report.json"
    )

    args = parser.parse_args()

    try:
        (
            requirements,
            specification,
            workflow,
            code_snippets,
            approvals
        ) = load_bundle(args.input)

        result = run_full_review(
            client=FakeModelClient(),
            requirements=requirements,
            specification=specification,
            workflow=workflow,
            code_snippets=code_snippets,
            approvals=approvals
        )

        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as file:
            json.dump(result, file, indent=2, ensure_ascii=False)

        print(json.dumps(result, indent=2, ensure_ascii=False))
        print(f"\nReport saved to: {output_path}")

        if result["status"] == "PASS":
            return 0
        elif result["status"] == "CHANGES_REQUIRED":
            return 1
        return 2

    except Exception as exc:
        print(f"Review failed: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
