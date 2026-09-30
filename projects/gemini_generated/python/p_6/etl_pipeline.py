import pandas as pd
from sqlalchemy import create_engine
import os

# --- Configuration ---
CSV_FILE = "source_data.csv"
DB_FILE = "company.db"
TABLE_NAME = "employees"
REPORT_FILE = "summary_statistics_report.txt"

def extract(file_path):
    """Extracts data from a CSV file into a pandas DataFrame."""
    print(f"\n[E]xtracting data from {file_path}...")
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Source file not found: {file_path}")
    df = pd.read_csv(file_path)
    print("Extraction complete.")
    return df

def transform(df):
    """Transforms the DataFrame by cleaning data and generating a report."""
    print("\n[T]ransforming data...")
    
    # --- Handle Missing Values ---
    # Fill missing salary with the median salary of the respective department
    df['salary'] = df.groupby('department')['salary'].transform(lambda x: x.fillna(x.median()))
    # If any department has all NaNs, fill remaining with global median
    global_median_salary = df['salary'].median()
    df['salary'].fillna(global_median_salary, inplace=True)

    # Fill missing manager_id with 0 as a placeholder
    df['manager_id'].fillna(0, inplace=True)
    
    # --- Data Type Conversion ---
    df['start_date'] = pd.to_datetime(df['start_date'])
    df['salary'] = df['salary'].astype(float)
    df['manager_id'] = df['manager_id'].astype(int)
    
    print("Data cleaning and type conversion complete.")

    # --- Generate Summary Statistics Report ---
    print(f"Generating summary report to {REPORT_FILE}...")
    report = df.describe(include='all', datetime_is_numeric=True)
    
    with open(REPORT_FILE, 'w') as f:
        f.write("--- Data Summary Statistics Report ---\n\n")
        f.write("DataFrame Info:\n")
        df.info(buf=f)
        f.write("\n\nDescriptive Statistics:\n")
        f.write(report.to_string())

    print("Report generation complete.")
    print("Transformation complete.")
    return df

def load(df, db_path, table_name):
    """Loads the transformed DataFrame into a SQLite database."""
    print(f"\n[L]oading data into {db_path}...")
    # Using SQLAlchemy to connect to the database
    engine = create_engine(f'sqlite:///{db_path}')
    
    # Write the DataFrame to the SQL table. 
    # if_exists='replace' makes the script idempotent.
    df.to_sql(table_name, con=engine, if_exists='replace', index=False)
    
    print(f"Data successfully loaded into table '{table_name}' in {db_path}.")
    print("Load complete.")

if __name__ == "__main__":
    print("--- Starting ETL Pipeline ---")
    try:
        # 1. Extract
        source_df = extract(CSV_FILE)
        
        # 2. Transform
        transformed_df = transform(source_df)
        
        # 3. Load
        load(transformed_df, DB_FILE, TABLE_NAME)
        
        print("\n--- ETL Pipeline Finished Successfully ---")
    except Exception as e:
        print(f"\n--- ETL Pipeline Failed: {e} ---")
