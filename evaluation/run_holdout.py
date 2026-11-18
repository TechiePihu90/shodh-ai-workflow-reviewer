
import csv
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

LABELS_FILE = ROOT / "evaluation" / "holdout" / "expected_labels.json"
BUNDLES_DIR = ROOT / "evaluation" / "holdout" / "bundles"
REPORTS_DIR = ROOT / "reports" / "holdout_cases"

RESULT_JSON = ROOT / "reports" / "holdout_results.json"
RESULT_CSV = ROOT / "reports" / "holdout_results.csv"


def main():
    with open(LABELS_FILE, "r", encoding="utf-8") as file:
        labels = json.load(file)

    results = []

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    for case in labels["cases"]:
        case_id = case["case_id"]
        expected = case["expected_status"]

        bundle_file = BUNDLES_DIR / f"{case_id}.json"
        report_file = REPORTS_DIR / f"{case_id}_report.json"

        if not bundle_file.exists():
            results.append({
                "case_id": case_id,
                "category": case["category"],
                "expected": expected,
                "actual": "ERROR",
                "match": False,
                "error": "Bundle file not found"
            })
            continue

        report_file.unlink(missing_ok=True)

        command = [
            sys.executable,
            str(ROOT / "main.py"),
            str(bundle_file),
            "--output",
            str(report_file)
        ]

        try:
            process = subprocess.run(
                command,
                cwd=ROOT,
                capture_output=True,
                text=True,
                timeout=60
            )

            if not report_file.exists():
                raise RuntimeError(
                    process.stderr or "Review report was not generated"
                )

            with open(report_file, "r", encoding="utf-8") as file:
                report = json.load(file)

            actual = report.get("status", "ERROR")

            results.append({
                "case_id": case_id,
                "category": case["category"],
                "expected": expected,
                "actual": actual,
                "match": actual == expected,
                "error": ""
            })

        except Exception as exc:
            results.append({
                "case_id": case_id,
                "category": case["category"],
                "expected": expected,
                "actual": "ERROR",
                "match": False,
                "error": str(exc)
            })

    total = len(results)
    matched = sum(item["match"] for item in results)
    mismatched = total - matched

    false_passes = sum(
        item["category"] == "defective"
        and item["actual"] == "PASS"
        for item in results
    )

    false_blocks = sum(
        item["category"] == "valid"
        and item["actual"] != "PASS"
        for item in results
    )

    summary = {
        "evaluation_type": "additional_validation",
        "total_cases": total,
        "matched_cases": matched,
        "mismatched_cases": mismatched,
        "accuracy_percent": round(
            matched / total * 100, 2
        ) if total else 0,
        "false_passes": false_passes,
        "false_blocks": false_blocks,
        "results": results
    }

    RESULT_JSON.parent.mkdir(parents=True, exist_ok=True)

    with open(RESULT_JSON, "w", encoding="utf-8") as file:
        json.dump(summary, file, indent=2, ensure_ascii=False)

    with open(RESULT_CSV, "w", newline="", encoding="utf-8") as file:
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

    print("\n========== HOLDOUT EVALUATION ==========")

    for item in results:
        print(
            f'{item["case_id"]}: '
            f'expected={item["expected"]}, '
            f'actual={item["actual"]}, '
            f'match={item["match"]}'
        )

    print("\n========== SUMMARY ==========")
    print(f"Total cases:       {total}")
    print(f"Matched cases:     {matched}")
    print(f"Mismatched cases:  {mismatched}")
    print(f"Accuracy:          {summary['accuracy_percent']:.2f}%")
    print(f"False passes:      {false_passes}")
    print(f"False blocks:      {false_blocks}")

    print(f"\nJSON report: {RESULT_JSON}")
    print(f"CSV report:  {RESULT_CSV}")

    return 0 if mismatched == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
