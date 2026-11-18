\# SHODH AI – Engineering Note



\## 1. System Overview



SHODH AI Reviewer is an AI-assisted workflow validation system developed to identify inconsistencies between written business requirements and their technical implementation.



The system reviews four main components:



1\. Source requirements.

2\. Structured specifications.

3\. Workflow graphs.

4\. Linked Python code snippets.



The primary objective is to detect missing requirements, incorrect conditions, action mismatches, precedence errors, workflow routing problems, and unsupported inputs.



The reviewer produces one of three statuses:



\- \*\*PASS:\*\* No blocking inconsistency was identified within the supported review scope.

\- \*\*CHANGES\_REQUIRED:\*\* One or more implementation inconsistencies were detected.

\- \*\*INCOMPLETE:\*\* Required evidence or supported analysis was unavailable.



\## 2. Architecture and Implementation



The system follows a modular Python architecture.



\### 2.1 Input Schemas



Pydantic models define structured inputs for:



\- Requirements

\- Specifications

\- Workflow nodes and branches

\- Code snippets

\- Approval records



This ensures that input bundles follow a predictable structure before review begins.



\### 2.2 Effective Requirements



The effective requirements module applies approved changes in version and revision order.



Only approved changes are applied. Unapproved suggestions are ignored.



The module also checks for conflicting changes and invalid old values before applying revisions.



\### 2.3 Condition Parser



A restricted Python AST-based condition evaluator is used instead of executing arbitrary Python code.



Supported operations include:



\- Equality and inequality.

\- Numeric comparisons.

\- AND and OR conditions.

\- NOT conditions.

\- Missing-value checks.



Unsupported function calls and expressions are rejected rather than executed.



\### 2.4 Specification Checker



The specification checker compares effective requirements against structured specification rules.



It checks:



\- Missing rules.

\- Condition mismatches.

\- Action mismatches.

\- Rule precedence.



The current implementation uses structural AST normalization for selected equivalent expressions. It does not provide complete semantic equivalence verification.



\### 2.5 Workflow Validation



NetworkX is used to represent and validate workflow graphs.



The graph checker identifies:



\- Duplicate node identifiers.

\- Invalid destinations.

\- Missing or multiple start nodes.

\- Unreachable nodes.



A separate behavioral checker follows workflow branches in order and evaluates the selected route.



\### 2.6 Consistency Checker



The consistency checker compares expected behavior from effective requirements with actual workflow routing.



It uses representative ticket scenarios, including missing categories, urgent tickets, and waiting-time boundaries.



When a mismatch is detected, the report includes a counterexample ticket.



This is sampled behavioral testing, not exhaustive verification of every possible input.



\### 2.7 Code Checker



The code checker inspects linked Python snippets.



It checks supported language, Python syntax, and selected structural relationships between conditions and actions.



It does not execute arbitrary submitted Python code. Structural checks are limited and should not be interpreted as proof of complete program behavior.



\### 2.8 Model Client



A model-client interface separates model interaction from deterministic review logic.



A fake model client is currently used for reproducible offline testing.



The model response validator checks response structure, status values, finding fields, and known references where supplied.



The current implementation does not establish factual correctness of every model claim. Real language-model integration remains a future improvement.



\## 3. Safety and Reliability



Several design decisions were made to improve reliability:



\- Arbitrary Python snippets are not executed.

\- Conditions are evaluated using a restricted AST interpreter.

\- Only explicitly approved changes affect effective requirements.

\- Unsupported expressions are reported.

\- Model failures and invalid responses are handled as incomplete reviews.

\- Review reports are generated in machine-readable JSON format.

\- The evaluation labels are kept separate from reviewer inputs.



A PASS result is intended to apply only within the implemented and supported review scope.



\## 4. Debugging and Engineering Improvements



Two substantive debugging examples from development are documented below.



\### Debugging Example 1: Missing Workflow Counterexample



\*\*Problem:\*\*



An urgent ticket with a waiting time of 35 minutes was incorrectly routed to escalation instead of the priority queue.



The original representative scenario set did not adequately expose this precedence issue.



\*\*Diagnosis:\*\*



The requirements specified that urgent tickets must be handled before the waiting-time escalation rule. The workflow behavior checker followed the configured branch order, but the evaluation scenarios did not include this important combination.



\*\*Fix:\*\*



An additional scenario covering an urgent ticket with a waiting time of 35 minutes was added to the consistency checker.



The expected result was derived from the ordered effective requirements and compared against the actual workflow route.



\*\*Regression validation:\*\*



