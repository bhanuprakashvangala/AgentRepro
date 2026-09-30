
import sqlalchemy
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

class QueryBuilder:
    def __init__(self, connection_string):
        try:
            self.engine = create_engine(connection_string)
            self.connection = self.engine.connect()
            print("Database connection successful.")
        except SQLAlchemyError as e:
            print(f"Error connecting to the database: {e}")
            raise

    def _validate_table_name(self, table_name):
        if not table_name.isalnum() or not table_name:
            raise ValueError("Invalid table name. Table names must be alphanumeric.")

    def _validate_columns(self, columns):
        if not isinstance(columns, (list, tuple)) or not all(isinstance(c, str) and c.isalnum() for c in columns):
            raise ValueError("Invalid column names. Columns must be a list of alphanumeric strings.")

    def _validate_where_clause(self, where_clause):
        if where_clause and not isinstance(where_clause, dict):
            raise ValueError("WHERE clause must be a dictionary of column-value pairs.")

    def select(self, table_name, columns, where_clause=None):
        self._validate_table_name(table_name)
        self._validate_columns(columns)
        self._validate_where_clause(where_clause)

        column_str = ", ".join(columns)
        query_str = f"SELECT {column_str} FROM {table_name}"
        params = {}

        if where_clause:
            where_conditions = []
            for col, val in where_clause.items():
                where_conditions.append(f"{col} = :{col}")
                params[col] = val
            query_str += " WHERE " + " AND ".join(where_conditions)

        try:
            statement = text(query_str)
            result = self.connection.execute(statement, params)
            return result.fetchall()
        except SQLAlchemyError as e:
            print(f"Error executing SELECT query: {e}")
            return None

    def insert(self, table_name, data):
        self._validate_table_name(table_name)
        if not isinstance(data, dict) or not data:
            raise ValueError("Data for INSERT must be a non-empty dictionary.")

        columns = ", ".join(data.keys())
        placeholders = ", ".join([f":{key}" for key in data.keys()])
        query_str = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"

        try:
            statement = text(query_str)
            self.connection.execute(statement, data)
            self.connection.commit()
            print("INSERT query executed successfully.")
            return True
        except SQLAlchemyError as e:
            self.connection.rollback()
            print(f"Error executing INSERT query: {e}")
            return False

    def update(self, table_name, data, where_clause):
        self._validate_table_name(table_name)
        if not isinstance(data, dict) or not data:
            raise ValueError("Data for UPDATE must be a non-empty dictionary.")
        self._validate_where_clause(where_clause)
        if not where_clause:
            raise ValueError("UPDATE query requires a WHERE clause.")

        set_statements = []
        params = {}
        for col, val in data.items():
            set_statements.append(f"{col} = :{col}")
            params[col] = val

        where_conditions = []
        for col, val in where_clause.items():
            where_conditions.append(f"{col} = :w_{col}")
            params[f"w_{col}"] = val

        query_str = f"UPDATE {table_name} SET {', '.join(set_statements)} WHERE {' AND '.join(where_conditions)}"

        try:
            statement = text(query_str)
            self.connection.execute(statement, params)
            self.connection.commit()
            print("UPDATE query executed successfully.")
            return True
        except SQLAlchemyError as e:
            self.connection.rollback()
            print(f"Error executing UPDATE query: {e}")
            return False

    def delete(self, table_name, where_clause):
        self._validate_table_name(table_name)
        self._validate_where_clause(where_clause)
        if not where_clause:
            raise ValueError("DELETE query requires a WHERE clause.")

        where_conditions = []
        params = {}
        for col, val in where_clause.items():
            where_conditions.append(f"{col} = :{col}")
            params[col] = val

        query_str = f"DELETE FROM {table_name} WHERE {' AND '.join(where_conditions)}"

        try:
            statement = text(query_str)
            self.connection.execute(statement, params)
            self.connection.commit()
            print("DELETE query executed successfully.")
            return True
        except SQLAlchemyError as e:
            self.connection.rollback()
            print(f"Error executing DELETE query: {e}")
            return False

    def close(self):
        self.connection.close()
        print("Database connection closed.")

