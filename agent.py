"""
Automated Job Application Agent for DevX Labs.
"""

import os
from typing import Dict, Any
from mcp_client import DevXMCPClient

class DevXJobAgent:
    def __init__(self, client: DevXMCPClient):
        self.client = client

    def sync_candidate_profile(self, profile: Dict[str, Any]) -> Dict[str, Any]:
        """Validates and updates profile fields in DevX database."""
        print(f"[*] Syncing profile for candidate: {profile.get('name', 'Unknown')}")
        return self.client.update_profile(profile)

    def upload_resume(self, resume_path: str) -> str:
        """Requests S3 upload URL, uploads file, and updates resume S3 key."""
        if not os.path.exists(resume_path):
            raise FileNotFoundError(f"Resume file not found at: {resume_path}")

        filename = os.path.basename(resume_path)
        print(f"[*] Requesting S3 upload URL for: {filename}")
        res = self.client.get_resume_upload_url(filename)
        upload_url = res.get("upload_url")
        resume_s3_key = res.get("resume_s3_key")

        print(f"[*] Uploading resume to S3...")
        self.client.upload_file_to_s3(resume_path, upload_url, content_type="application/pdf")
        
        print(f"[*] Linking resume S3 key: {resume_s3_key}")
        self.client.update_profile({"resume_s3_key": resume_s3_key})
        return resume_s3_key

    def process_screening(self) -> int:
        """Retrieves and checks screening questions."""
        res = self.client.get_screening_questions()
        questions = res.get("questions", [])
        print(f"[*] Found {len(questions)} screening questions.")
        return len(questions)

    def upload_session_log(self, log_content: str) -> str:
        """Generates and uploads application transcript log to S3."""
        print("[*] Generating application session transcript...")
        res = self.client.get_session_log_url()
        upload_url = res.get("upload_url")
        s3_key = res.get("session_log_s3_key")

        temp_log = "session_log_temp.md"
        with open(temp_log, "w", encoding="utf-8") as f:
            f.write(log_content)

        try:
            self.client.upload_file_to_s3(temp_log, upload_url, content_type="text/markdown")
            print(f"[*] Session log uploaded: {s3_key}")
        finally:
            if os.path.exists(temp_log):
                os.remove(temp_log)

        return s3_key

    def finalize_application(self) -> Dict[str, Any]:
        """Submits the finalized application."""
        print("[*] Submitting final job application...")
        return self.client.submit_application()
