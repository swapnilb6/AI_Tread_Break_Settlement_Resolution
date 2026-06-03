# app/ui/api_client.py
from __future__ import annotations

from typing import Any, Dict, Optional

import requests


class ApiClientError(Exception):
    pass


class WorkflowApiClient:
    def __init__(self, base_url: str, timeout_seconds: int = 180):
        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds

    def _handle_response(self, response: requests.Response) -> Dict[str, Any]:
        try:
            data = response.json()
        except Exception:
            data = {"raw_text": response.text}

        if response.status_code >= 400:
            raise ApiClientError(
                f"API error {response.status_code}: {data}"
            )
        return data

    def health(self) -> Dict[str, Any]:
        response = requests.get(
            f"{self.base_url}/health",
            timeout=30,
        )
        return self._handle_response(response)

    def run_workflow(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        response = requests.post(
            f"{self.base_url}/api/v1/cases/workflow/run",
            json=payload,
            timeout=self.timeout_seconds,
        )
        return self._handle_response(response)

    def get_case_state(self, case_id: str) -> Dict[str, Any]:
        response = requests.get(
            f"{self.base_url}/api/v1/cases/{case_id}/state",
            timeout=self.timeout_seconds,
        )
        return self._handle_response(response)

    def submit_approval(
        self,
        case_id: str,
        approved: bool,
        reviewer_name: str,
        reviewer_comments: str,
    ) -> Dict[str, Any]:
        response = requests.post(
            f"{self.base_url}/api/v1/cases/{case_id}/approval",
            json={
                "approved": approved,
                "reviewer_name": reviewer_name,
                "reviewer_comments": reviewer_comments,
            },
            timeout=self.timeout_seconds,
        )
        return self._handle_response(response)
