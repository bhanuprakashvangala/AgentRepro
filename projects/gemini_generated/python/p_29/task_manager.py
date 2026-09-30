import click
import sqlite3
from datetime import datetime

DATABASE_FILE = "tasks.db"

def get_db_connection():
    """Creates and returns a connection to the SQLite database."""
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initializes the database and creates the tasks table if it doesn't exist."""
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            priority INTEGER NOT NULL DEFAULT 3, -- 1:High, 2:Medium, 3:Low
            due_date TEXT,
            status TEXT NOT NULL DEFAULT 'pending', -- pending, done
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
    ''')
    conn.commit()
    conn.close()

def _print_tasks(tasks):
    """Helper function to print a list of tasks in a formatted table."""
    if not tasks:
        click.echo("No tasks found.")
        return

    click.echo(f"{'ID':<4} {'Priority':<10} {'Status':<10} {'Due Date':<12} {'Title':<40}")
    click.echo("-" * 80)
    priority_map = {1: 'High', 2: 'Medium', 3: 'Low'}
    for task in tasks:
        priority_str = priority_map.get(task['priority'], 'N/A')
        due_date_str = task['due_date'] if task['due_date'] else 'N/A'
        click.echo(f"{task['id']:<4} {priority_str:<10} {task['status']:<10} {due_date_str:<12} {task['title']:<40}")

@click.group()
def cli():
    """A simple command-line task manager using SQLite."""
    init_db()

@cli.command('add')
@click.argument('title')
@click.option('--priority', type=click.Choice(['1', '2', '3']), default='3', help='Priority: 1=High, 2=Medium, 3=Low.')
@click.option('--due-date', help='Due date in YYYY-MM-DD format.')
def add_task(title, priority, due_date):
    """Add a new task."""
    conn = get_db_connection()
    conn.execute(
        'INSERT INTO tasks (title, priority, due_date) VALUES (?, ?, ?)',
        (title, int(priority), due_date)
    )
    conn.commit()
    conn.close()
    click.echo(f"Added task: '{title}'")

@cli.command('list')
@click.option('--status', type=click.Choice(['all', 'pending', 'done']), default='pending', help='Filter by status.')
@click.option('--sort-by', type=click.Choice(['id', 'priority', 'due_date']), default='priority', help='Sort tasks.')
def list_tasks(status, sort_by):
    """List all tasks."""
    conn = get_db_connection()
    query = "SELECT * FROM tasks"
    if status != 'all':
        query += f" WHERE status = '{status}'"
    query += f" ORDER BY {sort_by}"
    tasks = conn.execute(query).fetchall()
    conn.close()
    _print_tasks(tasks)

@cli.command()
@click.argument('task_id', type=int)
@click.option('--title', help='New title for the task.')
@click.option('--priority', type=click.Choice(['1', '2', '3']), help='New priority.')
@click.option('--due-date', help='New due date (YYYY-MM-DD).')
@click.option('--status', type=click.Choice(['pending', 'done']), help='New status.')
def update(task_id, title, priority, due_date, status):
    """Update an existing task."""
    conn = get_db_connection()
    updates = []
    params = []
    if title: 
        updates.append("title = ?"); params.append(title)
    if priority: 
        updates.append("priority = ?"); params.append(int(priority))
    if due_date: 
        updates.append("due_date = ?"); params.append(due_date)
    if status: 
        updates.append("status = ?"); params.append(status)

    if not updates:
        click.echo("No update fields provided.")
        return

    params.append(task_id)
    query = f"UPDATE tasks SET { ', '.join(updates) } WHERE id = ?"
    cursor = conn.execute(query, tuple(params))
    conn.commit()
    conn.close()

    if cursor.rowcount == 0:
        click.echo(f"Error: No task found with ID {task_id}")
    else:
        click.echo(f"Task {task_id} updated successfully.")

@cli.command()
@click.argument('task_id', type=int)
def delete(task_id):
    """Delete a task."""
    conn = get_db_connection()
    cursor = conn.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
    conn.commit()
    conn.close()
    if cursor.rowcount == 0:
        click.echo(f"Error: No task found with ID {task_id}")
    else:
        click.echo(f"Task {task_id} deleted.")

@cli.command()
@click.argument('task_id', type=int)
def done(task_id):
    """Mark a task as done."""
    conn = get_db_connection()
    cursor = conn.execute('UPDATE tasks SET status = ? WHERE id = ?', ('done', task_id))
    conn.commit()
    conn.close()
    if cursor.rowcount == 0:
        click.echo(f"Error: No task found with ID {task_id}")
    else:
        click.echo(f"Task {task_id} marked as done.")

@cli.command()
@click.argument('term')
def search(term):
    """Search for tasks by title."""
    conn = get_db_connection()
    tasks = conn.execute("SELECT * FROM tasks WHERE title LIKE ? ORDER BY priority", (f'%{term}%',)).fetchall()
    conn.close()
    _print_tasks(tasks)

if __name__ == '__main__':
    cli()
