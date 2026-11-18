# SHODH AI – Workflow Requirements Reviewer

An AI-assisted workflow review system that checks consistency between written requirements, structured specifications, workflow graphs, and linked Python code snippets.

## 1. Project Overview

SHODH AI Reviewer helps identify inconsistencies between business requirements and their technical implementation.

The system reviews:
- Written and structured requirements.
- Specification rules, conditions, actions, and priorities.
- Workflow nodes, branches, and execution paths.
- Linked Python code snippets.
- Approved and unapproved requirement changes.

It generates a structured JSON report containing the review status, findings, evidence, and check results.

## 2. Key Features

- **Requirement Validation:** Checks whether specification rules match source requirements.
- **Approval Handling:** Applies approved changes and ignores unapproved suggestions.
- **Specification Checking:** Detects missing rules, condition mismatches, action mismatches, and precedence issues.
- **Workflow Graph Validation:** Checks graph connectivity, unreachable nodes, and invalid destinations.
- **Behavioral Consistency:** Uses representative ticket scenarios to compare expected and actual workflow outcomes.
- **Code Inspection:** Checks supported Python snippets for syntax and selected structural inconsistencies.
- **Safe Condition Evaluation:** Uses Python AST-based evaluation instead of executing arbitrary Python code.
- **Model Client Interface:** Supports a fake model client for reproducible offline testing.
- **Structured Reporting:** Produces PASS, CHANGES_REQUIRED, or INCOMPLETE review results.

## 3. Review Statuses

| Status | Meaning |
|---|---|
| PASS | Review completed within the supported scope without identified blockers. |
| CHANGES_REQUIRED | One or more implementation inconsistencies were detected. |
| INCOMPLETE | Required evidence or supported analysis was unavailable, so a complete review could not be established. |

## 4. Project Structure

```text
shodh-ai-reviewer/
│
├── main.py
├── pyproject.toml
├── requirements.txt
├── README.md
│
├── src/
│   ├── schemas/
│   ├── parser/
│   ├── requirements/
│   ├── workflow/
│   ├── reviewer/
│   ├── model/
│   └── frontend/
│
├── tests/
│
├── fixtures/
│
├── evaluation/
│   ├── bundles/
│   ├── holdout/
│   │   ├── bundles/
│   │   └── expected_labels.json
│   ├── expected_labels.json
│   ├── run_evaluation.py
│   └── run_holdout.py
│
├── reports/
│
├── checkpoints/
│
└── docs/
```

## 5. Technology Stack

- Python 3.11+
- Pydantic
- NetworkX
- Python AST
- Pytest
- JSON
- CSV

## 6. Installation

Clone or extract the project repository.

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it on Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## 7. Running the Reviewer

Run the reviewer against a JSON bundle:

```bash
python main.py evaluation/bundles/V01.json
```

Specify a custom report location:

```bash
python main.py evaluation/bundles/V01.json --output reports/my_report.json
```

The reviewer prints the JSON result and saves a machine-readable report.

Exit codes:

- `0`: PASS
- `1`: CHANGES_REQUIRED
- `2`: INCOMPLETE or review error

## 8. Running Tests

Run the complete automated test suite:

```bash
python -m pytest tests/ -v
```

## 9. Running Evaluation

Run the development evaluation:

```bash
python evaluation/run_evaluation.py
```

Run the additional validation evaluation:

```bash
python evaluation/run_holdout.py
```

Evaluation reports are saved under:

```text
reports/
├── evaluation_results.json
├── evaluation_results.csv
├── holdout_results.json
└── holdout_results.csv
```

The development evaluation currently contains 12 cases:
- 3 valid cases
- 6 defective cases
- 3 incomplete cases

The additional validation set contains 4 cases.

The current observed result is 12/12 matched development cases and 4/4 matched additional validation cases. These cases were inspected during development and should not be interpreted as independent blind holdout performance.

## 10. Example Business Rules

The sample workflow uses the following ordered rules:

1. Missing category → manual review.
2. Urgent ticket → priority queue.
3. Waiting time greater than or equal to 30 minutes → escalation.
4. Otherwise → normal queue.

Rule order is important because earlier matching rules take precedence.

## 11. Supported Scope and Limitations

- Conditions use a restricted Python expression syntax.
- Supported operations include equality, inequality, numeric comparisons, AND, OR, NOT, and missing-value checks.
- Arbitrary function calls and arbitrary Python execution are not supported.
- Workflow behavioral checking uses a defined set of representative test scenarios; it is not an exhaustive proof of all possible inputs.
- Code inspection is not equivalent to full program execution or formal verification.
- The current CLI uses a fake model client for reproducible offline testing.
- The current evaluation results apply only to the documented test bundles.

Unsupported or ambiguous inputs should be reported rather than silently treated as valid.

## 12. Reproducibility

The project uses fixed JSON evaluation bundles and expected labels. The evaluation scripts generate machine-readable JSON and CSV results.

The initial checkpoint is stored in:

```text
checkpoints/initial_working_checkpoint.zip
```

For reproducible results, use the same Python environment, dependencies, input bundles, and evaluation labels.

## 13. Future Improvements

- Streamlit-based interactive review interface.
- Expanded semantic equivalence checking.
- More comprehensive approval and revision conflict handling.
- Stronger code-to-requirement behavioral analysis.
- Additional independently prepared evaluation cases.
- Optional integration with a real language model.
- Improved evidence and finding-quality metrics.

## 14. Project Purpose

This project was developed as an AI/ML engineering assessment to demonstrate structured requirement analysis, deterministic validation, workflow consistency checking, safe code inspection, model integration interfaces, automated testing, and reproducible evaluation.