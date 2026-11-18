
import json
import sys
from pathlib import Path

import streamlit as st

# Add project root to Python path.
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from src.model.model_client import FakeModelClient
from src.reviewer.review_engine import run_full_review

from src.schemas.requirement import Requirement
from src.schemas.specification import Specification
from src.schemas.workflow import Workflow
from src.schemas.code_snippet import CodeSnippet
from src.schemas.approval import ApprovalRecord


# --------------------------------------------------
# Page configuration
# --------------------------------------------------

st.set_page_config(
    page_title="SHODH AI Reviewer",
    page_icon="🔍",
    layout="wide"
)

st.title("🔍 SHODH AI Reviewer")
st.caption(
    "AI-assisted requirements, specification and workflow validation"
)

st.divider()


# --------------------------------------------------
# Review function
# --------------------------------------------------

def review_bundle(bundle):
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

    result = run_full_review(
        client=FakeModelClient(),
        requirements=requirements,
        specification=specification,
        workflow=workflow,
        code_snippets=code_snippets,
        approvals=approvals
    )

    return result


# --------------------------------------------------
# Sidebar
# --------------------------------------------------

with st.sidebar:
    st.header("About SHODH AI")

    st.write(
        "This application reviews consistency between "
        "business requirements and their technical implementation."
    )

    st.divider()

    st.subheader("Review checks")

    st.write("✓ Requirement validation")
    st.write("✓ Specification checking")
    st.write("✓ Workflow graph validation")
    st.write("✓ Behavioral consistency")
    st.write("✓ Python code inspection")

    st.divider()

    st.caption("Model client: FakeModelClient")
    st.caption("Mode: Local / Offline review")


# --------------------------------------------------
# File upload
# --------------------------------------------------

st.subheader("1. Upload Review Bundle")

uploaded_file = st.file_uploader(
    "Choose a JSON review bundle",
    type=["json"],
    help="Upload a bundle containing requirements, specification and workflow."
)

if uploaded_file is None:
    st.info(
        "Upload a JSON bundle to start the review."
    )

    st.markdown(
        """
        **Expected JSON structure:**

        - `requirements`
        - `specification`
        - `workflow`
        - `code_snippets` (optional)
        - `approvals` (optional)
        """
    )

else:
    try:
        bundle = json.load(uploaded_file)

        if not isinstance(bundle, dict):
            raise ValueError("The JSON root must be an object.")

        required_keys = [
            "requirements",
            "specification",
            "workflow"
        ]

        missing_keys = [
            key for key in required_keys
            if key not in bundle
        ]

        if missing_keys:
            raise ValueError(
                "Missing required fields: "
                + ", ".join(missing_keys)
            )

        st.success("JSON bundle uploaded successfully.")

        with st.expander("Preview uploaded JSON"):
            st.json(bundle)

        st.divider()

        # --------------------------------------------------
        # Run review
        # --------------------------------------------------

        st.subheader("2. Run Review")

        if st.button(
            "🚀 Run Full Review",
            type="primary",
            use_container_width=True
        ):
            with st.spinner("Reviewing your workflow..."):
                try:
                    result = review_bundle(bundle)

                    st.session_state["review_result"] = result
                    st.session_state["review_filename"] = uploaded_file.name

                except Exception as exc:
                    st.session_state.pop("review_result", None)
                    st.error(f"Review failed: {exc}")

    except json.JSONDecodeError:
        st.error("Invalid JSON file. Please upload a valid JSON bundle.")

    except Exception as exc:
        st.error(f"Could not read the uploaded bundle: {exc}")


# --------------------------------------------------
# Display review results
# --------------------------------------------------

if "review_result" in st.session_state:

    result = st.session_state["review_result"]

    st.divider()
    st.subheader("3. Review Results")

    status = result.get("status", "UNKNOWN")

    if status == "PASS":
        st.success("PASS - No blocking inconsistencies detected.")

    elif status == "CHANGES_REQUIRED":
        st.error("CHANGES REQUIRED - Implementation issues detected.")

    elif status == "INCOMPLETE":
        st.warning(
            "INCOMPLETE - The review could not fully complete."
        )

    else:
        st.warning(f"Unknown review status: {status}")

    st.write(result.get("summary", ""))

    findings = result.get("findings", [])

    # Summary metrics
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Review Status", status)

    with col2:
        st.metric("Total Findings", len(findings))

    with col3:
        st.metric(
            "Code Snippets Checked",
            result.get("checks", {}).get(
                "code_snippets_checked", 0
            )
        )

    # Checks
    st.subheader("Review Checks")

    checks = result.get("checks", {})

    if checks:
        check_columns = st.columns(2)

        for index, (check_name, check_status) in enumerate(
            checks.items()
        ):
            with check_columns[index % 2]:
                st.write(
                    f"**{check_name.replace('_', ' ').title()}**"
                )
                st.code(str(check_status))

    # Findings
    st.subheader("Findings")

    if findings:
        for index, finding in enumerate(findings, start=1):

            finding_type = finding.get("type", "UNKNOWN")
            message = finding.get("message", "No message provided.")

            with st.expander(
                f"{index}. {finding_type}: {message}",
                expanded=True
            ):
                st.write("**Evidence**")
                st.write(
                    finding.get(
                        "evidence",
                        "No evidence provided."
                    )
                )

                if finding.get("rule_id"):
                    st.write(
                        f"**Rule ID:** {finding['rule_id']}"
                    )

                if finding.get("source_location"):
                    st.write(
                        "**Source location:** "
                        + str(finding["source_location"])
                    )

                if finding.get("severity"):
                    st.write(
                        f"**Severity:** {finding['severity']}"
                    )

    else:
        st.success("No findings reported.")

    # Download report
    st.divider()
    st.subheader("4. Download Report")

    report_json = json.dumps(
        result,
        indent=2,
        ensure_ascii=False
    )

    st.download_button(
        label="⬇️ Download JSON Report",
        data=report_json,
        file_name="shodh_review_report.json",
        mime="application/json",
        use_container_width=True
    )

    with st.expander("View complete JSON report"):
        st.json(result)
