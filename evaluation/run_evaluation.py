
import csv
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
BUNDLES_DIR = ROOT / "evaluation" / "bundles"
LABELS_FILE = ROOT / "evaluation" / "expected_labels.json"
REPORTS_DIR = ROOT / "reports" / "evaluation_cases"


def main():
    with open(LABELS_FILE, "r", encoding="utf-8") as file:
        labels = json.load(file)

    cases = labels["cases"]
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    results = []

    for case in cases:
        case_id = case["case_id"]
        expected = case["expected_status"]
        category = case["category"]

        bundle_path = BUNDLES_DIR / f"{case_id}.json"
        report_path = REPORTS_DIR / f"{case_id}_report.json"

        if not bundle_path.exists():
            print(f"Missing bundle: {case_id}")
            actual = "ERROR"
            error = "Bundle file not found."

        else:
            command = [
                sys.executable,
                str(ROOT / "main.py"),
                str(bundle_path),
                "--output",
                str(report_path)
            ]

            try:
                process = subprocess.run(
                    command,
                    cwd=ROOT,
                    capture_output=True,
                    text=True,
                    timeout=60
                )

                if report_path.exists():
                    with open(
                        report_path, "r", encoding="utf-8"
                    ) as file:
                        report = json.load(file)

                    actual = report.get("status", "ERROR")
                    error = ""

                else:
                    actual = "ERROR"
                    error = process.stderr or "Report was not generated."

            except subprocess.TimeoutExpired:
                actual = "ERROR"
                error = "Evaluation timed out."

        results.append({
            "case_id": case_id,
            "category": category,
            "expected": expected,
            "actual": actual,
            "match": expected == actual,
            "error": error
        })

        print(
            f"{case_id}: expected={expected}, "
            f"actual={actual}, match={expected == actual}"
        )

    # Calculate evaluation metrics.
    total = len(results)
    matched = sum(item["match"] for item in results)

    false_passes = sum(
        item["expected"] in ("CHANGES_REQUIRED", "INCOMPLETE")
        and item["actual"] == "PASS"
        for item in results
    )

    false_blocks = sum(
        item["expected"] == "PASS"
        and item["actual"] == "CHANGES_REQUIRED"
        for item in results
    )

    incomplete_by_category = {}

    for item in results:
        if item["actual"] == "INCOMPLETE":
            category = item["category"]
            incomplete_by_category[category] = (
                incomplete_by_category.get(category, 0) + 1
            )

    summary = {
        "total_cases": total,
        "matched_cases": matched,
        "mismatched_cases": total - matched,
        "accuracy": round(matched / total, 4) if total else 0,
        "false_passes": false_passes,
        "false_blocks": false_blocks,
        "incomplete_by_category": incomplete_by_category,
        "results": results
    }

    # Save machine-readable JSON report.
    json_path = ROOT / "reports" / "evaluation_results.json"
    json_path.parent.mkdir(parents=True, exist_ok=True)

    with open(json_path, "w", encoding="utf-8") as file:
        json.dump(summary, file, indent=2, ensure_ascii=False)

    # Save CSV report.
    csv_path = ROOT / "reports" / "evaluation_results.csv"

    with open(csv_path, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "case_id",
                "category",
                "expected",
                "actual",
                "match",
                "error"
            ]
        )
        writer.writeheader()
        writer.writerows(results)

    print("\n========== EVALUATION SUMMARY ==========")
    print(f"Total cases:       {total}")
    print(f"Matched cases:     {matched}")
    print(f"Mismatched cases:  {total - matched}")
    print(f"Accuracy:          {summary['accuracy'] * 100:.2f}%")
    print(f"False passes:      {false_passes}")
    print(f"False blocks:      {false_blocks}")
    print(f"Incomplete counts: {incomplete_by_category}")

    print(f"\nJSON report: {json_path}")
    print(f"CSV report:  {csv_path}")

    return 0 if matched == total else 1


if __name__ == "__main__":
    sys.exit(main())
