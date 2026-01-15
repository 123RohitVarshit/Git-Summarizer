"""Git-Summarizer CLI - Main entry point with interactive features."""

import click
from pathlib import Path

from .git import GitAnalyzer
from .llm import LLMClient
from .output import OutputFormatter
from .output.markdown_generator import MarkdownReportGenerator
from .output.prompts import (
    select_commits,
    select_files,
    select_days,
    confirm_action,
    select_report_type,
    select_main_action,
    select_output_options,
)
from .config import get_config
from .integrations.slack import SlackSender


# Initialize formatter
formatter = OutputFormatter()


@click.group(invoke_without_command=True)
@click.version_option(version="0.1.0", prog_name="git-summarizer")
@click.pass_context
def main(ctx):
    """🚀 Git-Summarizer: AI-powered Git progress reports and commit messages.
    
    Analyze your git repository and get human-readable summaries of your work.
    
    Run without arguments for interactive wizard mode.
    """
    if ctx.invoked_subcommand is None:
        # Wizard mode - no subcommand specified
        wizard_mode()


def wizard_mode():
    """Interactive wizard mode - guides user through all options."""
    formatter.print_header("Git-Summarizer", "Interactive Mode")
    
    action = select_main_action()
    
    if action == "exit":
        formatter.print_info("Goodbye! 👋")
        return
    
    if action == "status":
        # Run status with interactive mode
        ctx = click.Context(status)
        ctx.invoke(status, path=".", interactive=True, show_diff=True)
    
    elif action == "commit":
        # Run commit with interactive mode
        ctx = click.Context(commit)
        ctx.invoke(commit, path=".", interactive=True)
    
    elif action == "report":
        # Get time period
        days = select_days(default=7)
        
        # Get output options
        output_opts = select_output_options()
        
        # Run report
        ctx = click.Context(report)
        ctx.invoke(
            report,
            path=".",
            days=days,
            interactive=True,
            save_path=output_opts["save_path"],
            slack=output_opts["slack"]
        )


@main.command()
@click.option("--path", "-p", default=".", help="Path to the git repository")
@click.option("--interactive", "-i", is_flag=True, help="Interactive mode with file selection")
@click.option("--show-diff", "-d", is_flag=True, help="Show diff preview")
def status(path: str, interactive: bool, show_diff: bool):
    """📊 Summarize uncommitted changes in the repository."""
    try:
        # Initialize components
        repo_path = Path(path).resolve()
        formatter.print_header("Git-Summarizer", f"Repository: {repo_path.name}")
        
        try:
            git = GitAnalyzer(str(repo_path))
        except ValueError as e:
            formatter.print_error(str(e))
            return
        
        # Get repository status
        status = git.get_repo_status()
        formatter.print_status(
            branch=status.branch,
            is_dirty=status.is_dirty,
            staged=status.staged,
            modified=status.modified,
            untracked=status.untracked
        )
        
        # Show last activity
        last_activity = git.get_last_activity()
        formatter.print_last_activity(last_activity)
        
        # Check if there are changes to summarize
        if not status.is_dirty:
            formatter.print_no_changes()
            return
        
        # Get diff summary
        config = get_config()
        diff_summary = git.get_uncommitted_diff(max_chars=config.max_diff_chars)
        
        # Interactive file selection
        files_to_analyze = diff_summary.files
        if interactive and diff_summary.files:
            files_to_analyze = select_files(
                diff_summary.files,
                "Select files to include in analysis:"
            )
            if not files_to_analyze:
                formatter.print_warning("No files selected. Exiting.")
                return
        
        formatter.print_diff_stats(
            files=files_to_analyze,
            additions=diff_summary.total_additions,
            deletions=diff_summary.total_deletions
        )
        
        # Show file tree view
        formatter.print_file_tree(files_to_analyze)
        
        # Show diff preview if requested
        if show_diff:
            formatter.print_diff_preview(diff_summary.raw_diff)
        
        # Generate AI summary with spinner
        spinner = formatter.create_spinner()
        with spinner:
            task = spinner.add_task("🤖 Generating AI summary...", total=None)
            
            try:
                config.validate()
                llm = LLMClient()
                
                stats = f"{len(files_to_analyze)} files changed, +{diff_summary.total_additions}, -{diff_summary.total_deletions}"
                summary = llm.summarize_changes(
                    diff=diff_summary.raw_diff,
                    stats=stats,
                    files=files_to_analyze
                )
                
                spinner.remove_task(task)
            except ValueError as e:
                spinner.remove_task(task)
                formatter.print_warning(str(e))
                formatter.print_info("Run without AI summary. Set GEMINI_API_KEY to enable AI features.")
                return
            except Exception as e:
                spinner.remove_task(task)
                formatter.print_error(f"AI summary failed: {e}")
                return
        
        formatter.print_summary(summary)
    
    except Exception as e:
        formatter.print_error(f"Unexpected error: {e}")


