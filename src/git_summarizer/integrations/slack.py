"""Slack integration for sharing reports via webhooks."""

import httpx
from typing import Optional


class SlackSender:
    """Send messages to Slack via incoming webhooks."""
    
    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url
    
    def send_report(
        self,
        repo_name: str,
        days: int,
        total_commits: int,
        report_text: str,
        commits: list
    ) -> bool:
        """Send a progress report to Slack."""
        
        avg = round(total_commits / max(days, 1), 1)
        
        # Build Slack message blocks
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "📊 Git Progress Report",
                    "emoji": True
                }
            },
            {
                "type": "section",
                "fields": [
                    {"type": "mrkdwn", "text": f"*Repository:*\n{repo_name}"},
                    {"type": "mrkdwn", "text": f"*Period:*\nLast {days} days"},
                    {"type": "mrkdwn", "text": f"*Total Commits:*\n{total_commits}"},
                    {"type": "mrkdwn", "text": f"*Average:*\n{avg} commits/day"}
                ]
            },
            {"type": "divider"},
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*📝 Summary*\n{self._truncate(report_text, 2500)}"
                }
            }
        ]
        
        # Add recent commits
        if commits:
            commit_text = "*📜 Recent Commits*\n"
            for i, commit in enumerate(commits[:5], 1):
                if hasattr(commit, 'subject'):
                    subject = commit.subject[:50]
                else:
                    subject = str(commit.get('subject', ''))[:50] if isinstance(commit, dict) else str(commit)[:50]
                commit_text += f"• {subject}\n"
            
            if len(commits) > 5:
                commit_text += f"_... and {len(commits) - 5} more_"
            
            blocks.append({
                "type": "section",
                "text": {"type": "mrkdwn", "text": commit_text}
            })
        
        # Add footer
        blocks.append({"type": "divider"})
        blocks.append({
            "type": "context",
            "elements": [
                {"type": "mrkdwn", "text": "_Sent by Git-Summarizer_ 🚀"}
            ]
        })
        
        payload = {"blocks": blocks}
        
        try:
            with httpx.Client(timeout=30.0) as client:
                response = client.post(self.webhook_url, json=payload)
                response.raise_for_status()
                return True
        except Exception as e:
            raise RuntimeError(f"Failed to send to Slack: {e}")
    
    def _truncate(self, text: str, max_length: int) -> str:
        """Truncate text to max length."""
        if len(text) <= max_length:
            return text
        return text[:max_length - 3] + "..."
    
    def send_simple_message(self, message: str) -> bool:
        """Send a simple text message to Slack."""
        payload = {"text": message}
        
        try:
            with httpx.Client(timeout=30.0) as client:
                response = client.post(self.webhook_url, json=payload)
                response.raise_for_status()
                return True
        except Exception as e:
            raise RuntimeError(f"Failed to send to Slack: {e}")
