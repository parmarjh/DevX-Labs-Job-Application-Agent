"""
CLI Entrypoint for DevX Job Application Agent.
"""

import sys
import os
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from config import DEVX_BASE_URL, DEVX_AUTH_TOKEN
from mcp_client import DevXMCPClient
from agent import DevXJobAgent

console = Console()

def run_application_flow(resume_file: str, token: str):
    console.print(Panel.fit("[bold cyan]DevX Labs — Job Application Agent[/bold cyan]\n[dim]Automated MCP-based Application Runner[/dim]"))

    if not token:
        console.print("[bold red]Error:[/bold red] DEVX_AUTH_TOKEN is required. Provide via argument or .env file.")
        sys.exit(1)

    client = DevXMCPClient(base_url=DEVX_BASE_URL, token=token)
    agent = DevXJobAgent(client)

    try:
        # Step 1: Fetch Profile & Role
        console.print("\n[bold yellow]Step 1: Fetching current profile and position...[/bold yellow]")
        profile_data = client.get_profile()
        target_pos = profile_data.get("target_position", {})
        console.print(f"[green]✓ Target Role:[/green] [bold]{target_pos.get('title', 'Data Scientist')}[/bold]")

        # Step 2: Upload Resume
        console.print(f"\n[bold yellow]Step 2: Uploading resume PDF ({resume_file})...[/bold yellow]")
        s3_key = agent.upload_resume(resume_file)
        console.print(f"[green]✓ Resume Uploaded & Linked:[/green] {s3_key}")

        # Step 3: Screening Questions
        console.print("\n[bold yellow]Step 3: Checking screening questions...[/bold yellow]")
        count = agent.process_screening()
        console.print(f"[green]✓ Screening questions count:[/green] {count}")

        # Step 4: Upload Session Log
        console.print("\n[bold yellow]Step 4: Uploading session audit log...[/bold yellow]")
        log_content = f"# DevX Job Application Log\n\nTarget Position: {target_pos.get('title')}\nResume: {resume_file}\n"
        agent.upload_session_log(log_content)
        console.print("[green]✓ Audit log uploaded successfully.[/green]")

        # Step 5: Final Submission
        console.print("\n[bold yellow]Step 5: Submitting final application...[/bold yellow]")
        result = agent.finalize_application()
        console.print("[bold green]🎉 Application Successfully Submitted to DevX Labs![/bold green]")
        console.print(result)

    except Exception as e:
        console.print(f"\n[bold red]Pipeline Error:[/bold red] {e}")

if __name__ == "__main__":
    resume_path = sys.argv[1] if len(sys.argv) > 1 else "C:\\Users\\parma\\OneDrive\\Desktop\\devX Apps\\Jatincv.pdf"
    auth_token = sys.argv[2] if len(sys.argv) > 2 else DEVX_AUTH_TOKEN
    run_application_flow(resume_path, auth_token)