@main.command()
@click.option("--path", "-p", default=".", help="Path to the git repository")
@click.option("--interactive", "-i", is_flag=True, help="Interactive mode")
def commit(path: str, interactive: bool):
    """💡 Suggest a commit message for staged changes."""
    try:
        repo_path = Path(path).resolve()
        formatter.print_header("Commit Message Generator", f"Repository: {repo_path.name}")
        
        try:
            git = GitAnalyzer(str(repo_path))
        except ValueError as e:
            formatter.print_error(str(e))
            return
        
        # Get staged changes first, fall back to all uncommitted
        config = get_config()
        diff_summary = git.get_staged_diff(max_chars=config.max_diff_chars)
        
        if not diff_summary.files:
            # No staged changes, try uncommitted
            diff_summary = git.get_uncommitted_diff(max_chars=config.max_diff_chars)
            if not diff_summary.files:
                formatter.print_no_changes()
                return
            formatter.print_warning("No staged changes. Using all uncommitted changes.")
        
        # Interactive file selection
        files_to_analyze = diff_summary.files
        if interactive and diff_summary.files:
            files_to_analyze = select_files(
                diff_summary.files,
                "Select files to include in commit:"
            )
            if not files_to_analyze:
                formatter.print_warning("No files selected. Exiting.")
                return
        
        formatter.print_diff_stats(
            files=files_to_analyze,
            additions=diff_summary.total_additions,
            deletions=diff_summary.total_deletions
        )
        
        # Generate commit message with spinner
        spinner = formatter.create_spinner()
        with spinner:
            task = spinner.add_task("🤖 Generating commit message...", total=None)
            
            try:
                config.validate()
                llm = LLMClient()
                
                stats = f"{len(files_to_analyze)} files changed, +{diff_summary.total_additions}, -{diff_summary.total_deletions}"
                message = llm.suggest_commit_message(
                    diff=diff_summary.raw_diff,
                    stats=stats
                )
                
                spinner.remove_task(task)
            except ValueError as e:
                spinner.remove_task(task)
                formatter.print_error(str(e))
                return
            except Exception as e:
                spinner.remove_task(task)
                formatter.print_error(f"Failed to generate commit message: {e}")
                return
        
        formatter.print_commit_message(message)
        
        # Interactive: ask to run commit
        if interactive:
            if confirm_action("Would you like to run this commit?"):
                import subprocess
                result = subprocess.run(
                    ["git", "commit", "-m", message],
                    cwd=repo_path,
                    capture_output=True,
                    text=True
                )
                if result.returncode == 0:
                    formatter.print_success("Commit created successfully!")
                else:
                    formatter.print_error(f"Commit failed: {result.stderr}")
    
    except Exception as e:
        formatter.print_error(f"Unexpected error: {e}")


