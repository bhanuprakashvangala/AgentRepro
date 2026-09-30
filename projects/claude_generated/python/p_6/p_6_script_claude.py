"""
ETL Pipeline: Extract data from CSV, Transform, and Load to SQLite
"""
import pandas as pd
import numpy as np
from sqlalchemy import create_engine, Column, Integer, Float, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

Base = declarative_base()

class SalesData(Base):
    """SQLAlchemy model for sales data"""
    __tablename__ = 'sales_data'

    id = Column(Integer, primary_key=True)
    date = Column(DateTime)
    product = Column(String(100))
    category = Column(String(50))
    quantity = Column(Integer)
    unit_price = Column(Float)
    total_amount = Column(Float)
    region = Column(String(50))
    customer_segment = Column(String(50))


class ETLPipeline:
    """ETL Pipeline for processing sales data"""

    def __init__(self, csv_path, db_path='sales_data.db'):
        self.csv_path = csv_path
        self.db_path = db_path
        self.engine = create_engine(f'sqlite:///{db_path}')
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    def extract(self):
        """Extract data from CSV file"""
        logger.info(f"Extracting data from {self.csv_path}")
        try:
            df = pd.read_csv(self.csv_path)
            logger.info(f"Successfully extracted {len(df)} records")
            return df
        except FileNotFoundError:
            logger.error(f"File not found: {self.csv_path}")
            raise
        except Exception as e:
            logger.error(f"Error extracting data: {str(e)}")
            raise

    def transform(self, df):
        """Transform and clean the data"""
        logger.info("Starting data transformation")

        # Create a copy to avoid modifying original
        df_transformed = df.copy()

        # Convert date column to datetime
        if 'date' in df_transformed.columns:
            df_transformed['date'] = pd.to_datetime(df_transformed['date'], errors='coerce')

        # Handle missing values
        logger.info("Handling missing values")

        # Fill numeric columns with median
        numeric_columns = df_transformed.select_dtypes(include=[np.number]).columns
        for col in numeric_columns:
            if df_transformed[col].isnull().any():
                median_value = df_transformed[col].median()
                df_transformed[col].fillna(median_value, inplace=True)
                logger.info(f"Filled {col} missing values with median: {median_value}")

        # Fill categorical columns with mode or 'Unknown'
        categorical_columns = df_transformed.select_dtypes(include=['object']).columns
        for col in categorical_columns:
            if col != 'date' and df_transformed[col].isnull().any():
                mode_value = df_transformed[col].mode()
                if len(mode_value) > 0:
                    df_transformed[col].fillna(mode_value[0], inplace=True)
                else:
                    df_transformed[col].fillna('Unknown', inplace=True)
                logger.info(f"Filled {col} missing values")

        # Calculate total_amount if not present
        if 'total_amount' not in df_transformed.columns:
            if 'quantity' in df_transformed.columns and 'unit_price' in df_transformed.columns:
                df_transformed['total_amount'] = df_transformed['quantity'] * df_transformed['unit_price']
                logger.info("Calculated total_amount from quantity and unit_price")

        # Remove duplicates
        initial_count = len(df_transformed)
        df_transformed.drop_duplicates(inplace=True)
        removed_count = initial_count - len(df_transformed)
        if removed_count > 0:
            logger.info(f"Removed {removed_count} duplicate records")

        # Remove rows with invalid data (e.g., negative quantities or prices)
        if 'quantity' in df_transformed.columns:
            df_transformed = df_transformed[df_transformed['quantity'] >= 0]
        if 'unit_price' in df_transformed.columns:
            df_transformed = df_transformed[df_transformed['unit_price'] >= 0]

        logger.info(f"Transformation complete. Final record count: {len(df_transformed)}")
        return df_transformed

    def load(self, df):
        """Load data into SQLite database"""
        logger.info(f"Loading data to database: {self.db_path}")
        try:
            # Load data to database
            df.to_sql('sales_data', self.engine, if_exists='replace', index=False)
            logger.info(f"Successfully loaded {len(df)} records to database")
        except Exception as e:
            logger.error(f"Error loading data: {str(e)}")
            raise

    def generate_summary_report(self, df):
        """Generate summary statistics report"""
        logger.info("Generating summary statistics report")

        report = []
        report.append("=" * 80)
        report.append("ETL PIPELINE SUMMARY REPORT")
        report.append("=" * 80)
        report.append(f"Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Total Records Processed: {len(df)}")
        report.append("\n" + "-" * 80)
        report.append("DATA OVERVIEW")
        report.append("-" * 80)

        # Basic statistics
        report.append(f"\nDataset Shape: {df.shape[0]} rows × {df.shape[1]} columns")
        report.append(f"\nColumns: {', '.join(df.columns.tolist())}")

        # Numeric columns statistics
        numeric_df = df.select_dtypes(include=[np.number])
        if not numeric_df.empty:
            report.append("\n" + "-" * 80)
            report.append("NUMERIC STATISTICS")
            report.append("-" * 80)
            report.append("\n" + numeric_df.describe().to_string())

        # Categorical columns statistics
        categorical_df = df.select_dtypes(include=['object'])
        if not categorical_df.empty:
            report.append("\n" + "-" * 80)
            report.append("CATEGORICAL STATISTICS")
            report.append("-" * 80)
            for col in categorical_df.columns:
                if col != 'date':
                    unique_count = df[col].nunique()
                    report.append(f"\n{col}:")
                    report.append(f"  Unique values: {unique_count}")
                    if unique_count <= 10:
                        value_counts = df[col].value_counts()
                        report.append("  Value distribution:")
                        for val, count in value_counts.items():
                            report.append(f"    {val}: {count}")

        # Business metrics (if applicable columns exist)
        if 'total_amount' in df.columns:
            report.append("\n" + "-" * 80)
            report.append("BUSINESS METRICS")
            report.append("-" * 80)
            report.append(f"\nTotal Revenue: ${df['total_amount'].sum():,.2f}")
            report.append(f"Average Transaction: ${df['total_amount'].mean():,.2f}")
            report.append(f"Median Transaction: ${df['total_amount'].median():,.2f}")

            if 'category' in df.columns:
                report.append("\nRevenue by Category:")
                category_revenue = df.groupby('category')['total_amount'].sum().sort_values(ascending=False)
                for cat, rev in category_revenue.items():
                    report.append(f"  {cat}: ${rev:,.2f}")

            if 'region' in df.columns:
                report.append("\nRevenue by Region:")
                region_revenue = df.groupby('region')['total_amount'].sum().sort_values(ascending=False)
                for reg, rev in region_revenue.items():
                    report.append(f"  {reg}: ${rev:,.2f}")

        # Missing values report
        missing_counts = df.isnull().sum()
        if missing_counts.sum() > 0:
            report.append("\n" + "-" * 80)
            report.append("MISSING VALUES (After Transformation)")
            report.append("-" * 80)
            for col, count in missing_counts.items():
                if count > 0:
                    report.append(f"{col}: {count} ({count/len(df)*100:.2f}%)")
        else:
            report.append("\n" + "-" * 80)
            report.append("No missing values in the dataset!")

        report.append("\n" + "=" * 80)

        report_text = "\n".join(report)

        # Save report to file
        with open('etl_summary_report.txt', 'w') as f:
            f.write(report_text)

        logger.info("Summary report saved to etl_summary_report.txt")
        print("\n" + report_text)

        return report_text

    def run(self):
        """Execute the complete ETL pipeline"""
        logger.info("Starting ETL Pipeline")

        try:
            # Extract
            df_raw = self.extract()

            # Transform
            df_transformed = self.transform(df_raw)

            # Load
            self.load(df_transformed)

            # Generate report
            self.generate_summary_report(df_transformed)

            logger.info("ETL Pipeline completed successfully")
            return True

        except Exception as e:
            logger.error(f"ETL Pipeline failed: {str(e)}")
            return False


