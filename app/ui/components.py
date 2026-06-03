# app/ui/components.py
from __future__ import annotations

from typing import Any, Dict, List

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


FLOW_STAGE_ORDER = [
    "INTAKE",
    "RETRIEVE_CASE_DATA",
    "RETRIEVE_POLICY_CONTEXT",
    "INFER_ROOT_CAUSE",
    "RECOMMEND_ACTION",
    "CHECK_APPROVAL_RULES",
    "REQUEST_HUMAN_APPROVAL",
    "FINALIZE_DRAFT",
    "PERSIST_AUDIT_TRAIL",
    "RETURN_FINAL_SUMMARY",
]


def render_kpi_row(summary: Dict[str, Any]) -> None:
    if not summary:
        st.warning("Summary data not available.")
        return
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Case ID", summary.get("case_id", "N/A"))
    col2.metric("Workflow Status", summary.get("workflow_status", "N/A"))
    col3.metric("Approval Status", summary.get("approval_status", "N/A"))
    col4.metric("Route To", summary.get("route_to", "N/A"))


def render_flow_progress(state: Dict[str, Any]) -> None:
    current_stage = state.get("current_stage", "INTAKE")
    stages_df = pd.DataFrame(
        {
            "stage": FLOW_STAGE_ORDER,
            "position": list(range(1, len(FLOW_STAGE_ORDER) + 1)),
            "completed": [1 if FLOW_STAGE_ORDER.index(stage) <= FLOW_STAGE_ORDER.index(current_stage) else 0 for stage in FLOW_STAGE_ORDER],
        }
    )

    fig = px.bar(
        stages_df,
        x="position",
        y="completed",
        hover_name="stage",
        title="Flow Progress",
        labels={"position": "Stage क्रम", "completed": "Completed"},
    )
    fig.update_xaxes(
        tickmode="array",
        tickvals=stages_df["position"],
        ticktext=stages_df["stage"],
    )
    st.plotly_chart(fig, use_container_width=True)


def render_parsed_entities(state: Dict[str, Any]) -> None:
    if not state:
        st.warning("State data not available.")
        return
    intake = state.get("intake_result") or {}
    entities = intake.get("extracted_entities") or {}
    missing_fields = intake.get("missing_fields") or []

    st.subheader("Parsed Case")
    c1, c2, c3 = st.columns(3)
    c1.write(f"**Exception Type:** {intake.get('exception_type', 'N/A')}")
    c2.write(f"**Confidence:** {intake.get('exception_type_confidence', 'N/A')}")
    c3.write(f"**Risk:** {intake.get('risk', 'N/A')}")

    st.write(f"**Normalized Summary:** {intake.get('normalized_summary', 'N/A')}")

    st.markdown("**Extracted Entities**")
    if entities:
        st.json(entities)
    else:
        st.info("No extracted entities available.")

    if missing_fields:
        st.warning(f"Missing fields: {', '.join(missing_fields)}")

    if intake.get("suspected_prompt_injection"):
        st.error("Prompt injection / adversarial note suspected.")

    if not state:
        st.info("No state available.")
        return

def render_tool_calls(state: Dict[str, Any]) -> None:
    st.subheader("Tool Calls")

    case_context = state.get("case_context") or {}
    rag_context = state.get("rag_context") or {}

    traces = []
    traces.extend(case_context.get("tool_trace") or [])
    traces.extend(rag_context.get("tool_trace") or [])

    if not traces:
        st.info("No tool trace available.")
        return

    df = pd.DataFrame(traces)
    st.dataframe(df, use_container_width=True)

    if not state:
        st.info("No state available.")
        return

def render_retrieved_sources(state: Dict[str, Any]) -> None:
    st.subheader("Retrieved Sources")

    sources = []
    case_context = state.get("case_context") or {}
    rag_context = state.get("rag_context") or {}

    sources.extend(case_context.get("evidence_refs") or [])
    sources.extend(rag_context.get("evidence_refs") or [])

    if not sources:
        st.info("No evidence references available.")
        return

    st.dataframe(pd.DataFrame(sources), use_container_width=True)


