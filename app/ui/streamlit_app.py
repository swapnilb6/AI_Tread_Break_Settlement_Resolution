# app/ui/streamlit_app.py
from __future__ import annotations

import json
from typing import Any, Dict, Optional

import streamlit as st

from app.ui.api_client import ApiClientError, WorkflowApiClient
from app.ui.components import (
    render_analytics_dashboard,
    render_approval_panel,
    render_case_timeline,
    render_confidence_timeline,
    render_decision_lineage,
    render_flow_progress,
    render_kpi_row,
    render_parsed_entities,
    render_policy_citations_panel,
    render_recommendation_panel,
    render_retrieved_sources,
    render_root_cause_panel,
    render_similar_cases_panel,
    render_tool_calls,
)
from app.ui.session_state import (
    clear_last_error,
    init_session_state,
    set_last_error,
    set_workflow_result,
)


st.set_page_config(
    page_title="Trade Break & Settlement Exception Resolution Agent",
    page_icon="📈",
    layout="wide",
)


def build_client() -> WorkflowApiClient:
    return WorkflowApiClient(base_url=st.session_state.api_base_url)


def extract_uploaded_text(uploaded_file) -> str:
    if uploaded_file is None:
        return ""

    try:
        content = uploaded_file.read()
        if isinstance(content, bytes):
            return content.decode("utf-8", errors="ignore")
        return str(content)
    except Exception:
        return ""


def load_case_state_if_needed(case_id: str) -> Optional[Dict[str, Any]]:
    """Load and cache case state from backend."""
    if not case_id:
        return None
    client = build_client()
    try:
        state = client.get_case_state(case_id)
        return state if isinstance(state, dict) else None
    except Exception as exc:
        set_last_error(f"Failed to load case state: {str(exc)}")
        return None


def sidebar() -> str:
    with st.sidebar:
        st.title("🎯 Workflow UI")
        
        api_url = st.text_input(
            "API Base URL",
            key="api_base_url",
            help="FastAPI backend base URL (e.g., http://localhost:8000)",
        )
        
        # Health check button
        if st.button("🏥 Check Backend Health", use_container_width=True):
            try:
                client = build_client()
                health = client.health()
                if health and health.get("status") == "ok":
                    st.success(f"✅ Backend healthy: {health}")
                else:
                    st.warning(f"⚠️ Backend status: {health}")
            except Exception as exc:
                st.error(f"❌ Backend unreachable: {str(exc)}")

        pages = [
            "Case Intake",
            "Agent Trace",
            "Case Review",
            "Approval Console",
            "Audit & Analytics",
        ]
        selected_page = st.radio("📄 Navigate", pages, index=pages.index(st.session_state.selected_page))
        st.session_state.selected_page = selected_page

        st.markdown("---")
        st.caption("📋 Current Case")
        st.write(st.session_state.current_case_id or "No case selected")

        if st.button("🔄 Refresh Current Case", use_container_width=True) and st.session_state.current_case_id:
            state = load_case_state_if_needed(st.session_state.current_case_id)
            if state:
                st.session_state.workflow_state = state
                st.session_state.workflow_summary = state.get("final_summary")
                st.success("✅ Case refreshed")
            else:
                st.error("❌ Failed to refresh case")

        return selected_page


def page_case_intake() -> None:
    st.title("Page 1: Case Intake")

    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("Paste Ticket / Email")
        raw_text = st.text_area(
            "Email / Ticket Text",
            height=220,
            placeholder="Paste ticket, email, or ops note text here...",
        )

        uploaded_file = st.file_uploader(
            "Upload supporting file",
            type=["txt", "md", "json", "csv", "log"],
        )
        uploaded_text = extract_uploaded_text(uploaded_file)

        if uploaded_text:
            with st.expander("Uploaded File Preview"):
                st.code(uploaded_text[:5000])

    with col2:
        st.subheader("Structured Hints (Optional)")
        trade_id = st.text_input("Trade ID")
        exception_id = st.text_input("Exception ID")
        counterparty_id = st.text_input("Counterparty ID")
        market = st.text_input("Market")
        notes = st.text_area("Analyst Notes", height=180)

    combined_raw_text = "\n\n".join(
        [part for part in [raw_text, uploaded_text] if part and part.strip()]
    )

    if st.button("Run Investigation", type="primary", use_container_width=True):
        clear_last_error()

        payload = {
            "trade_id": trade_id or None,
            "exception_id": exception_id or None,
            "counterparty_id": counterparty_id or None,
            "market": market or None,
            "notes": notes or None,
            "raw_exception_text": combined_raw_text or raw_text or notes or "",
        }

        with st.spinner("Running end-to-end workflow..."):
            try:
                client = build_client()
                summary = client.run_workflow(payload)
                case_id = summary.get("case_id")
                
                if not case_id:
                    set_last_error("Workflow returned no case_id")
                    st.error(st.session_state.last_error)
                    return
                
                # Fetch full state after workflow completes
                full_state = load_case_state_if_needed(case_id)
                
                if full_state:
                    set_workflow_result(summary, full_state)
                else:
                    set_workflow_result(summary, {"final_summary": summary})

                st.success("✅ Workflow completed successfully.")
                st.info(f"Case ID: {case_id} | Status: {summary.get('workflow_status', 'UNKNOWN')}")
            except Exception as exc:
                error_msg = f"Workflow failed: {str(exc)}"
                set_last_error(error_msg)
                st.error(error_msg)
                return

    if st.session_state.last_error:
        st.error(f"❌ {st.session_state.last_error}")

    if st.session_state.workflow_state:
        st.markdown("---")
        render_parsed_entities(st.session_state.workflow_state)


