# SQLite Task Manager CLI

A command-line task manager built with Click and SQLite. Supports CRUD operations, priorities, due dates, and filtering/search.

## Setup
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Usage

### Add a task
```bash
python task_manager.py add --title "Finish report" --priority high --due-date 2024-01-15
```
(Description prompts interactively or via `--description`.)

### List tasks with filters
```bash
python task_manager.py list --status pending --priority high --search report
```

### Update a task
```bash
python task_manager.py update 1 --status completed
```

### Delete a task
```bash
python task_manager.py delete 1
```

### Show a task
```bash
python task_manager.py show 2
```

Priorities: `low`, `medium`, `high`, `critical`. Status options: `pending`, `in_progress`, `completed`, `archived`. Due dates use ISO format (YYYY-MM-DD). Tasks are stored in `tasks.db` alongside the script and created automatically.
