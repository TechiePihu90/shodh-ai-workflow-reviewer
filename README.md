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
- **Model Client Interface:** Provides a model-client interface and a FakeModelClient for reproducible offline testing.
- **Structured Reporting:** Produces PASS, CHANGES_REQUIRED, or INCOMPLETE review results.
- **Interactive Frontend:** Provides a Streamlit interface for uploading JSON bundles, reviewing results, and downloading reports.

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
├── fixtures/
│
├── evaluation/
│   ├── bundles/
│   ├── holdout/
│   │   ├── bundles/
│   │   └── expected_labels.json
│   ├── expected_labels.json
│   ├── run_evaluation.py
│   ├── run_holdout.py
│   └── run_ablation.py
│
├── reports/
├── checkpoints/
└── docs/
    ├── engineering_note.md
    └── ai_assistance_note.md
```

## 5. Technology Stack

- Python 3.11+
- Pydantic
- NetworkX
- Python AST
- Pytest
- Streamlit
- JSON
- CSV

## 6. Installation

Clone or extract the project repository:

```bash
git clone https://github.com/TechiePihu90/shodh-ai-workflow-reviewer.git
cd shodh-ai-workflow-reviewer
```

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

## 8. Running the Streamlit Frontend

Start the interactive application:

```bash
streamlit run src/frontend/app.py
```

The frontend supports:

- Uploading JSON review bundles.
- Previewing input data.
- Running the reviewer.
- Displaying review status and findings.
- Viewing check results and evidence.
- Downloading the JSON review report.

## 9. Running Tests and Offline Evaluation

Run the complete automated test suite:

```bash
python -m pytest tests/ -v
```

Run the development evaluation:

```bash
python evaluation/run_evaluation.py
```

Run additional validation:

```bash
python evaluation/run_holdout.py
```

Run the controlled ablation experiment:

```bash
python evaluation/run_ablation.py
```

### Combined CPU-only offline command

On Windows PowerShell, run the following single command from the project root to execute tests and all evaluation scripts:

```powershell
python -m pytest tests/ -v; if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }; python evaluation/run_evaluation.py; if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }; python evaluation/run_holdout.py; if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }; python evaluation/run_ablation.py; exit $LASTEXITCODE
```

These commands use the local FakeModelClient and do not require a live model API key, GPU, or paid model service.

### Evaluation Dataset

The development evaluation contains 12 cases:

- 3 valid cases.
- 6 defective cases.
- 3 incomplete cases.

The additional validation set contains 4 cases.

Observed results:

| Evaluation | Matched cases | Accuracy |
|---|---:|---:|
| Development evaluation | 12/12 | 100% |
| Additional validation | 4/4 | 100% |

These cases were inspected during development. The additional validation cases are not independent blind holdout results and should not be interpreted as such.

### Ablation Experiment

A controlled ablation experiment was performed using the D05 defective bundle.

- Normal mode: workflow consistency checking enabled.
- Ablation mode: workflow consistency checking disabled.

Observed results:

| Mode | Status | Route mismatch |
|---|---|---|
| Normal | CHANGES_REQUIRED | Detected |
| Ablation | PASS | Not detected |

The experiment demonstrates the contribution of the workflow consistency checker for this test case. The ablation PASS is experimental only because a required check was deliberately skipped.

Machine-readable reports are saved under `reports/`, including JSON and CSV evaluation and ablation outputs.

## 10. Example Business Rules

The sample workflow uses the following ordered rules:

1. Missing category → manual review.
2. Urgent ticket → priority queue.
3. Waiting time greater than or equal to 30 minutes → escalation.
4. Otherwise → normal queue.

Rule order is important because earlier matching rules take precedence.

## 11. Model Client and AI Performance

The project provides a model-client interface and a local FakeModelClient for reproducible testing.

- The current CLI evaluation uses FakeModelClient.
- No live language model was connected during the reported evaluation.
- Semantic model performance was not measured.
- Fake-client evaluation results must not be interpreted as live model performance.
- The prompt and model interface are included in the project.

A real model integration can be added through the model-client interface in a future version.

## 12. Supported Scope and Limitations

- Conditions use a restricted Python expression syntax.
- Supported operations include equality, inequality, numeric comparisons, AND, OR, NOT, and missing-value checks.
- Arbitrary function calls and arbitrary Python execution are not supported.
- Workflow behavioral checking uses a defined set of representative test scenarios; it is not an exhaustive proof of all possible inputs.
- Code inspection is not equivalent to full program execution or formal verification.
- The current model evaluation uses a fake client.
- Evaluation results apply only to the documented test bundles.
- Baseline metrics from a separately executed initial-checkpoint evaluation have not been reported.

Unsupported or ambiguous inputs should be reported rather than silently treated as valid.

## 13. Reproducibility

The project uses fixed JSON evaluation bundles and expected labels. Evaluation scripts generate machine-readable JSON and CSV results.

The initial checkpoint is stored in:

```text
checkpoints/initial_working_checkpoint.zip
```

For reproducible results, use:

- The same Python environment.
- The pinned project dependencies.
- The same input bundles.
- The same expected evaluation labels.
- The same evaluation scripts and configuration.

The reported evaluation uses local CPU execution and does not require external model services.

## 14. Documentation

The `docs/` directory contains:

- `engineering_note.md`: Architecture, supported scope, design decisions, semantic checks, evaluation, debugging examples, and limitations.
- `ai_assistance_note.md`: Material AI assistance used during development and how the implementation was verified.

## 15. Future Improvements

- Expand the existing Streamlit-based interactive review interface.
- Integrate an optional real language model.
- Expand semantic equivalence checking.
- Improve approval and revision conflict handling.
- Strengthen code-to-requirement behavioral analysis.
- Add independently prepared evaluation cases.
- Improve evidence validation and finding-quality metrics.
- Establish a separately measured baseline and final checkpoint comparison.

## 16. Project Purpose

This project was developed as an AI/ML engineering assessment to demonstrate structured requirement analysis, deterministic validation, workflow consistency checking, safe code inspection, model integration interfaces, automated testing, and reproducible evaluation.