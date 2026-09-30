#!/usr/bin/env python3
"""Command-line task manager with SQLite storage."""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable, List, Optional

import click

DB_PATH = Path(__file__).with_name("tasks.db")
PRIORITY_LEVELS = ["low", "medium", "high", "critical"]


@dataclass
class Task:
    id: int
    title: str
    description: str
    priority: str
    due_date: Optional[str]
    status: str
    created_at: str
    updated_at: str


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                priority TEXT NOT NULL,
                due_date TEXT,
                status TEXT NOT NULL DEFAULT 'pending',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        conn.commit()


def validate_priority(ctx: click.Context, param: click.Parameter, value: str) -> str:
    if value not in PRIORITY_LEVELS:
        raise click.BadParameter(f"Priority must be one of {', '.join(PRIORITY_LEVELS)}")
    return value


def parse_due_date(value: Optional[str]) -> Optional[str]:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value).date().isoformat()
    except ValueError as exc:
        raise click.BadParameter("Due date must be in ISO format YYYY-MM-DD") from exc


def fetch_tasks(where_clause: str = "", params: Iterable = ()) -> List[Task]:
    query = "SELECT * FROM tasks"
    if where_clause:
        query += f" WHERE {where_clause}"
    query += " ORDER BY CASE priority WHEN 'critical' THEN 1 WHEN 'high' THEN 2 WHEN 'medium' THEN 3 ELSE 4 END, due_date IS NULL, due_date"

    with get_connection() as conn:
        cursor = conn.execute(query, params)
        rows = cursor.fetchall()
    return [Task(**dict(row)) for row in rows]


def show_tasks(tasks: List[Task]) -> None:
    if not tasks:
        click.echo("No tasks found.")
        return
    for task in tasks:
        click.echo(f"[{task.id}] {task.title}")
        click.echo(f"    Priority: {task.priority} | Status: {task.status}")
        if task.due_date:
            click.echo(f"    Due: {task.due_date}")
        if task.description:
            click.echo(f"    {task.description}")
        click.echo(f"    Created: {task.created_at} | Updated: {task.updated_at}")
        click.echo("")


@click.group()
def cli() -> None:
    """Task manager CLI."""
    init_db()


@cli.command()
@click.option("--title", prompt=True, help="Title for the task")
@click.option("--description", default="", help="Optional description")
@click.option("--priority", default="medium", callback=validate_priority, help="Priority level")
@click.option("--due-date", callback=lambda ctx, param, value: parse_due_date(value), help="Due date YYYY-MM-DD")
def add(title: str, description: str, priority: str, due_date: Optional[str]) -> None:
    """Create a new task."""
    now = datetime.utcnow().isoformat()
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO tasks (title, description, priority, due_date, status, created_at, updated_at)
            VALUES (?, ?, ?, ?, 'pending', ?, ?)
            """,
            (title, description, priority, due_date, now, now),
        )
        conn.commit()
    click.echo("Task added successfully.")


@cli.command()
@click.option("--status", type=click.Choice(["pending", "in_progress", "completed", "archived"]))
@click.option("--priority", callback=lambda ctx, param, value: validate_priority(ctx, param, value) if value else value)
@click.option("--due-before", help="Filter tasks due before date YYYY-MM-DD")
@click.option("--search", help="Search keyword in title or description")
def list(status: Optional[str], priority: Optional[str], due_before: Optional[str], search: Optional[str]) -> None:
    """List tasks with optional filters."""
    clauses = []
    params: List = []

    if status:
        clauses.append("status = ?")
        params.append(status)
    if priority:
        clauses.append("priority = ?")
        params.append(priority)
    if due_before:
        clauses.append("due_date <= ?")
        params.append(parse_due_date(due_before))
    if search:
        clauses.append("(title LIKE ? OR description LIKE ?)")
        params.extend([f"%{search}%", f"%{search}%"])

    where_clause = " AND ".join(filter(None, clauses))
    show_tasks(fetch_tasks(where_clause, params))


@cli.command()
@click.argument("task_id", type=int)
@click.option("--title", help="New title")
@click.option("--description", help="New description")
@click.option("--priority", callback=lambda ctx, param, value: validate_priority(ctx, param, value) if value else value)
@click.option("--due-date", callback=lambda ctx, param, value: parse_due_date(value) if value else value)
@click.option("--status", type=click.Choice(["pending", "in_progress", "completed", "archived"]))
def update(task_id: int, title: Optional[str], description: Optional[str], priority: Optional[str], due_date: Optional[str], status: Optional[str]) -> None:
    """Update an existing task."""
    fields = []
    params: List = []
    if title is not None:
        fields.append("title = ?")
        params.append(title)
    if description is not None:
        fields.append("description = ?")
        params.append(description)
    if priority is not None:
        fields.append("priority = ?")
        params.append(priority)
    if due_date is not None:
        fields.append("due_date = ?")
        params.append(due_date)
    if status is not None:
        fields.append("status = ?")
        params.append(status)

    if not fields:
        click.echo("No updates provided.")
        return

    fields.append("updated_at = ?")
    params.append(datetime.utcnow().isoformat())
    params.append(task_id)

    with get_connection() as conn:
        cursor = conn.execute(
            f"UPDATE tasks SET {', '.join(fields)} WHERE id = ?",
            params,
        )
        conn.commit()
        if cursor.rowcount == 0:
            click.echo("Task not found.")
        else:
            click.echo("Task updated successfully.")


@cli.command()
@click.argument("task_id", type=int)
def delete(task_id: int) -> None:
    """Delete a task by ID."""
    with get_connection() as conn:
        cursor = conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        conn.commit()
        if cursor.rowcount == 0:
            click.echo("Task not found.")
        else:
            click.echo("Task deleted.")


@cli.command()
@click.argument("task_id", type=int)
def show(task_id: int) -> None:
    """Show a single task."""
    tasks = fetch_tasks("id = ?", (task_id,))
    if not tasks:
        click.echo("Task not found.")
    else:
        show_tasks(tasks)


if __name__ == "__main__":
    cli()
