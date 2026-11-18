\# AI Assistance Note



\## 1. Use of AI Assistance



AI assistance was used during the development of the SHODH AI Workflow Requirements Reviewer project.



The assistance focused on:



\- Understanding the assessment requirements and breaking them into implementation tasks.

\- Planning the modular Python project architecture.

\- Drafting and improving Python modules for schemas, condition parsing, workflow validation, and consistency checking.

\- Identifying implementation errors and suggesting debugging approaches.

\- Preparing automated test scenarios and evaluation scripts.

\- Improving project documentation, including the README and engineering note.



\## 2. Human Review and Verification



AI-generated suggestions were not treated as automatically correct.



The implementation was reviewed and tested through:



\- Running Python modules against structured JSON bundles.

\- Executing automated Pytest regression tests.

\- Inspecting review reports and identified counterexamples.

\- Checking expected and actual statuses in evaluation scripts.

\- Verifying approval handling and unsupported-input behavior.



Issues discovered during testing were corrected and regression-tested.



\## 3. Limitations and Transparency



The current implementation uses a fake model client for reproducible offline testing. It does not claim to have completed integration with a production language model.



Evaluation results are based on the documented development and additional validation cases. These cases were inspected during development and are not an independent blind holdout.



AI assistance supported implementation and documentation, while the final project behavior was checked through local execution and automated tests.



\## 4. Responsibility



The project author is responsible for reviewing, understanding, testing, and validating the submitted implementation and its reported results.

