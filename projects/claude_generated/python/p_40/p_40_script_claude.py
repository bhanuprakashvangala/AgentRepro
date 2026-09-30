"""
SQL Query Builder with Parameterization and SQL Injection Prevention
Supports SELECT, INSERT, UPDATE, DELETE queries with validation
"""

from typing import Any, Dict, List, Optional, Union, Tuple
from sqlalchemy import (
    create_engine,
    Table,
    Column,
    Integer,
    String,
    MetaData,
    select,
    insert,
    update,
    delete,
    text,
)
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.sql import Select, Insert, Update, Delete
from sqlalchemy.engine import Engine, Result
import re


class QueryValidationError(Exception):
    """Custom exception for query validation errors"""
    pass


class SQLQueryBuilder:
    """
    A safe SQL query builder with parameterization and SQL injection prevention.
    Uses SQLAlchemy's Core API for secure query construction.
    """

    def __init__(self, database_url: str = "sqlite:///example.db"):
        """
        Initialize the query builder with a database connection.

        Args:
            database_url: SQLAlchemy database URL (default: SQLite in-memory)
        """
        self.engine: Engine = create_engine(database_url, echo=False)
        self.metadata = MetaData()
        self.connection = None

    def connect(self):
        """Establish a database connection"""
        if self.connection is None:
            self.connection = self.engine.connect()
        return self.connection

    def close(self):
        """Close the database connection"""
        if self.connection:
            self.connection.close()
            self.connection = None

    def __enter__(self):
        """Context manager entry"""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()

    @staticmethod
    def validate_identifier(identifier: str) -> str:
        """
        Validate SQL identifiers (table names, column names) to prevent injection.

        Args:
            identifier: The identifier to validate

        Returns:
            The validated identifier

        Raises:
            QueryValidationError: If identifier is invalid
        """
        if not identifier:
            raise QueryValidationError("Identifier cannot be empty")

        # Allow alphanumeric characters, underscores, and dots (for schema.table)
        if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*(\.[a-zA-Z_][a-zA-Z0-9_]*)?$', identifier):
            raise QueryValidationError(
                f"Invalid identifier '{identifier}'. Only alphanumeric characters, "
                "underscores, and dots are allowed."
            )

        return identifier

    def select(
        self,
        table_name: str,
        columns: Optional[List[str]] = None,
        where: Optional[Dict[str, Any]] = None,
        order_by: Optional[Union[str, List[str]]] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Build a SELECT query with parameterization.

        Args:
            table_name: Name of the table to query
            columns: List of column names to select (None = all columns)
            where: Dictionary of column-value pairs for WHERE clause
            order_by: Column name(s) for ORDER BY clause
            limit: Maximum number of rows to return
            offset: Number of rows to skip

        Returns:
            Tuple of (query_string, parameters)
        """
        # Validate table name
        table_name = self.validate_identifier(table_name)

        # Build column list
        if columns:
            validated_columns = [self.validate_identifier(col) for col in columns]
            cols_str = ", ".join(validated_columns)
        else:
            cols_str = "*"

        # Start building query
        query = f"SELECT {cols_str} FROM {table_name}"
        params = {}

        # Add WHERE clause
        if where:
            where_clauses = []
            for i, (col, val) in enumerate(where.items()):
                validated_col = self.validate_identifier(col)
                param_name = f"where_{col}_{i}"
                where_clauses.append(f"{validated_col} = :{param_name}")
                params[param_name] = val
            query += " WHERE " + " AND ".join(where_clauses)

        # Add ORDER BY clause
        if order_by:
            if isinstance(order_by, str):
                order_by = [order_by]
            validated_order = [self.validate_identifier(col) for col in order_by]
            query += " ORDER BY " + ", ".join(validated_order)

        # Add LIMIT and OFFSET
        if limit is not None:
            if not isinstance(limit, int) or limit < 0:
                raise QueryValidationError("LIMIT must be a non-negative integer")
            query += f" LIMIT {limit}"

        if offset is not None:
            if not isinstance(offset, int) or offset < 0:
                raise QueryValidationError("OFFSET must be a non-negative integer")
            query += f" OFFSET {offset}"

        return query, params

    def insert(
        self,
        table_name: str,
        values: Union[Dict[str, Any], List[Dict[str, Any]]]
    ) -> Tuple[str, Union[Dict[str, Any], List[Dict[str, Any]]]]:
        """
        Build an INSERT query with parameterization.

        Args:
            table_name: Name of the table to insert into
            values: Dictionary or list of dictionaries with column-value pairs

        Returns:
            Tuple of (query_string, parameters)
        """
        # Validate table name
        table_name = self.validate_identifier(table_name)

        # Handle single row vs multiple rows
        if isinstance(values, dict):
            values = [values]

        if not values:
            raise QueryValidationError("No values provided for INSERT")

        # Validate all column names
        first_row = values[0]
        columns = [self.validate_identifier(col) for col in first_row.keys()]

        # Check all rows have the same columns
        for row in values:
            if set(row.keys()) != set(first_row.keys()):
                raise QueryValidationError("All rows must have the same columns")

        # Build query
        cols_str = ", ".join(columns)
        placeholders = ", ".join([f":{col}" for col in first_row.keys()])
        query = f"INSERT INTO {table_name} ({cols_str}) VALUES ({placeholders})"

        # For multiple rows, return the list
        if len(values) == 1:
            return query, values[0]
        else:
            return query, values

    def update(
        self,
        table_name: str,
        values: Dict[str, Any],
        where: Dict[str, Any]
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Build an UPDATE query with parameterization.

        Args:
            table_name: Name of the table to update
            values: Dictionary of column-value pairs to update
            where: Dictionary of column-value pairs for WHERE clause

        Returns:
            Tuple of (query_string, parameters)
        """
        # Validate table name
        table_name = self.validate_identifier(table_name)

        if not values:
            raise QueryValidationError("No values provided for UPDATE")

        if not where:
            raise QueryValidationError(
                "WHERE clause is required for UPDATE to prevent accidental mass updates"
            )

        # Build SET clause
        set_clauses = []
        params = {}
        for col, val in values.items():
            validated_col = self.validate_identifier(col)
            param_name = f"set_{col}"
            set_clauses.append(f"{validated_col} = :{param_name}")
            params[param_name] = val

        # Build WHERE clause
        where_clauses = []
        for col, val in where.items():
            validated_col = self.validate_identifier(col)
            param_name = f"where_{col}"
            where_clauses.append(f"{validated_col} = :{param_name}")
            params[param_name] = val

        query = (
            f"UPDATE {table_name} "
            f"SET {', '.join(set_clauses)} "
            f"WHERE {' AND '.join(where_clauses)}"
        )

        return query, params

    def delete(
        self,
        table_name: str,
        where: Dict[str, Any]
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Build a DELETE query with parameterization.

        Args:
            table_name: Name of the table to delete from
            where: Dictionary of column-value pairs for WHERE clause

        Returns:
            Tuple of (query_string, parameters)
        """
        # Validate table name
        table_name = self.validate_identifier(table_name)

        if not where:
            raise QueryValidationError(
                "WHERE clause is required for DELETE to prevent accidental mass deletions"
            )

        # Build WHERE clause
        where_clauses = []
        params = {}
        for col, val in where.items():
            validated_col = self.validate_identifier(col)
            param_name = f"where_{col}"
            where_clauses.append(f"{validated_col} = :{param_name}")
            params[param_name] = val

        query = f"DELETE FROM {table_name} WHERE {' AND '.join(where_clauses)}"

        return query, params

    def execute(
        self,
        query: str,
        params: Optional[Union[Dict[str, Any], List[Dict[str, Any]]]] = None
    ) -> Result:
        """
        Execute a parameterized query safely.

        Args:
            query: The SQL query string with parameter placeholders
            params: Parameters for the query (dict or list of dicts)

        Returns:
            SQLAlchemy Result object

        Raises:
            SQLAlchemyError: If query execution fails
        """
        if self.connection is None:
            raise RuntimeError("Database connection not established. Use connect() or context manager.")

        try:
            if params is None:
                params = {}

            # Execute with parameterization
            if isinstance(params, list):
                # Execute multiple rows
                result = self.connection.execute(text(query), params)
            else:
                # Execute single query
                result = self.connection.execute(text(query), params)

            self.connection.commit()
            return result

        except SQLAlchemyError as e:
            self.connection.rollback()
            raise SQLAlchemyError(f"Query execution failed: {str(e)}")

    def execute_select(
        self,
        table_name: str,
        columns: Optional[List[str]] = None,
        where: Optional[Dict[str, Any]] = None,
        order_by: Optional[Union[str, List[str]]] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Execute a SELECT query and return results as list of dictionaries.

        Returns:
            List of dictionaries representing rows
        """
        query, params = self.select(table_name, columns, where, order_by, limit, offset)
        result = self.execute(query, params)

        # Convert to list of dicts
        rows = []
        for row in result:
            rows.append(dict(row._mapping))

        return rows

    def execute_insert(
        self,
        table_name: str,
        values: Union[Dict[str, Any], List[Dict[str, Any]]]
    ) -> int:
        """
        Execute an INSERT query and return number of rows inserted.

        Returns:
            Number of rows inserted
        """
        query, params = self.insert(table_name, values)
        result = self.execute(query, params)
        return result.rowcount

    def execute_update(
        self,
        table_name: str,
        values: Dict[str, Any],
        where: Dict[str, Any]
    ) -> int:
        """
        Execute an UPDATE query and return number of rows affected.

        Returns:
            Number of rows updated
        """
        query, params = self.update(table_name, values, where)
        result = self.execute(query, params)
        return result.rowcount

    def execute_delete(
        self,
        table_name: str,
        where: Dict[str, Any]
    ) -> int:
        """
        Execute a DELETE query and return number of rows affected.

        Returns:
            Number of rows deleted
        """
        query, params = self.delete(table_name, where)
        result = self.execute(query, params)
        return result.rowcount


# Example usage and demonstration
def main():
    """Demonstrate the SQL query builder with various operations"""

    # Create a query builder instance (using SQLite for demo)
    qb = SQLQueryBuilder("sqlite:///demo.db")

    # Create a demo table
    with qb.engine.connect() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                age INTEGER
            )
        """))
        conn.commit()

        # Clear existing data
        conn.execute(text("DELETE FROM users"))
        conn.commit()

    print("=" * 60)
    print("SQL Query Builder Demo - Secure Parameterized Queries")
    print("=" * 60)

    # Use context manager for automatic connection handling
    with qb:
        # 1. INSERT examples
        print("\n1. INSERT Operations:")
        print("-" * 60)

        # Single insert
        query, params = qb.insert("users", {
            "name": "Alice Smith",
            "email": "alice@example.com",
            "age": 30
        })
        print(f"Query: {query}")
        print(f"Params: {params}")
        qb.execute(query, params)
        print("✓ Inserted 1 user")

        # Multiple inserts
        rows_inserted = qb.execute_insert("users", [
            {"name": "Bob Jones", "email": "bob@example.com", "age": 25},
            {"name": "Charlie Brown", "email": "charlie@example.com", "age": 35},
            {"name": "Diana Prince", "email": "diana@example.com", "age": 28}
        ])
        print(f"✓ Inserted {rows_inserted} more users")

        # 2. SELECT examples
        print("\n2. SELECT Operations:")
        print("-" * 60)

        # Select all
        query, params = qb.select("users")
        print(f"Query: {query}")
        print(f"Params: {params}")
        results = qb.execute_select("users")
        print(f"✓ All users ({len(results)} rows):")
        for row in results:
            print(f"  {row}")

        # Select with WHERE clause
        print("\nSelect with WHERE clause:")
        query, params = qb.select("users", where={"name": "Alice Smith"})
        print(f"Query: {query}")
        print(f"Params: {params}")
        results = qb.execute_select("users", where={"name": "Alice Smith"})
        print(f"✓ Results: {results}")

        # Select specific columns with ORDER BY and LIMIT
        print("\nSelect specific columns with ORDER BY and LIMIT:")
        query, params = qb.select(
            "users",
            columns=["name", "age"],
            order_by="age",
            limit=2
        )
        print(f"Query: {query}")
        print(f"Params: {params}")
        results = qb.execute_select(
            "users",
            columns=["name", "age"],
            order_by="age",
            limit=2
        )
        print(f"✓ Results: {results}")

        # 3. UPDATE examples
        print("\n3. UPDATE Operations:")
        print("-" * 60)

        query, params = qb.update(
            "users",
            values={"age": 31},
            where={"name": "Alice Smith"}
        )
        print(f"Query: {query}")
        print(f"Params: {params}")
        rows_updated = qb.execute_update(
            "users",
            values={"age": 31},
            where={"name": "Alice Smith"}
        )
        print(f"✓ Updated {rows_updated} row(s)")

        # Verify update
        results = qb.execute_select("users", where={"name": "Alice Smith"})
        print(f"✓ Updated user: {results}")

        # 4. DELETE examples
        print("\n4. DELETE Operations:")
        print("-" * 60)

        query, params = qb.delete("users", where={"name": "Bob Jones"})
        print(f"Query: {query}")
        print(f"Params: {params}")
        rows_deleted = qb.execute_delete("users", where={"name": "Bob Jones"})
        print(f"✓ Deleted {rows_deleted} row(s)")

        # Verify deletion
        results = qb.execute_select("users")
        print(f"✓ Remaining users ({len(results)} rows):")
        for row in results:
            print(f"  {row}")

        # 5. SQL Injection Prevention Demo
        print("\n5. SQL Injection Prevention:")
        print("-" * 60)

        try:
            # This will fail due to validation
            malicious_input = "users; DROP TABLE users; --"
            qb.select(malicious_input)
        except QueryValidationError as e:
            print(f"✓ Prevented SQL injection attempt: {e}")

        try:
            # This will also fail
            malicious_column = "name'; DROP TABLE users; --"
            qb.select("users", columns=[malicious_column])
        except QueryValidationError as e:
            print(f"✓ Prevented column name injection: {e}")

        # Parameterized values are safe
        print("\n✓ Safe parameterized query with special characters:")
        qb.execute_insert("users", {
            "name": "Robert'); DROP TABLE users; --",
            "email": "safe@example.com",
            "age": 40
        })
        results = qb.execute_select("users", where={
            "name": "Robert'); DROP TABLE users; --"
        })
        print(f"  Safely inserted and retrieved: {results[0]['name']}")

        # 6. Error Handling Demo
        print("\n6. Error Handling:")
        print("-" * 60)

        try:
            # Missing WHERE clause for UPDATE
            qb.update("users", {"age": 100}, where={})
        except QueryValidationError as e:
            print(f"✓ Prevented unsafe UPDATE: {e}")

        try:
            # Missing WHERE clause for DELETE
            qb.delete("users", where={})
        except QueryValidationError as e:
            print(f"✓ Prevented unsafe DELETE: {e}")

        try:
            # Invalid table name
            qb.select("nonexistent_table")
            qb.execute_select("nonexistent_table")
        except Exception as e:
            print(f"✓ Handled database error: {type(e).__name__}")

    print("\n" + "=" * 60)
    print("Demo completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    main()
