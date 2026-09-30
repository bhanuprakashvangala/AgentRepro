# Simple ETL Pipeline

This project demonstrates a basic ETL (Extract, Transform, Load) pipeline using Python. It reads employee data from a CSV file, cleans and transforms the data using `pandas`, and loads it into a SQLite database using `sqlalchemy`.

## Features

- **Extract**: Reads data from `source_data.csv`.
- **Transform**: 
    - Handles missing `salary` values by filling them with the median salary of the employee's department.
    - Fills missing `manager_id` values.
    - Converts columns to their appropriate data types.
    - Generates a `summary_statistics_report.txt` with descriptive statistics about the data.
- **Load**: Creates and populates an `employees` table in a SQLite database file (`company.db`).

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

3.  **Run the ETL pipeline:**
    ```bash
    python etl_pipeline.py
    ```

## Output

After running the script, the following files will be created in the project directory:

1.  `company.db`: A SQLite database file containing the cleaned `employees` data.
2.  `summary_statistics_report.txt`: A text file containing detailed information and descriptive statistics about the transformed data.

The script will also print its progress to the console.