@main.command()
@click.option("--path", "-p", default=".", help="Path to the git repository")
@click.option("--days", "-d", default=None, type=int, help="Number of days to include")
@click.option("--interactive", "-i", is_flag=True, help="Interactive mode with commit selection")
@click.option("--save", "-s", "save_path", default=None, help="Save report as Markdown file")
@click.option("--slack", is_flag=True, help="Send report to Slack (requires SLACK_WEBHOOK_URL)")
def report(path: str, days: int, interactive: bool, save_path: str, slack: bool):
    """📈 Generate a progress report for recent commits."""
    try:
        repo_path = Path(path).resolve()
        formatter.print_header("Progress Report Generator", f"Repository: {repo_path.name}")
        
        try:
            git = GitAnalyzer(str(repo_path))
        except ValueError as e:
            formatter.print_error(str(e))
            return
        
        # Interactive: select time period
        if interactive and days is None:
            days = select_days(default=7)
        elif days is None:
            days = 7
        
        # Get recent commits
        commits = git.get_recent_commits(days=days)
        
        if not commits:
            formatter.print_warning(f"No commits found in the last {days} days.")
            return
        
        formatter.print_info(f"Found {len(commits)} commits in the last {days} days")
        
        # Show commits table
        formatter.print_commits_table(commits)
        
        # Interactive: select commits to include
        selected_commits = commits
        if interactive:
            selected_commits = select_commits(commits, "Select commits to include in report:")
            if not selected_commits:
                formatter.print_warning("No commits selected. Exiting.")
                return
            formatter.print_info(f"Selected {len(selected_commits)} commits for report")
        
        # Build commits summary for the LLM
        def get_commit_info(c):
            """Safely extract commit info whether it's an object or dict."""
            if hasattr(c, 'date'):
                date_str = c.date.strftime('%Y-%m-%d')
                subject = c.subject
                author = c.author
            else:
                # Handle dict case
                date_obj = c.get('date') if isinstance(c, dict) else None
                date_str = date_obj.strftime('%Y-%m-%d') if date_obj else 'unknown'
                subject = c.get('subject', '') if isinstance(c, dict) else str(c)
                author = c.get('author', 'unknown') if isinstance(c, dict) else 'unknown'
            return f"- [{date_str}] {subject} (by {author})"
        
        commits_summary = "\n".join([get_commit_info(c) for c in selected_commits])
        
        # Generate report with spinner
        spinner = formatter.create_spinner()
        with spinner:
            task = spinner.add_task("🤖 Generating progress report...", total=None)
            
            try:
                config = get_config()
                config.validate()
                llm = LLMClient()
                
                report_text = llm.generate_report(
                    commits_summary=commits_summary,
                    total_commits=len(selected_commits),
                    days=days
                )
                
                spinner.remove_task(task)
            except ValueError as e:
                spinner.remove_task(task)
                formatter.print_error(str(e))
                return
            except Exception as e:
                spinner.remove_task(task)
                formatter.print_error(f"Failed to generate report: {e}")
                return
        
        # Save as Markdown if requested
        if save_path:
            try:
                md_gen = MarkdownReportGenerator()
                saved_path = md_gen.generate(
                    repo_name=repo_path.name,
                    days=days,
                    total_commits=len(selected_commits),
                    report_text=report_text,
                    commits=selected_commits,
                    output_path=save_path
                )
                formatter.print_success(f"Report saved to: {saved_path}")
            except Exception as e:
                formatter.print_error(f"Failed to save report: {e}")
        
        # Send to Slack if requested
        if slack:
            config = get_config()
            if not config.slack_webhook_url:
                formatter.print_error(
                    "Slack webhook URL not configured.\n"
                    "Set SLACK_WEBHOOK_URL in your .env file or environment."
                )
            else:
                try:
                    slack_sender = SlackSender(config.slack_webhook_url)
                    slack_sender.send_report(
                        repo_name=repo_path.name,
                        days=days,
                        total_commits=len(selected_commits),
                        report_text=report_text,
                        commits=selected_commits
                    )
                    formatter.print_success("📤 Report sent to Slack!")
                except Exception as e:
                    formatter.print_error(f"Failed to send to Slack: {e}")
        
        formatter.print_report(report_text, days)
    
    except Exception as e:
        formatter.print_error(f"Unexpected error: {e}")


if __name__ == "__main__":
    main()

# Short command aliases
main.add_command(status, name="s")
main.add_command(commit, name="c")
main.add_command(report, name="r")

