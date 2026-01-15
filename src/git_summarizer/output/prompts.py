"""Interactive prompts using InquirerPy for user input."""

from typing import List, Optional
from dataclasses import dataclass

from InquirerPy import inquirer
from InquirerPy.base.control import Choice
from InquirerPy.separator import Separator


@dataclass
class CommitChoice:
    """Represents a commit that can be selected."""
    hash: str
    subject: str
    author: str
    date: str
    selected: bool = True


def select_commits(commits: list, title: str = "Select commits to include:") -> list:
    """
    Let user select which commits to include in a report.
    
    Args:
        commits: List of CommitInfo objects
        title: Title for the selection prompt
    
    Returns:
        List of selected CommitInfo objects
    """
    if not commits:
        return []
    
    # Build choices
    choices = []
    for commit in commits:
        # Handle both object and dict access
        if hasattr(commit, 'date'):
            date_str = commit.date.strftime("%m/%d") if commit.date else ""
            subject = commit.subject
        else:
            date_obj = commit.get('date') if isinstance(commit, dict) else None
            date_str = date_obj.strftime("%m/%d") if date_obj else ""
            subject = commit.get('subject', '') if isinstance(commit, dict) else str(commit)
        
        label = f"[{date_str}] {subject[:50]}{'...' if len(subject) > 50 else ''}"
        choices.append(Choice(value=commit, name=label, enabled=True))
    
    # Run interactive selection
    selected = inquirer.checkbox(
        message=title,
        choices=choices,
        instruction="(Space to toggle, Enter to confirm)",
        transformer=lambda result: f"{len(result)} commits selected",
    ).execute()
    
    return selected or []


def select_files(files: list, title: str = "Select files to include:") -> list:
    """
    Let user select which files to include.
    
    Args:
        files: List of file paths
        title: Title for the selection prompt
    
    Returns:
        List of selected file paths
    """
    if not files:
        return []
    
    # Build choices
    choices = [Choice(value=f, name=f, enabled=True) for f in files]
    
    # Run interactive selection
    selected = inquirer.checkbox(
        message=title,
        choices=choices,
        instruction="(Space to toggle, Enter to confirm)",
        transformer=lambda result: f"{len(result)} files selected",
    ).execute()
    
    return selected or []


def select_days(default: int = 7) -> int:
    """
    Let user select the number of days for a report.
    
    Args:
        default: Default number of days
    
    Returns:
        Selected number of days
    """
    choices = [
        Choice(value=1, name="Today only"),
        Choice(value=3, name="Last 3 days"),
        Choice(value=7, name="Last week"),
        Choice(value=14, name="Last 2 weeks"),
        Choice(value=30, name="Last month"),
        Separator(),
        Choice(value=-1, name="Custom..."),
    ]
    
    selected = inquirer.select(
        message="Select time period for report:",
        choices=choices,
        default=7,
    ).execute()
    
    if selected == -1:
        # Custom input using text to avoid the append issue
        def validate_days(val):
            try:
                num = int(val)
                return 1 <= num <= 365
            except ValueError:
                return False
        
        custom = inquirer.text(
            message="Enter number of days (1-365):",
            default="",  # Empty default so user types fresh
            validate=validate_days,
            invalid_message="Please enter a number between 1 and 365",
        ).execute()
        return int(custom)
    
    return selected


def confirm_action(message: str, default: bool = True) -> bool:
    """
    Ask user to confirm an action.
    
    Args:
        message: Confirmation message
        default: Default response
    
    Returns:
        True if confirmed, False otherwise
    """
    return inquirer.confirm(
        message=message,
        default=default,
    ).execute()


def select_report_type() -> str:
    """
    Let user select the type of report to generate.
    
    Returns:
        Selected report type
    """
    choices = [
        Choice(value="summary", name="📊 Summary Report - High-level overview"),
        Choice(value="detailed", name="📝 Detailed Report - Include commit details"),
        Choice(value="changelog", name="📋 Changelog - Formatted for release notes"),
    ]
    
    return inquirer.select(
        message="Select report type:",
        choices=choices,
        default="summary",
    ).execute()


def select_output_format() -> str:
    """
    Let user select the output format.
    
    Returns:
        Selected output format
    """
    choices = [
        Choice(value="terminal", name="🖥️  Terminal - Rich formatted output"),
        Choice(value="markdown", name="📄 Markdown - Save to file"),
        Choice(value="json", name="📦 JSON - Machine-readable"),
    ]
    
    return inquirer.select(
        message="Select output format:",
        choices=choices,
        default="terminal",
    ).execute()


def input_custom_prompt(default: str = "") -> str:
    """
    Let user input a custom prompt for the AI.
    
    Args:
        default: Default prompt text
    
    Returns:
        Custom prompt text
    """
    return inquirer.text(
        message="Enter custom instructions for the AI (optional):",
        default=default,
    ).execute()


def select_main_action() -> str:
    """
    Main menu wizard - let user select what action to perform.
    
    Returns:
        Selected action: 'status', 'commit', or 'report'
    """
    choices = [
        Choice(value="status", name="📊 Status - Check uncommitted changes"),
        Choice(value="commit", name="💡 Commit - Generate commit message"),
        Choice(value="report", name="📈 Report - Generate progress report"),
        Separator(),
        Choice(value="exit", name="👋 Exit"),
    ]
    
    return inquirer.select(
        message="What would you like to do?",
        choices=choices,
        default="status",
    ).execute()


def select_output_options() -> dict:
    """
    Let user select output options for report.
    
    Returns:
        Dict with 'save_path', 'slack' keys
    """
    choices = [
        Choice(value="terminal", name="🖥️  Terminal only"),
        Choice(value="save", name="💾 Save as Markdown file"),
        Choice(value="slack", name="📤 Send to Slack"),
        Choice(value="both", name="💾+📤 Save and send to Slack"),
    ]
    
    selected = inquirer.select(
        message="How would you like to output the report?",
        choices=choices,
        default="terminal",
    ).execute()
    
    result = {"save_path": None, "slack": False}
    
    if selected in ["save", "both"]:
        result["save_path"] = inquirer.text(
            message="Enter filename (e.g., report.md):",
            default="report.md",
        ).execute()
    
    if selected in ["slack", "both"]:
        result["slack"] = True
    
    return result

