# app/ui/session_state.py
from __future__ import annotations

from typing import Any, Dict, List

import streamlit as st


DEFAULT_API_BASE_URL = "http://localhost:8000"


def init_session_state() -> None:
    defaults = {
        "api_base_url": DEFAULT_API_BASE_URL,
        "selected_page": "Case Intake",
        "current_case_id": None,
        "workflow_summary": None,
        "workflow_state": None,
        "case_history": [],
        "last_error": None,
        "uploaded_text": "",
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def set_workflow_result(summary: Dict[str, Any], state: Dict[str, Any]) -> None:
    st.session_state.workflow_summary = summary
    st.session_state.workflow_state = state
    st.session_state.current_case_id = summary.get("case_id")

    history = st.session_state.case_history
    existing_idx = next(
        (i for i, item in enumerate(history) if item.get("case_id") == summary.get("case_id")),
        None,
    )
    if existing_idx is None:
        history.append(summary)
    else:
        history[existing_idx] = summary

    st.session_state.case_history = history


def clear_last_error() -> None:
    st.session_state.last_error = None


def set_last_error(message: str) -> None:
    st.session_state.last_error = message