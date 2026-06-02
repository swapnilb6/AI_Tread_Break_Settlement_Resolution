import json
import httpx
import streamlit as st

from app.config import get_settings

settings = get_settings()

st.set_page_config(
    page_title="Capital Markets Exception Resolution Agent",
    layout="wide",
)

st.title("Capital Markets Trade Break & Settlement Exception Resolution Agent")
st.caption("Phase 1 Foundation UI")

with st.sidebar:
    st.subheader("Environment")
    st.write(f"API Base URL: {settings.api_base_url}")

st.subheader("Case Intake")

default_payload = {
    "raw_text": "Failed settlement for equity trade due to possible SSI mismatch. Counterparty instruction differs from booked settlement account.",
    "source_system": "OPS_PORTAL",
}

payload_text = st.text_area(
    "Incoming exception payload (JSON)",
    value=json.dumps(default_payload, indent=2),
    height=220,
)

col1, col2 = st.columns([1, 3])

with col1:
    submit = st.button("Submit Intake")

if submit:
    try:
        payload = json.loads(payload_text)
        with httpx.Client(timeout=20.0) as client:
            response = client.post(f"{settings.api_base_url}/api/v1/cases/intake", json=payload)
            response.raise_for_status()
            data = response.json()

        st.success("Case intake successful")
        st.json(data)

    except Exception as exc:
        st.error(f"Request failed: {exc}")

st.divider()

st.subheader("Health Checks")

if st.button("Check Services"):
    try:
        with httpx.Client(timeout=10.0) as client:
            response = client.get(f"{settings.api_base_url}/health")
            response.raise_for_status()
            health = response.json()

        st.json(health)
    except Exception as exc:
        st.error(f"Health check failed: {exc}")