def create_sample_csv(filename='sample_sales_data.csv'):
    """Create a sample CSV file for testing"""
    np.random.seed(42)

    data = {
        'date': pd.date_range('2024-01-01', periods=100, freq='D').tolist(),
        'product': np.random.choice(['Laptop', 'Mouse', 'Keyboard', 'Monitor', 'Headphones'], 100),
        'category': np.random.choice(['Electronics', 'Accessories', 'Peripherals'], 100),
        'quantity': np.random.randint(1, 20, 100),
        'unit_price': np.random.uniform(10, 1000, 100).round(2),
        'region': np.random.choice(['North', 'South', 'East', 'West'], 100),
        'customer_segment': np.random.choice(['Enterprise', 'SMB', 'Consumer'], 100)
    }

    df = pd.DataFrame(data)

    # Introduce some missing values
    df.loc[np.random.choice(df.index, 10), 'quantity'] = np.nan
    df.loc[np.random.choice(df.index, 5), 'region'] = np.nan

    df.to_csv(filename, index=False)
    logger.info(f"Sample CSV file created: {filename}")


if __name__ == "__main__":
    # Create sample data
    print("Creating sample CSV data...")
    create_sample_csv()

    # Run ETL pipeline
    print("\nRunning ETL Pipeline...")
    pipeline = ETLPipeline(csv_path='sample_sales_data.csv')
    success = pipeline.run()

    if success:
        print("\n✓ ETL Pipeline completed successfully!")
        print(f"✓ Database created: sales_data.db")
        print(f"✓ Summary report saved: etl_summary_report.txt")
    else:
        print("\n✗ ETL Pipeline failed. Check logs for details.")
