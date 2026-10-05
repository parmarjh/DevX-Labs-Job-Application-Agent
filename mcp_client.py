"""
DevX MCP Client implementation for interacting with DevX Hiring platform tools.
"""

import json
import requests
from typing import Dict, Any, Optional

class DevXMCPClient:
    def __init__(self, base_url: str, token: str):
        self.base_url = base_url.rstrip("/")
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

    def call_tool(self, name: str, arguments: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Calls a tool on the DevX MCP endpoint."""
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": name,
                "arguments": arguments or {}
            }
        }
        try:
            response = requests.post(
                self.base_url,
                headers=self.headers,
                json=payload,
                timeout=30
            )
        except requests.RequestException as e:
            raise RuntimeError(f"Network error connecting to {self.base_url}: {e}")

        if not response.ok:
            error_details = response.text
            try:
                err_json = response.json()
                if isinstance(err_json, dict):
                    error_details = err_json.get("detail") or err_json.get("error") or err_json.get("message") or response.text
            except Exception:
                pass
            raise RuntimeError(f"DevX Server Error ({response.status_code}): {error_details}")

        result = response.json()
        if "error" in result:
            raise RuntimeError(f"MCP Tool Error: {result['error']}")
        return result.get("result", {})

    def get_profile(self) -> Dict[str, Any]:
        """Retrieve candidate profile and target job description."""
        return self.call_tool("get_my_profile")

    def update_profile(self, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update candidate profile attributes."""
        return self.call_tool("update_my_profile", profile_data)

    def get_resume_upload_url(self, filename: str) -> Dict[str, Any]:
        """Get pre-signed S3 upload URL for PDF resume."""
        return self.call_tool("get_resume_upload_url", {"filename": filename})

    def upload_file_to_s3(self, file_path: str, upload_url: str, content_type: str = "application/pdf") -> bool:
        """Uploads a local file directly to AWS S3 using presigned URL."""
        with open(file_path, "rb") as f:
            data = f.read()
        res = requests.put(
            upload_url,
            data=data,
            headers={"Content-Type": content_type},
            timeout=60
        )
        res.raise_for_status()
        return res.status_code == 200

    def get_screening_questions(self) -> Dict[str, Any]:
        """Get mandatory screening questions."""
        return self.call_tool("get_screening_questions")

    def answer_screening_question(self, question_id: str, answer: str) -> Dict[str, Any]:
        """Submit candidate answer for a screening question."""
        return self.call_tool("answer_screening_question", {
            "question_id": question_id,
            "answer": answer
        })

    def get_session_log_url(self) -> Dict[str, Any]:
        """Get upload URL for the markdown session transcript."""
        return self.call_tool("save_session_log")

    def submit_application(self) -> Dict[str, Any]:
        """Finalize and submit the job application."""
        return self.call_tool("submit_application")
