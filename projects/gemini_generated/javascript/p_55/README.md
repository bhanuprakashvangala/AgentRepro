# Command-Line Task Runner

This project is a command-line task runner application built with Commander.js and ora.

## Requirements

- Node.js
- npm

## Installation

1.  Install the dependencies:

    ```bash
    npm install
    ```

2.  Make the script executable:

    ```bash
    chmod +x task-runner.js
    ```

3.  (Optional) Create a symbolic link to make the command available globally:

    ```bash
    npm link
    ```

## Usage

Run the tasks using the following commands:

```bash
./task-runner.js task1
./task-runner.js task2
```

If you created a symbolic link, you can use the command directly:

```bash
task-runner task1
task-runner task2
```
