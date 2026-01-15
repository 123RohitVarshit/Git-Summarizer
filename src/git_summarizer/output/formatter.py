"""Rich terminal output formatting with enhanced visuals."""

from datetime import datetime
from typing import Optional, List

from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.table import Table
from rich.text import Text
from rich.syntax import Syntax
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.live import Live
from rich.layout import Layout
from rich.align import Align
from rich.tree import Tree
from rich import box


console = Console()


class OutputFormatter:
    """Formats output for the terminal using Rich with enhanced visuals."""
    
    def __init__(self):
        self.console = console
    
    def print_header(self, title: str, subtitle: Optional[str] = None) -> None:
        """Print a styled header."""
        self.console.print()
        
        # Create header text
        header_text = Text()
        header_text.append("🚀 ", style="bold")
        header_text.append(title, style="bold cyan")
        
        self.console.print(
            Panel(
                Align.center(header_text),
                subtitle=subtitle,
                style="cyan",
                box=box.DOUBLE_EDGE,
                padding=(1, 2)
            )
        )
        self.console.print()
    
    def print_status(
        self,
        branch: str,
        is_dirty: bool,
        staged: list[str],
        modified: list[str],
        untracked: list[str]
    ) -> None:
        """Print repository status with icons."""
        status_icon = "🔴" if is_dirty else "🟢"
        status_text = "Has uncommitted changes" if is_dirty else "Clean"
        
        # Branch info with style
        self.console.print(
            Panel(
                f"📍 [bold cyan]{branch}[/] {status_icon} {status_text}",
                title="Branch Status",
                border_style="dim",
                box=box.ROUNDED
            )
        )
        
        if staged:
            self.console.print(f"\n[bold green]✓ Staged ({len(staged)}):[/]")
            for f in staged[:5]:
                self.console.print(f"  [green]•[/] {f}")
            if len(staged) > 5:
                self.console.print(f"  [dim]... and {len(staged) - 5} more[/]")
        
        if modified:
            self.console.print(f"\n[bold yellow]● Modified ({len(modified)}):[/]")
            for f in modified[:5]:
                self.console.print(f"  [yellow]•[/] {f}")
            if len(modified) > 5:
                self.console.print(f"  [dim]... and {len(modified) - 5} more[/]")
        
        if untracked:
            self.console.print(f"\n[dim]? Untracked ({len(untracked)}):[/]")
            for f in untracked[:3]:
                self.console.print(f"  [dim]•[/] {f}")
            if len(untracked) > 3:
                self.console.print(f"  [dim]... and {len(untracked) - 3} more[/]")
    
    def print_diff_stats(
        self,
        files: list[str],
        additions: int,
        deletions: int
    ) -> None:
        """Print diff statistics in a beautiful table."""
        self.console.print()
        
        # Create a stats table
        table = Table(
            show_header=True,
            header_style="bold magenta",
            box=box.ROUNDED,
            title="📊 Change Statistics",
            title_style="bold"
        )
        table.add_column("Metric", style="cyan")
        table.add_column("Value", justify="right")
        table.add_column("Visual", justify="left")
        
        # Calculate visual bars
        total = additions + deletions if (additions + deletions) > 0 else 1
        add_bar = "█" * min(int(additions / total * 20), 20)
        del_bar = "█" * min(int(deletions / total * 20), 20)
        
        table.add_row(
            "📁 Files changed",
            str(len(files)),
            f"[dim]{len(files)} file{'s' if len(files) != 1 else ''}[/]"
        )
        table.add_row(
            "[green]+ Additions[/]",
            f"[green]+{additions}[/]",
            f"[green]{add_bar}[/]"
        )
        table.add_row(
            "[red]- Deletions[/]",
            f"[red]-{deletions}[/]",
            f"[red]{del_bar}[/]"
        )
        
        self.console.print(table)
    
    def print_diff_preview(self, diff: str, max_lines: int = 20) -> None:
        """Print a syntax-highlighted diff preview."""
        if not diff.strip():
            return
        
        lines = diff.split('\n')[:max_lines]
        preview = '\n'.join(lines)
        
        if len(diff.split('\n')) > max_lines:
            preview += f"\n... ({len(diff.split(chr(10))) - max_lines} more lines)"
        
        self.console.print()
        self.console.print(
            Panel(
                Syntax(preview, "diff", theme="monokai", line_numbers=False),
                title="📝 Diff Preview",
                border_style="dim",
                box=box.ROUNDED
            )
        )
    
    def print_summary(self, summary: str, title: str = "AI Summary") -> None:
        """Print an AI-generated summary in a beautiful panel."""
        self.console.print()
        self.console.print(
            Panel(
                Markdown(summary),
                title=f"🤖 {title}",
                border_style="green",
                box=box.DOUBLE_EDGE,
                padding=(1, 2)
            )
        )
    
    def print_commit_message(self, message: str) -> None:
        """Print a suggested commit message with copy hint."""
        self.console.print()
        self.console.print(
            Panel(
                Text(message, style="bold yellow", justify="center"),
                title="💡 Suggested Commit Message",
                border_style="yellow",
                box=box.DOUBLE_EDGE,
                padding=(1, 2)
            )
        )
        self.console.print()
        self.console.print("[dim]📋 Copy the message above or run:[/]")
        self.console.print(f'  [cyan]git commit -m "{message}"[/]')
    
    def print_report(self, report: str, days: int) -> None:
        """Print a progress report."""
        self.console.print()
        self.console.print(
            Panel(
                Markdown(report),
                title=f"📈 Progress Report (Last {days} days)",
                border_style="blue",
                box=box.DOUBLE_EDGE,
                padding=(1, 2)
            )
        )
    
    def print_commits_table(self, commits: list) -> None:
        """Print a table of commits."""
        if not commits:
            return
        
        table = Table(
            show_header=True,
            header_style="bold cyan",
            box=box.ROUNDED,
            title="📜 Recent Commits",
            title_style="bold"
        )
        table.add_column("#", style="dim", width=4)
        table.add_column("Date", style="magenta")
        table.add_column("Message", style="white")
        table.add_column("Author", style="cyan")
        
        for i, commit in enumerate(commits[:15], 1):
            # Handle both object and dict access
            if hasattr(commit, 'date'):
                date_str = commit.date.strftime("%m/%d") if commit.date else "N/A"
                subject = commit.subject
                author = commit.author
            else:
                date_obj = commit.get('date') if isinstance(commit, dict) else None
                date_str = date_obj.strftime("%m/%d") if date_obj else "N/A"
                subject = commit.get('subject', '') if isinstance(commit, dict) else str(commit)
                author = commit.get('author', 'unknown') if isinstance(commit, dict) else 'unknown'
            
            subject_display = subject[:50] + "..." if len(subject) > 50 else subject
            table.add_row(
                str(i),
                date_str,
                subject_display,
                author
            )
        
        if len(commits) > 15:
            table.add_row("", "", f"[dim]... and {len(commits) - 15} more[/]", "")
        
        self.console.print()
        self.console.print(table)
    
    def print_error(self, message: str) -> None:
        """Print an error message."""
        self.console.print()
        self.console.print(
            Panel(
                Text(f"❌ {message}", style="bold red"),
                border_style="red",
                box=box.ROUNDED
            )
        )
    
    def print_warning(self, message: str) -> None:
        """Print a warning message."""
        self.console.print(f"[yellow]⚠️  {message}[/]")
    
    def print_info(self, message: str) -> None:
        """Print an info message."""
        self.console.print(f"[blue]ℹ️  {message}[/]")
    
    def print_success(self, message: str) -> None:
        """Print a success message."""
        self.console.print(f"[green]✅ {message}[/]")
    
    def print_no_changes(self) -> None:
        """Print message when there are no changes."""
        self.console.print()
        self.console.print(
            Panel(
                Text("✨ Working tree is clean. No uncommitted changes.", 
                     justify="center", style="green"),
                style="green",
                box=box.ROUNDED
            )
        )
    
    def print_last_activity(self, last_activity: Optional[datetime]) -> None:
        """Print when the repo was last worked on."""
        if last_activity:
            now = datetime.now(last_activity.tzinfo)
            delta = now - last_activity
            
            if delta.days == 0:
                if delta.seconds < 3600:
                    time_str = f"{delta.seconds // 60} minutes ago"
                else:
                    time_str = f"{delta.seconds // 3600} hours ago"
            elif delta.days == 1:
                time_str = "Yesterday"
            else:
                time_str = f"{delta.days} days ago"
            
            self.console.print(
                f"🕐 Last activity: [bold]{time_str}[/] "
                f"[dim]({last_activity.strftime('%Y-%m-%d %H:%M')})[/]"
            )
    
    def create_spinner(self, message: str = "Processing..."):
        """Create a spinner context manager for async operations."""
        return Progress(
            SpinnerColumn(style="cyan"),
            TextColumn("[cyan]{task.description}"),
            console=self.console,
            transient=True
        )
    
    def print_step(self, step: int, total: int, message: str, done: bool = False) -> None:
        """Print a step in a multi-step process."""
        icon = "✓" if done else "⠋"
        style = "green" if done else "cyan"
        self.console.print(f"  [{style}]{icon}[/] [{style}]{message}[/] [dim]({step}/{total})[/]")
    
    def print_file_tree(self, files: list[str], title: str = "📁 Changed Files") -> None:
        """Print files in a tree view structure."""
        if not files:
            return
        
        self.console.print()
        tree = Tree(f"[bold cyan]{title}[/]", guide_style="dim")
        
        # Group files by directory
        dirs = {}
        for file_path in files:
            parts = file_path.replace("\\", "/").split("/")
            if len(parts) == 1:
                # Root level file
                icon = self._get_file_icon(parts[0])
                tree.add(f"{icon} [white]{parts[0]}[/]")
            else:
                # Nested file
                dir_path = "/".join(parts[:-1])
                if dir_path not in dirs:
                    dirs[dir_path] = tree.add(f"[bold yellow]📂 {dir_path}/[/]")
                icon = self._get_file_icon(parts[-1])
                dirs[dir_path].add(f"{icon} [white]{parts[-1]}[/]")
        
        self.console.print(tree)
    
    def _get_file_icon(self, filename: str) -> str:
        """Get an icon for a file based on its extension."""
        ext = filename.split(".")[-1].lower() if "." in filename else ""
        icons = {
            "py": "🐍",
            "js": "📜",
            "ts": "📘",
            "jsx": "⚛️",
            "tsx": "⚛️",
            "json": "📋",
            "md": "📝",
            "css": "🎨",
            "html": "🌐",
            "yml": "⚙️",
            "yaml": "⚙️",
            "toml": "⚙️",
            "txt": "📄",
            "sh": "🔧",
            "sql": "🗃️",
        }
        return icons.get(ext, "📄")
    
    def print_gradient_text(self, text: str, colors: list[str] = None) -> None:
        """Print text with gradient colors."""
        if colors is None:
            colors = ["bright_cyan", "cyan", "bright_blue", "blue", "magenta", "bright_magenta"]
        
        gradient_text = Text()
        for i, char in enumerate(text):
            color = colors[i % len(colors)]
            gradient_text.append(char, style=f"bold {color}")
        
        self.console.print(gradient_text)