def render_confidence_timeline(state: Dict[str, Any]) -> None:
    st.subheader("Confidence Timeline")
    if not state:
        st.info("No state available.")
        return
    intake = state.get("intake_result") or {}
    root = state.get("root_cause") or {}
    rec = state.get("recommendation") or {}

    points = [
        {"stage": "Intake", "confidence": intake.get("exception_type_confidence")},
        {"stage": "Root Cause", "confidence": root.get("confidence")},
        {"stage": "Recommendation", "confidence": rec.get("confidence")},
    ]
    df = pd.DataFrame([p for p in points if p["confidence"] is not None])

    if df.empty:
        st.info("Confidence data not available.")
        return

    fig = px.line(
        df,
        x="stage",
        y="confidence",
        markers=True,
        title="Confidence Timeline",
        labels={"stage": "Stage", "confidence": "Confidence"},
    )
    fig.update_yaxes(range=[0, 1])
    st.plotly_chart(fig, use_container_width=True)


def render_root_cause_panel(state: Dict[str, Any]) -> None:
    root = state.get("root_cause") or {}
    st.subheader("Root Cause")
    st.write(f"**Likely Root Cause:** {root.get('likely_root_cause', 'N/A')}")
    st.write(f"**Confidence:** {root.get('confidence', 'N/A')}")
    st.write("**Contributing Factors**")
    st.write(root.get("contributing_factors") or [])
    st.write("**Alternative Causes**")
    st.write(root.get("alternative_causes") or [])
    unresolved = root.get("unresolved_conflicts") or []
    if unresolved:
        st.warning("Unresolved Conflicts")
        st.write(unresolved)


def render_recommendation_panel(state: Dict[str, Any]) -> None:
    rec = state.get("recommendation") or {}
    st.subheader("Recommendation")
    st.write(f"**Action Code:** {rec.get('action_code', 'N/A')}")
    st.write(f"**Title:** {rec.get('action_title', 'N/A')}")
    st.write(f"**Summary:** {rec.get('action_summary', 'N/A')}")
    st.write(f"**Confidence:** {rec.get('confidence', 'N/A')}")

    st.markdown("**Action Steps**")
    for step in rec.get("action_steps") or []:
        st.markdown(f"- {step}")

    st.markdown("**Side Effects**")
    st.write(
        {
            "booking_correction_required": rec.get("booking_correction_required"),
            "settlement_instruction_change_required": rec.get("settlement_instruction_change_required"),
            "external_communication_required": rec.get("external_communication_required"),
        }
    )

    warnings = rec.get("warnings") or []
    if not state:
        st.info("No state available.")
        return
    if warnings:
        st.warning("\n".join(warnings))


def render_policy_citations_panel(state: Dict[str, Any]) -> None:
    st.subheader("Policy Citations")
    rag_context = state.get("rag_context") or {}
    policies = rag_context.get("retrieved_policies") or []

    if not policies:
        st.info("No policy citations retrieved.")
        return

    for idx, policy in enumerate(policies, start=1):
        with st.expander(f"{idx}. {policy.get('doc_name', 'Unknown Doc')} | {policy.get('section_heading', 'No Section')}"):
            st.write(f"**Relevance:** {policy.get('relevance_score', 'N/A')}")
            st.write(f"**Type:** {policy.get('doc_type', 'N/A')}")
            st.write(f"**Version:** {policy.get('version', 'N/A')}")
            st.write(f"**Effective Date:** {policy.get('effective_date', 'N/A')}")
            st.code(policy.get("excerpt", ""), language="markdown")

    contradictions = rag_context.get("policy_contradictions") or []
    if contradictions:
        st.warning("Policy Contradictions")
        st.write(contradictions)


def render_similar_cases_panel(state: Dict[str, Any]) -> None:
    st.subheader("Similar Historical Cases")
    case_context = state.get("case_context") or {}
    similar_cases = case_context.get("similar_cases") or []

    if not state:
        st.info("No state available.")
        return
    if not similar_cases:
        st.info("No similar historical cases found.")
        return

    st.dataframe(pd.DataFrame(similar_cases), use_container_width=True)


def render_approval_panel(state: Dict[str, Any]) -> None:
    st.subheader("Approval Snapshot")
    approval = state.get("approval_decision") or {}
    st.write(f"**Status:** {approval.get('status', 'N/A')}")
    st.write(f"**Requires Human Approval:** {approval.get('requires_human_approval', 'N/A')}")
    st.write(f"**Route To:** {approval.get('route_to', 'N/A')}")

    reasons = approval.get("reasons") or []
    if reasons:
        st.warning("Approval Reasons")
        for reason in reasons:
            st.markdown(f"- {reason}")
    if not state:
        st.info("No state available.")
        return
    events = state.get("event_log") or []
    checks = approval.get("policy_checks") or []
    if checks:
        st.markdown("**Policy Checks**")
        st.dataframe(pd.DataFrame(checks), use_container_width=True)


