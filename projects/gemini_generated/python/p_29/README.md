# Command-Line Task Manager

This is a simple but powerful command-line task manager built with Python, `click`, and `sqlite3`.

## Features

- **Persistent Storage**: Tasks are stored in a local SQLite database file (`tasks.db`), so your data persists between sessions.
- **CRUD Operations**: Full support for Creating, Reading (Listing), Updating, and Deleting tasks.
- **Task Metadata**: Supports priority levels (1=High, 2=Medium, 3=Low), due dates, and status (pending/done).
- **Filtering & Sorting**: Easily list tasks filtered by status and sorted by priority, ID, or due date.
- **Search**: Find tasks with a simple title search.
- **Intuitive CLI**: Built with `click` for a clean, easy-to-use command-line interface.

## Usage

1.  **Set up a virtual environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Run the tool:**
    The script automatically creates and initializes the `tasks.db` database file the first time you run any command.

### Command Reference

**Add a new task:**
```bash
# Add with default priority (Low)
python task_manager.py add "Finish the report"

# Add with high priority and a due date
python task_manager.py add "Prepare presentation slides" --priority 1 --due-date 2024-11-15
```

**List tasks:**
```bash
# List pending tasks (default), sorted by priority
python task_manager.py list

# List all completed tasks
python task_manager.py list --status done

# List all tasks, sorted by due date
python task_manager.py list --status all --sort-by due_date
```

**Update a task:**
(Use `list` to find the ID of the task you want to modify)
```bash
python task_manager.py update 1 --priority 2 --status done
```

**Mark a task as done (shortcut):**
```bash
python task_manager.py done 1
```

**Delete a task:**
```bash
python task_manager.py delete 3
```

**Search for tasks:**
```bash
python task_manager.py search "report"
```
