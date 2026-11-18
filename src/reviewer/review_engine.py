
from src.reviewer.specification_checker import check_specification
from src.reviewer.consistency_checker import (
    check_requirement_workflow_consistency
)
from src.reviewer.code_checker import check_code_snippet
from src.workflow.graph_checker import (
    check_workflow_graph,
    WorkflowGraphError
)
from src.requirements.effective_requirements import (
    derive_effective_requirements
)
from src.model.review_pipeline import run_model_review


def run_full_review(
    client,
    requirements,
    specification,
    workflow,
    code_snippets=None,
    approvals=None,
    enable_workflow_consistency=True
):
    code_snippets = code_snippets or []
    approvals = approvals or []

    findings = []
    incomplete = False

    # 1. Apply approved requirement changes.
    try:
        effective_requirements = derive_effective_requirements(
            requirements, approvals
        )
    except Exception as exc:
        return {
            "status": "INCOMPLETE",
            "summary": "Could not determine effective requirements.",
            "findings": [{
                "type": "APPROVAL_ERROR",
                "message": str(exc),
                "evidence": "Approved changes could not be safely applied."
            }]
        }

    # 2. Check requirements against specification.
    try:
        specification_result = check_specification(
            effective_requirements,
            specification
        )
        findings.extend(specification_result["findings"])

    except Exception as exc:
        incomplete = True
        findings.append({
            "type": "SPECIFICATION_CHECK_FAILED",
            "message": str(exc),
            "evidence": "Specification consistency check could not finish."
        })

    # 3. Check workflow graph.
    try:
        graph_result = check_workflow_graph(workflow)

        if not graph_result["valid"]:
            for error in graph_result["errors"]:
                findings.append({
                    "type": "WORKFLOW_GRAPH_ERROR",
                    "message": error,
                    "evidence": "Workflow graph validation failed."
                })

    except WorkflowGraphError as exc:
        findings.append({
            "type": "WORKFLOW_GRAPH_ERROR",
            "message": str(exc),
            "evidence": "Workflow contains invalid graph references."
        })

    except Exception as exc:
        incomplete = True
        findings.append({
            "type": "WORKFLOW_CHECK_FAILED",
            "message": str(exc),
            "evidence": "Workflow graph check could not finish."
        })

    # 4. Workflow consistency check or controlled ablation.
    if enable_workflow_consistency:
        try:
            consistency_result = check_requirement_workflow_consistency(
                requirements,
                workflow,
                approvals
            )

            findings.extend(consistency_result["findings"])

            if consistency_result["status"] == "INCOMPLETE":
                incomplete = True

        except Exception as exc:
            incomplete = True
            consistency_result = {
                "status": "INCOMPLETE",
                "findings": []
            }
            findings.append({
                "type": "CONSISTENCY_CHECK_FAILED",
                "message": str(exc),
                "evidence": "Requirement-workflow consistency check failed."
            })
    else:
        consistency_result = {
            "status": "SKIPPED",
            "findings": []
        }

    # 5. Check linked code snippets.
    requirement_map = {
        item.rule_id: item
        for item in effective_requirements
    }

    for snippet in code_snippets:
        requirement = requirement_map.get(snippet.rule_id)

        try:
            code_result = check_code_snippet(
                snippet,
                requirement
            )

            code_findings = code_result["findings"]
            findings.extend(code_findings)

            if any(
                finding.get("type") == "UNSUPPORTED_LANGUAGE"
                for finding in code_findings
            ):
                incomplete = True

        except Exception as exc:
            incomplete = True
            findings.append({
                "type": "CODE_CHECK_FAILED",
                "message": str(exc),
                "evidence": f"Could not check snippet {snippet.snippet_id}."
            })

    # 6. Run model review.
    try:
        model_result = run_model_review(
            client=client,
            requirements=requirements,
            specification=specification,
            workflow=workflow,
            code_snippets=code_snippets,
            approvals=approvals
        )

        findings.extend(model_result["findings"])

        if model_result["status"] == "INCOMPLETE":
            incomplete = True

    except Exception as exc:
        incomplete = True
        model_result = {
            "status": "INCOMPLETE",
            "findings": [{
                "type": "MODEL_REVIEW_FAILED",
                "message": str(exc),
                "evidence": "Model review could not complete."
            }]
        }
        findings.extend(model_result["findings"])

    # 7. Determine final review status.
    if incomplete:
        status = "INCOMPLETE"

    elif findings or model_result["status"] == "CHANGES_REQUIRED":
        status = "CHANGES_REQUIRED"

    else:
        status = "PASS"

    return {
        "status": status,
        "summary": f"Full review completed with status: {status}.",
        "findings": findings,
        "checks": {
            "specification": "completed",
            "workflow_graph": "completed",
            "workflow_consistency": consistency_result["status"],
            "code_snippets_checked": len(code_snippets),
            "model_review": model_result["status"]
        }
    }
