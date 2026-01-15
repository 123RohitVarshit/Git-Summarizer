"""Prompt templates for LLM interactions."""


class Prompts:
    """Collection of prompt templates for different summarization tasks."""
    
    @staticmethod
    def status_summary(diff: str, stats: str, files: list[str]) -> str:
        """Prompt to summarize uncommitted changes."""
        file_list = "\n".join(f"  - {f}" for f in files[:20])
        if len(files) > 20:
            file_list += f"\n  ... and {len(files) - 20} more files"
        
        return f"""You are a helpful coding assistant analyzing git changes. 
Analyze the following uncommitted changes and provide a concise, human-readable summary.

**Changed Files:**
{file_list}

**Statistics:**
{stats}

**Diff (may be truncated):**
```diff
{diff}
```

**Instructions:**
1. Describe WHAT the developer is working on in 2-3 sentences
2. List the key changes as bullet points (max 5 bullets)
3. Note any potential issues or incomplete work if visible

Format your response as:
## Summary
[2-3 sentence overview]

## Key Changes
- [change 1]
- [change 2]
...

## Notes
[Any observations about incomplete work, potential issues, etc. Skip if none.]
"""

    @staticmethod
    def commit_message(diff: str, stats: str) -> str:
        """Prompt to generate a commit message."""
        return f"""You are a helpful coding assistant. Generate a conventional commit message for these changes.

**Statistics:**
{stats}

**Diff:**
```diff
{diff}
```

**Instructions:**
Generate a commit message following the Conventional Commits format:
- Type: feat, fix, docs, style, refactor, test, chore
- Scope: optional, in parentheses
- Description: imperative mood, lowercase, no period

Examples:
- feat(auth): add JWT token refresh mechanism
- fix: resolve null pointer in user validation
- docs: update API documentation for v2 endpoints

Respond with ONLY the commit message, nothing else.
"""

    @staticmethod
    def progress_report(commits_summary: str, total_commits: int, days: int) -> str:
        """Prompt to generate a progress report."""
        return f"""You are a helpful coding assistant creating a progress report.

**Period:** Last {days} days
**Total Commits:** {total_commits}

**Commit History:**
{commits_summary}

**Instructions:**
Create a brief, developer-friendly progress report that:
1. Summarizes the main accomplishments in 2-3 sentences
2. Groups related commits into categories/features
3. Highlights any notable patterns (bug fixes, new features, refactoring)

Format your response as:

## Progress Summary
[2-3 sentence overview of accomplishments]

## Work Completed
### [Category 1]
- [accomplishment]
- [accomplishment]

### [Category 2]
- [accomplishment]

## Statistics
- Total commits: {total_commits}
- Period: {days} days
"""