The test suite was updated to cover this scenario. The checker now detects the incorrect route and reports a ROUTE\_MISMATCH with counterexample evidence.



\### Debugging Example 2: Unsupported Language Status



\*\*Problem:\*\*



A code snippet written in JavaScript was initially reported as CHANGES\_REQUIRED, even though the reviewer could not fully inspect that language.



\*\*Diagnosis:\*\*



The code checker correctly identified the unsupported language, but the review engine did not initially treat this finding as a reason to mark the overall review incomplete.



\*\*Fix:\*\*



The review engine was updated to detect UNSUPPORTED\_LANGUAGE findings and set the incomplete-review flag.



This prevents an unsupported code snippet from being treated as a fully reviewed implementation.



\*\*Regression validation:\*\*



The I03 evaluation bundle was rerun and correctly returned INCOMPLETE. The full automated test suite subsequently passed with 71 tests.



\## 5. Evaluation Methodology



The project contains two evaluation groups.



| Evaluation group | Cases | Purpose |

|---|---:|---|

| Development evaluation | 12 | Test and improve reviewer behavior |

| Additional validation | 4 | Check behavior on additional scenarios |



The development evaluation contains:



\- 3 expected PASS cases.

\- 6 expected CHANGES\_REQUIRED cases.

\- 3 expected INCOMPLETE cases.



The additional validation set contains:



\- 3 expected PASS cases.

\- 1 expected INCOMPLETE case.



\### Observed Results



| Metric | Development | Additional validation |

|---|---:|---:|

| Total cases | 12 | 4 |

| Matching outcomes | 12 | 4 |

| Mismatches | 0 | 0 |

| Outcome agreement | 100% | 100% |



The development evaluation recorded zero false passes and zero false blocks against its expected labels.



The additional validation evaluation also recorded zero outcome mismatches.



\*\*Evaluation limitation:\*\* These cases were inspected during development. The additional validation cases are not an untouched independent blind holdout. Therefore, the observed agreement should not be interpreted as independent generalization performance.



The project also includes automated regression tests using Pytest.



\## 6. Current Limitations



The current implementation has the following limitations:



1\. Condition support is restricted to a documented Python expression subset.

2\. Semantic equivalence checking is structural and does not cover all logically equivalent expressions.

3\. Workflow behavior is checked using representative scenarios rather than exhaustive input-space exploration.

4\. Code inspection does not guarantee runtime correctness.

5\. Real language-model integration has not yet been completed; the current CLI uses a fake model client.

6\. Model evidence validation does not independently prove the truth of every model-generated claim.

7\. Evaluation metrics currently focus primarily on outcome agreement and do not fully measure finding quality.



These limitations should be considered when interpreting review results.



\## 7. Future Improvements



Potential improvements include:



\- More comprehensive semantic equivalence checking.

\- Better revision and approval conflict handling.

\- Expanded behavioral test generation.

\- Stronger evidence validation for model-generated findings.

\- Independent blind holdout evaluation.

\- Finding-quality metrics and controlled ablation experiments.

\- Optional integration with a real language model.

\- Streamlit-based graphical interface.



\## 8. Conclusion



SHODH AI Reviewer demonstrates a modular approach to validating consistency across business requirements, specifications, workflow graphs, and linked code.



The implementation combines deterministic validation, safe condition evaluation, workflow analysis, structured model interfaces, automated regression tests, and machine-readable evaluation reports.



The system is designed to report unsupported or incomplete analysis rather than silently treating unverified inputs as correct.



\## 9. Controlled Ablation Experiment



A controlled ablation experiment was performed to measure the contribution of the workflow consistency checker.



\*\*Experimental setup:\*\*



\- Input bundle: D05.json

\- Model client: FakeModelClient

\- Input data and other review settings were kept identical.

\- Normal mode: All review checks enabled.

\- Ablation mode: Workflow consistency checking disabled.



\*\*Observed results:\*\*



| Mode | Review status | Route mismatch |

|---|---|---|

| Normal | CHANGES\_REQUIRED | Detected |

| Ablation | PASS | Not detected |



\*\*Interpretation:\*\*



With the workflow consistency checker enabled, the reviewer detected the incorrect routing behavior in D05 and generated a ROUTE\_MISMATCH finding.



When the checker was disabled, that finding disappeared. This demonstrates that the workflow consistency checker contributed directly to detecting the tested defect.



The PASS status in ablation mode is an experimental output and does not represent a complete review, because workflow consistency was intentionally skipped.



Machine-readable results are available in:



\- reports/ablation\_results.json

\- reports/ablation\_results.csv