def page_agent_trace() -> None:
    st.title("Page 2: Agent Trace")

    state = st.session_state.workflow_state
    summary = st.session_state.workflow_summary

    if not state or not summary:
        st.info("Run a case first from Case Intake.")
        return

    render_kpi_row(summary)
    st.markdown("---")
    render_flow_progress(state)

    col1, col2 = st.columns(2)
    with col1:
        render_tool_calls(state)
    with col2:
        render_retrieved_sources(state)

    st.markdown("---")
    render_confidence_timeline(state)


def page_case_review() -> None:
    st.title("Page 3: Case Review")

    state = st.session_state.workflow_state
    if not state:
        st.info("Run a case first from Case Intake.")
        return

    col1, col2 = st.columns(2)
    with col1:
        render_root_cause_panel(state)
        st.markdown("---")
        render_recommendation_panel(state)
    with col2:
        render_policy_citations_panel(state)
        st.markdown("---")
        render_similar_cases_panel(state)


def page_approval_console() -> None:
    st.title("Page 4: Approval Console")

    state = st.session_state.workflow_state
    summary = st.session_state.workflow_summary

    if not state or not summary:
        st.info("Run a case first from Case Intake.")
        return

    render_approval_panel(state)

    requires_human = summary.get("requires_human_approval", False)
    current_status = summary.get("workflow_status")

    if not requires_human or current_status != "PENDING_HUMAN_APPROVAL":
        st.success("✅ This case does not currently require manual approval.")
        return

    st.markdown("---")
    st.subheader("Reviewer Action")

    reviewer_name = st.text_input("Reviewer Name", placeholder="Enter your name")
    reviewer_comments = st.text_area("Reviewer Comments / Edit Notes", height=160, placeholder="Enter decision rationale")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("✅ Approve Case", type="primary", use_container_width=True):
            if not reviewer_name:
                st.warning("Please enter reviewer name.")
                return
            try:
                client = build_client()
                updated_summary = client.submit_approval(
                    case_id=summary["case_id"],
                    approved=True,
                    reviewer_name=reviewer_name,
                    reviewer_comments=reviewer_comments or "Approved in UI.",
                )
                updated_state = load_case_state_if_needed(summary["case_id"])
                if updated_state:
                    set_workflow_result(updated_summary, updated_state)
                else:
                    set_workflow_result(updated_summary, {"final_summary": updated_summary})
                st.success(f"✅ Case approved by {reviewer_name}.")
                st.rerun()
            except Exception as exc:
                error_msg = f"Approval failed: {str(exc)}"
                set_last_error(error_msg)
                st.error(error_msg)

    with col2:
        if st.button("❌ Reject Case", use_container_width=True):
            if not reviewer_name:
                st.warning("Please enter reviewer name.")
                return
            try:
                client = build_client()
                updated_summary = client.submit_approval(
                    case_id=summary["case_id"],
                    approved=False,
                    reviewer_name=reviewer_name,
                    reviewer_comments=reviewer_comments or "Rejected in UI.",
                )
                updated_state = load_case_state_if_needed(summary["case_id"])
                if updated_state:
                    set_workflow_result(updated_summary, updated_state)
                else:
                    set_workflow_result(updated_summary, {"final_summary": updated_summary})
                st.warning(f"⛔ Case rejected by {reviewer_name}.")
                st.rerun()
            except Exception as exc:
                error_msg = f"Rejection failed: {str(exc)}"
                set_last_error(error_msg)
                st.error(error_msg)


def page_audit_analytics() -> None:
    st.title("Page 5: Audit & Analytics")

    state = st.session_state.workflow_state
    if state:
        render_case_timeline(state)
        st.markdown("---")
        render_decision_lineage(state)
        st.markdown("---")

    render_analytics_dashboard(st.session_state.case_history)


def main() -> None:
    init_session_state()
    selected_page = sidebar()

    st.caption("Capital Markets Trade Break & Settlement Exception Resolution Agent")

    if selected_page == "Case Intake":
        page_case_intake()
    elif selected_page == "Agent Trace":
        page_agent_trace()
    elif selected_page == "Case Review":
        page_case_review()
    elif selected_page == "Approval Console":
        page_approval_console()
    elif selected_page == "Audit & Analytics":
        page_audit_analytics()


if __name__ == "__main__":
    main()