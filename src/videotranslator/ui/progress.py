"""Progress tracking and status display using Rich."""

from contextlib import contextmanager
from typing import Generator

from rich.console import Console
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TaskID,
    TextColumn,
    TimeElapsedColumn,
    TimeRemainingColumn,
)
from rich.table import Table


class ProgressManager:
    """Manages progress bars and status display for video processing."""

    def __init__(self):
        """Initialize the progress manager."""
        self.console = Console()
        self.progress = Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeElapsedColumn(),
            TimeRemainingColumn(),
            console=self.console,
        )

    @contextmanager
    def task(self, description: str, total: float = 100.0) -> Generator[TaskID, None, None]:
        """
        Context manager for tracking a task with a progress bar.

        Args:
            description: Task description to display
            total: Total units of work

        Yields:
            TaskID for updating progress
        """
        with self.progress:
            task_id = self.progress.add_task(description, total=total)
            yield task_id

    def update(self, task_id: TaskID, advance: float = 1.0, description: str | None = None):
        """
        Update a task's progress.

        Args:
            task_id: ID of the task to update
            advance: Amount to advance progress by
            description: Optional new description
        """
        self.progress.update(task_id, advance=advance, description=description)

    def success(self, message: str):
        """Display a success message."""
        self.console.print(f"[bold green]✓[/bold green] {message}")

    def error(self, message: str):
        """Display an error message."""
        self.console.print(f"[bold red]✗[/bold red] {message}")

    def info(self, message: str):
        """Display an info message."""
        self.console.print(f"[bold blue]ℹ[/bold blue] {message}")

    def warning(self, message: str):
        """Display a warning message."""
        self.console.print(f"[bold yellow]⚠[/bold yellow] {message}")

    def status_table(self, title: str, data: dict[str, str]):
        """
        Display a status table.

        Args:
            title: Table title
            data: Dictionary of key-value pairs to display
        """
        table = Table(title=title, show_header=True, header_style="bold magenta")
        table.add_column("Property", style="cyan", width=25)
        table.add_column("Value", style="green")

        for key, value in data.items():
            table.add_row(key, str(value))

        self.console.print(table)
