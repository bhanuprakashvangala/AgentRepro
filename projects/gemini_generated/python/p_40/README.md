# SQL Query Builder

This project contains a Python script for a SQL query builder with parameterization to prevent SQL injection.

## Requirements

- Python 3.x
- SQLAlchemy

## Installation

1.  Install the required Python packages:

    ```bash
    pip install -r requirements.txt
    ```

## Usage

1.  Import the `QueryBuilder` class from the `p_40_query_builder` module.
2.  Create an instance of the `QueryBuilder` class with a database connection string.
3.  Use the `select`, `insert`, `update`, and `delete` methods to build and execute queries.

### Example

```python
from p_40_query_builder import QueryBuilder

# Use an in-memory SQLite database for this example
db = QueryBuilder('sqlite:///:memory:')

# Create a table
db.connection.execute(text('CREATE TABLE users (id int, name varchar, age int)'))

# Insert data
db.insert('users', {'id': 1, 'name': 'Alice', 'age': 30})
db.insert('users', {'id': 2, 'name': 'Bob', 'age': 25})

# Select data
users = db.select('users', ['id', 'name', 'age'])
print(users)

# Update data
db.update('users', {'age': 26}, {'name': 'Bob'})

# Delete data
db.delete('users', {'name': 'Alice'})

# Close the connection
db.close()
```