def render_case_timeline(state: Dict[str, Any]) -> None:
    st.subheader("Case Timeline")
    if not state:
        st.info("No state available.")
        return
    events = state.get("event_log") or []
    if not events:
        st.info("No event log available.")
        return

    df = pd.DataFrame(events)
    st.dataframe(df, use_container_width=True)


def render_decision_lineage(state: Dict[str, Any]) -> None:
    st.subheader("Decision Lineage")

    lineage = [
        {
            "step": "Intake Classification",
            "value": (state.get("intake_result") or {}).get("exception_type"),
            "confidence": (state.get("intake_result") or {}).get("exception_type_confidence"),
        },
        {
            "step": "Root Cause",
            "value": (state.get("root_cause") or {}).get("likely_root_cause"),
            "confidence": (state.get("root_cause") or {}).get("confidence"),
        },
        {
            "step": "Recommendation",
            "value": (state.get("recommendation") or {}).get("action_title"),
            "confidence": (state.get("recommendation") or {}).get("confidence"),
        },
        {
            "step": "Approval Decision",
            "value": (state.get("approval_decision") or {}).get("status"),
            "confidence": None,
        },
    ]

    st.dataframe(pd.DataFrame(lineage), use_container_width=True)


def render_analytics_dashboard(history: List[Dict[str, Any]]) -> None:
    st.subheader("📊 Evaluation Dashboard")

    if not history:
        st.info("No session analytics available yet. Run cases first.")
        return

    df = pd.DataFrame(history)

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Cases", len(df))
    
    approval_count = 0
    pending_count = 0
    
    if "approval_status" in df:
        approval_count = int((df["approval_status"] == "AUTO_APPROVED").sum())
    if "workflow_status" in df:
        pending_count = int((df["workflow_status"] == "PENDING_HUMAN_APPROVAL").sum())
    
    col2.metric("Auto Approved", approval_count)
    col3.metric("Pending Approval", pending_count)

    if "workflow_status" in df and not df["workflow_status"].isna().all():
        try:
            fig1 = px.histogram(df, x="workflow_status", title="Workflow Status Distribution")
            st.plotly_chart(fig1, use_container_width=True)
        except Exception as e:
            st.warning(f"Could not render workflow status chart: {e}")

    if "route_to" in df and not df["route_to"].isna().all():
        try:
            fig2 = px.histogram(df, x="route_to", title="Escalation / Route Distribution")
            st.plotly_chart(fig2, use_container_width=True)
        except Exception as e:
            st.warning(f"Could not render route distribution chart: {e}")

    if "root_cause_confidence" in df and df["root_cause_confidence"].notna().any():
        try:
            fig3 = px.box(df, y="root_cause_confidence", title="Root Cause Confidence Distribution")
            st.plotly_chart(fig3, use_container_width=True)
        except Exception as e:
            st.warning(f"Could not render root cause confidence chart: {e}")

    if "recommendation_confidence" in df and df["recommendation_confidence"].notna().any():
        try:
            fig4 = px.box(df, y="recommendation_confidence", title="Recommendation Confidence Distribution")
            st.plotly_chart(fig4, use_container_width=True)
        except Exception as e:
            st.warning(f"Could not render recommendation confidence chart: {e}")

def render_historical_cases_memory(state: Dict[str, Any]) -> None:
    st.subheader("Historical Memory: Similar Resolved Cases")
    memory = state.get("memory_context") or {}
    cases = memory.get("episodic_cases") or []
    if not cases:
        st.info("No historical similar cases available.")
        return
    st.dataframe(pd.DataFrame(cases), use_container_width=True)

def render_approval_history_memory(state: Dict[str, Any]) -> None:
    st.subheader("Approval Memory")
    memory = state.get("memory_context") or {}
    approval_history = memory.get("approval_history") or []
    stats = memory.get("approval_pattern_stats") or {}

    if stats:
        c1, c2, c3 = st.columns(3)
        c1.metric("Total Reviews", stats.get("total_reviews", 0))
        c2.metric("Approval Rate", round(stats.get("approval_rate", 0.0) * 100, 1))
        c3.metric("Override Rate", round(stats.get("override_rate", 0.0) * 100, 1))

    if approval_history:
        st.dataframe(pd.DataFrame(approval_history), use_container_width=True)
    else:
        st.info("No approval history available.")

    hints = memory.get("recommendation_hints") or []
    notes = memory.get("safety_notes") or []

    if hints:
        st.markdown("**Historical Recommendation Hints**")
        for hint in hints:
            st.markdown(f"- {hint}")

    if notes:
        st.warning("\n".join(notes))