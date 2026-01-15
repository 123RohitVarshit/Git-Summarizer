"""Git repository analyzer - extracts diffs, commits, and status information."""

import subprocess
import re
from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from pathlib import Path


@dataclass
class CommitInfo:
    """Information about a single git commit."""
    hash: str
    author: str
    email: str
    date: datetime
    subject: str
    body: str
    files_changed: int = 0
    insertions: int = 0
    deletions: int = 0


@dataclass
class DiffSummary:
    """Summary of changes in a diff."""
    files: list[str]
    total_additions: int
    total_deletions: int
    raw_diff: str


@dataclass
class RepoStatus:
    """Current status of the repository."""
    staged: list[str]
    modified: list[str]
    untracked: list[str]
    is_dirty: bool
    branch: str


class GitAnalyzer:
    """Analyzes a git repository to extract useful information."""
    
    def __init__(self, repo_path: str = "."):
        self.repo_path = Path(repo_path).resolve()
        self._validate_repo()
    
    def _validate_repo(self) -> None:
        """Check if the path is a valid git repository."""
        git_dir = self.repo_path / ".git"
        if not git_dir.exists():
            raise ValueError(f"Not a git repository: {self.repo_path}")
    
    def _run_git(self, *args: str) -> str:
        """Run a git command and return the output."""
        try:
            result = subprocess.run(
                ["git", *args],
                capture_output=True,
                text=True,
                cwd=self.repo_path,
                check=False
            )
            if result.returncode != 0 and result.stderr:
                # Some git commands return non-zero but are still valid
                if "fatal:" in result.stderr:
                    raise RuntimeError(f"Git error: {result.stderr.strip()}")
            return result.stdout
        except FileNotFoundError:
            raise RuntimeError("Git is not installed or not in PATH")
    
    def get_current_branch(self) -> str:
        """Get the name of the current branch."""
        return self._run_git("branch", "--show-current").strip()
    
    def get_repo_status(self) -> RepoStatus:
        """Get the current status of the repository."""
        status_output = self._run_git("status", "--porcelain")
        
        staged = []
        modified = []
        untracked = []
        
        for line in status_output.strip().split('\n'):
            if not line:
                continue
            code = line[:2]
            filename = line[3:]
            
            # Index status (first character)
            if code[0] in 'MADRC':
                staged.append(filename)
            # Working tree status (second character)
            if code[1] == 'M':
                modified.append(filename)
            # Untracked
            if code == '??':
                untracked.append(filename)
        
        return RepoStatus(
            staged=staged,
            modified=modified,
            untracked=untracked,
            is_dirty=bool(staged or modified),
            branch=self.get_current_branch()
        )
    
    def get_uncommitted_diff(self, max_chars: Optional[int] = None) -> DiffSummary:
        """Get diff of all uncommitted changes (staged + unstaged)."""
        raw_diff = self._run_git("diff", "HEAD")
        stat_output = self._run_git("diff", "--stat", "HEAD")
        
        return self._parse_diff_stats(raw_diff, stat_output, max_chars)
    
    def get_staged_diff(self, max_chars: Optional[int] = None) -> DiffSummary:
        """Get diff of only staged changes."""
        raw_diff = self._run_git("diff", "--cached")
        stat_output = self._run_git("diff", "--stat", "--cached")
        
        return self._parse_diff_stats(raw_diff, stat_output, max_chars)
    
    def _parse_diff_stats(
        self, 
        raw_diff: str, 
        stat_output: str,
        max_chars: Optional[int] = None
    ) -> DiffSummary:
        """Parse diff statistics from git output."""
        files = []
        additions = 0
        deletions = 0
        
        for line in stat_output.strip().split('\n'):
            if '|' in line:
                filename = line.split('|')[0].strip()
                files.append(filename)
        
        # Parse summary line
        summary_match = re.search(
            r'(\d+) insertions?\(\+\)',
            stat_output
        )
        if summary_match:
            additions = int(summary_match.group(1))
        
        del_match = re.search(
            r'(\d+) deletions?\(-\)',
            stat_output
        )
        if del_match:
            deletions = int(del_match.group(1))
        
        # Truncate diff if needed
        diff_text = raw_diff
        if max_chars and len(raw_diff) > max_chars:
            diff_text = raw_diff[:max_chars] + "\n\n... (truncated)"
        
        return DiffSummary(
            files=files,
            total_additions=additions,
            total_deletions=deletions,
            raw_diff=diff_text
        )
    
    def get_recent_commits(self, days: int = 7) -> list[CommitInfo]:
        """Get commits from the last N days."""
        # Use null byte as delimiter for reliable parsing
        format_str = "%H%x00%an%x00%ae%x00%ad%x00%s%x00%b%x00%x01"
        
        output = self._run_git(
            "log",
            f"--since={days} days ago",
            f"--pretty=format:{format_str}",
            "--date=iso"
        )
        
        if not output.strip():
            return []
        
        commits = []
        entries = output.split('\x01')
        
        for entry in entries:
            entry = entry.strip()
            if not entry:
                continue
            
            parts = entry.split('\x00')
            if len(parts) >= 5:
                try:
                    # Parse ISO date
                    date_str = parts[3].strip()
                    # Handle timezone in date string
                    date = datetime.fromisoformat(date_str.replace(' ', 'T', 1).replace(' ', ''))
                except (ValueError, IndexError):
                    date = datetime.now()
                
                commits.append(CommitInfo(
                    hash=parts[0],
                    author=parts[1],
                    email=parts[2],
                    date=date,
                    subject=parts[4],
                    body=parts[5] if len(parts) > 5 else ""
                ))
        
        return commits
    
    def get_commit_diff(self, commit_hash: str, max_chars: Optional[int] = None) -> str:
        """Get the diff for a specific commit."""
        diff = self._run_git("show", commit_hash, "--pretty=format:", "--patch")
        
        if max_chars and len(diff) > max_chars:
            return diff[:max_chars] + "\n\n... (truncated)"
        
        return diff
    
    def get_commit_count(self, days: int = 7) -> int:
        """Get the number of commits in the last N days."""
        output = self._run_git(
            "rev-list",
            "--count",
            f"--since={days} days ago",
            "HEAD"
        )
        return int(output.strip()) if output.strip() else 0
    
    def get_last_activity(self) -> Optional[datetime]:
        """Get the timestamp of the last commit."""
        output = self._run_git("log", "-1", "--format=%ai")
        if not output.strip():
            return None
        
        try:
            date_str = output.strip()
            return datetime.fromisoformat(date_str.replace(' ', 'T', 1).replace(' ', ''))
        except ValueError:
            return None
