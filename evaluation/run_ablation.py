
import csv
import json
import sys
from pathlib import Path

# Add project root to Python import path.
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from main import load_bundle
from src.model.model_client import FakeModelClient
from src.reviewer.review_engine import run_full_review


INPUT_FILE = ROOT / "evaluation" / "bundles" / "D05.json"
REPORT_DIR = ROOT / "reports"


def run_experiment(enable_consistency):
    (
        requirements,
        specification,
        workflow,
        code_snippets,
        approvals
    ) = load_bundle(INPUT_FILE)

    return run_full_review(
        client=FakeModelClient(),
        requirements=requirements,
        specification=specification,
        workflow=workflow,
        code_snippets=code_snippets,
        approvals=approvals,
        enable_workflow_consistency=enable_consistency
    )


def summarize_result(mode, result):
    findings = result.get("findings", [])

    return {
        "mode": mode,
        "status": result["status"],
        "workflow_consistency": result.get(
            "checks", {}
        ).get("workflow_consistency", "UNKNOWN"),
        "finding_count": len(findings),
        "finding_types": [
            finding.get("type", "UNKNOWN")
            for finding in findings
        ],
        "route_mismatch_detected": any(
            finding.get("type") == "ROUTE_MISMATCH"
            for finding in findings
        )
    }


def main():
    print("Running controlled ablation experiment...")
    print(f"Input: {INPUT_FILE.name}")

    normal_result = run_experiment(True)
    ablation_result = run_experiment(False)

    normal = summarize_result("normal", normal_result)
    ablation = summarize_result("ablation", ablation_result)

    report = {
        "experiment": "Workflow Consistency Checker Ablation",
        "input_bundle": "D05.json",
        "model_client": "FakeModelClient",
        "same_input_for_both_runs": True,
        "normal_run": normal,
        "ablation_run": ablation,
        "comparison": {
            "normal_detected_route_mismatch":
                normal["route_mismatch_detected"],
            "ablation_detected_route_mismatch":
                ablation["route_mismatch_detected"],
            "checker_contribution_demonstrated": (
                normal["route_mismatch_detected"]
                and not ablation["route_mismatch_detected"]
            )
        }
    }

    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    json_path = REPORT_DIR / "ablation_results.json"
    csv_path = REPORT_DIR / "ablation_results.csv"

    with open(json_path, "w", encoding="utf-8") as file:
        json.dump(report, file, indent=2, ensure_ascii=False)

    with open(csv_path, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "mode",
                "status",
                "workflow_consistency",
                "finding_count",
                "finding_types",
                "route_mismatch_detected"
            ]
        )

        writer.writeheader()

        for row in [normal, ablation]:
            csv_row = row.copy()
            csv_row["finding_types"] = ";".join(
                csv_row["finding_types"]
            )
            writer.writerow(csv_row)

    print("\n========== ABLATION RESULTS ==========")

    for row in [normal, ablation]:
        print(f"\nMode: {row['mode']}")
        print(f"Status: {row['status']}")
        print(
            "Workflow consistency:",
            row["workflow_consistency"]
        )
        print("Findings:", row["finding_types"])
        print(
            "Route mismatch detected:",
            row["route_mismatch_detected"]
        )

    print(
        "\nChecker contribution demonstrated:",
        report["comparison"]["checker_contribution_demonstrated"]
    )

    print(f"\nJSON report saved: {json_path}")
    print(f"CSV report saved: {csv_path}")


if __name__ == "__main__":
    main()
