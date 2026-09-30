#!/usr/bin/env python3
"""
Command-line task manager with SQLite storage.
"""

import click
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Optional, List
import os


class TaskDatabase:
    """Handles all database operations for tasks."""

    def __init__(self, db_path: str = "tasks.db"):
        self.db_path = db_path
        self.init_database()

    def init_database(self):
        """Initialize the database with required tables."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                priority TEXT CHECK(priority IN ('low', 'medium', 'high')) DEFAULT 'medium',
                status TEXT CHECK(status IN ('pending', 'in_progress', 'completed')) DEFAULT 'pending',
                due_date TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)

        conn.commit()
        conn.close()

    def create_task(self, title: str, description: Optional[str] = None,
                   priority: str = 'medium', due_date: Optional[str] = None) -> int:
        """Create a new task."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        now = datetime.now().isoformat()

        cursor.execute("""
            INSERT INTO tasks (title, description, priority, due_date, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (title, description, priority, due_date, now, now))

        task_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return task_id

    def get_task(self, task_id: int) -> Optional[dict]:
        """Get a single task by ID."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
        row = cursor.fetchone()
        conn.close()

        if row:
            return dict(row)
        return None

    def get_all_tasks(self, status: Optional[str] = None,
                     priority: Optional[str] = None,
                     search: Optional[str] = None) -> List[dict]:
        """Get all tasks with optional filters."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        query = "SELECT * FROM tasks WHERE 1=1"
        params = []

        if status:
            query += " AND status = ?"
            params.append(status)

        if priority:
            query += " AND priority = ?"
            params.append(priority)

        if search:
            query += " AND (title LIKE ? OR description LIKE ?)"
            search_pattern = f"%{search}%"
            params.extend([search_pattern, search_pattern])

        query += " ORDER BY created_at DESC"

        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()

        return [dict(row) for row in rows]

    def update_task(self, task_id: int, title: Optional[str] = None,
                   description: Optional[str] = None, priority: Optional[str] = None,
                   status: Optional[str] = None, due_date: Optional[str] = None) -> bool:
        """Update a task."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Build dynamic update query
        updates = []
        params = []

        if title is not None:
            updates.append("title = ?")
            params.append(title)

        if description is not None:
            updates.append("description = ?")
            params.append(description)

        if priority is not None:
            updates.append("priority = ?")
            params.append(priority)

        if status is not None:
            updates.append("status = ?")
            params.append(status)

        if due_date is not None:
            updates.append("due_date = ?")
            params.append(due_date)

        if not updates:
            conn.close()
            return False

        updates.append("updated_at = ?")
        params.append(datetime.now().isoformat())

        params.append(task_id)

        query = f"UPDATE tasks SET {', '.join(updates)} WHERE id = ?"
        cursor.execute(query, params)

        affected = cursor.rowcount > 0
        conn.commit()
        conn.close()

        return affected

    def delete_task(self, task_id: int) -> bool:
        """Delete a task."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))

        affected = cursor.rowcount > 0
        conn.commit()
        conn.close()

        return affected


# Initialize database
db = TaskDatabase()


@click.group()
def cli():
    """Task Manager - A simple CLI task management tool."""
    pass


@cli.command()
@click.argument('title')
@click.option('--description', '-d', help='Task description')
@click.option('--priority', '-p', type=click.Choice(['low', 'medium', 'high']),
              default='medium', help='Task priority')
@click.option('--due-date', help='Due date (YYYY-MM-DD format)')
def add(title: str, description: Optional[str], priority: str, due_date: Optional[str]):
    """Add a new task."""
    # Validate due date format if provided
    if due_date:
        try:
            datetime.strptime(due_date, '%Y-%m-%d')
        except ValueError:
            click.echo(click.style('Error: Due date must be in YYYY-MM-DD format', fg='red'))
            return

    task_id = db.create_task(title, description, priority, due_date)
    click.echo(click.style(f'✓ Task created with ID: {task_id}', fg='green'))


@cli.command()
@click.argument('task_id', type=int)
def show(task_id: int):
    """Show details of a specific task."""
    task = db.get_task(task_id)

    if not task:
        click.echo(click.style(f'Error: Task {task_id} not found', fg='red'))
        return

    click.echo(click.style(f"\n━━━ Task #{task['id']} ━━━", fg='cyan', bold=True))
    click.echo(f"Title:       {task['title']}")
    click.echo(f"Status:      {format_status(task['status'])}")
    click.echo(f"Priority:    {format_priority(task['priority'])}")

    if task['description']:
        click.echo(f"Description: {task['description']}")

    if task['due_date']:
        click.echo(f"Due Date:    {task['due_date']}")

    click.echo(f"Created:     {format_datetime(task['created_at'])}")
    click.echo(f"Updated:     {format_datetime(task['updated_at'])}")
    click.echo()


@cli.command()
@click.option('--status', '-s', type=click.Choice(['pending', 'in_progress', 'completed']),
              help='Filter by status')
@click.option('--priority', '-p', type=click.Choice(['low', 'medium', 'high']),
              help='Filter by priority')
@click.option('--search', help='Search in title and description')
def list(status: Optional[str], priority: Optional[str], search: Optional[str]):
    """List all tasks with optional filters."""
    tasks = db.get_all_tasks(status, priority, search)

    if not tasks:
        click.echo(click.style('No tasks found.', fg='yellow'))
        return

    click.echo(click.style(f"\n{'ID':<6} {'Title':<35} {'Priority':<10} {'Status':<15} {'Due Date':<12}",
                          fg='cyan', bold=True))
    click.echo("─" * 85)

    for task in tasks:
        due_date_str = task['due_date'] if task['due_date'] else '—'
        title_truncated = task['title'][:32] + '...' if len(task['title']) > 35 else task['title']

        click.echo(
            f"{task['id']:<6} "
            f"{title_truncated:<35} "
            f"{format_priority(task['priority']):<20} "
            f"{format_status(task['status']):<25} "
            f"{due_date_str:<12}"
        )

    click.echo(f"\nTotal: {len(tasks)} task(s)\n")


@cli.command()
@click.argument('task_id', type=int)
@click.option('--title', '-t', help='New title')
@click.option('--description', '-d', help='New description')
@click.option('--priority', '-p', type=click.Choice(['low', 'medium', 'high']),
              help='New priority')
@click.option('--status', '-s', type=click.Choice(['pending', 'in_progress', 'completed']),
              help='New status')
@click.option('--due-date', help='New due date (YYYY-MM-DD format)')
def update(task_id: int, title: Optional[str], description: Optional[str],
          priority: Optional[str], status: Optional[str], due_date: Optional[str]):
    """Update an existing task."""
    # Validate due date format if provided
    if due_date:
        try:
            datetime.strptime(due_date, '%Y-%m-%d')
        except ValueError:
            click.echo(click.style('Error: Due date must be in YYYY-MM-DD format', fg='red'))
            return

    success = db.update_task(task_id, title, description, priority, status, due_date)

    if success:
        click.echo(click.style(f'✓ Task {task_id} updated successfully', fg='green'))
    else:
        click.echo(click.style(f'Error: Task {task_id} not found or no changes made', fg='red'))


@cli.command()
@click.argument('task_id', type=int)
@click.confirmation_option(prompt='Are you sure you want to delete this task?')
def delete(task_id: int):
    """Delete a task."""
    success = db.delete_task(task_id)

    if success:
        click.echo(click.style(f'✓ Task {task_id} deleted successfully', fg='green'))
    else:
        click.echo(click.style(f'Error: Task {task_id} not found', fg='red'))


@cli.command()
@click.argument('task_id', type=int)
def complete(task_id: int):
    """Mark a task as completed."""
    success = db.update_task(task_id, status='completed')

    if success:
        click.echo(click.style(f'✓ Task {task_id} marked as completed', fg='green'))
    else:
        click.echo(click.style(f'Error: Task {task_id} not found', fg='red'))


def format_priority(priority: str) -> str:
    """Format priority with color."""
    colors = {
        'low': 'blue',
        'medium': 'yellow',
        'high': 'red'
    }
    symbols = {
        'low': '↓',
        'medium': '•',
        'high': '↑'
    }
    return click.style(f"{symbols[priority]} {priority.upper()}", fg=colors[priority])


def format_status(status: str) -> str:
    """Format status with color."""
    colors = {
        'pending': 'yellow',
        'in_progress': 'blue',
        'completed': 'green'
    }
    symbols = {
        'pending': '○',
        'in_progress': '◐',
        'completed': '●'
    }
    display_text = status.replace('_', ' ').upper()
    return click.style(f"{symbols[status]} {display_text}", fg=colors[status])


def format_datetime(dt_str: str) -> str:
    """Format datetime string to more readable format."""
    try:
        dt = datetime.fromisoformat(dt_str)
        return dt.strftime('%Y-%m-%d %H:%M')
    except:
        return dt_str


if __name__ == '__main__':
    cli()
