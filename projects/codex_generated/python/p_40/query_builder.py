#!/usr/bin/env python3
"""SQL query builder supporting parameterized CRUD operations with validation."""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple


class QueryBuilderError(ValueError):
    pass


@dataclass
class QueryResult:
    sql: str
    params: Tuple[Any, ...]


@dataclass
class QueryBuilder:
    table: str
    columns: List[str] = field(default_factory=list)

    def select(self, columns: Optional[Sequence[str]] = None) -> "SelectQuery":
        cols = list(columns) if columns else self.columns or ["*"]
        return SelectQuery(self.table, cols)

    def insert(self, values: Dict[str, Any]) -> QueryResult:
        if not values:
            raise QueryBuilderError("Insert values cannot be empty")
        columns = ", ".join(values.keys())
        placeholders = ", ".join(["?" for _ in values])
        sql = f"INSERT INTO {self.table} ({columns}) VALUES ({placeholders})"
        return QueryResult(sql, tuple(values.values()))

    def update(self, values: Dict[str, Any], where: Optional[Dict[str, Any]] = None) -> QueryResult:
        if not values:
            raise QueryBuilderError("Update values cannot be empty")
        set_clause = ", ".join([f"{col} = ?" for col in values])
        params: List[Any] = list(values.values())
        sql = f"UPDATE {self.table} SET {set_clause}"
        if where:
            where_clause, where_params = build_where_clause(where)
            sql += f" WHERE {where_clause}"
            params.extend(where_params)
        return QueryResult(sql, tuple(params))

    def delete(self, where: Optional[Dict[str, Any]] = None) -> QueryResult:
        sql = f"DELETE FROM {self.table}"
        params: List[Any] = []
        if where:
            where_clause, where_params = build_where_clause(where)
            sql += f" WHERE {where_clause}"
            params.extend(where_params)
        return QueryResult(sql, tuple(params))


@dataclass
class SelectQuery:
    table: str
    columns: Sequence[str]
    where_conditions: Optional[Dict[str, Any]] = None
    order_by_clause: Optional[str] = None
    limit_value: Optional[int] = None

    def where(self, conditions: Dict[str, Any]) -> "SelectQuery":
        self.where_conditions = conditions
        return self

    def order_by(self, clause: str) -> "SelectQuery":
        self.order_by_clause = clause
        return self

    def limit(self, value: int) -> "SelectQuery":
        if value <= 0:
            raise QueryBuilderError("Limit must be positive")
        self.limit_value = value
        return self

    def build(self) -> QueryResult:
        columns = ", ".join(self.columns) if self.columns else "*"
        sql = f"SELECT {columns} FROM {self.table}"
        params: List[Any] = []
        if self.where_conditions:
            where_clause, where_params = build_where_clause(self.where_conditions)
            sql += f" WHERE {where_clause}"
            params.extend(where_params)
        if self.order_by_clause:
            sql += f" ORDER BY {self.order_by_clause}"
        if self.limit_value is not None:
            sql += " LIMIT ?"
            params.append(self.limit_value)
        return QueryResult(sql, tuple(params))


def build_where_clause(conditions: Dict[str, Any]) -> Tuple[str, Tuple[Any, ...]]:
    if not conditions:
        raise QueryBuilderError("WHERE conditions cannot be empty")
    clauses = []
    params: List[Any] = []
    for column, value in conditions.items():
        if isinstance(value, tuple) and len(value) == 2:
            operator, operand = value
            if operator not in {"=", "!=", "<", "<=", ">", ">=", "LIKE"}:
                raise QueryBuilderError(f"Unsupported operator: {operator}")
            clauses.append(f"{column} {operator} ?")
            params.append(operand)
        elif isinstance(value, Iterable) and not isinstance(value, (str, bytes)):
            placeholders = ", ".join(["?" for _ in value])
            clauses.append(f"{column} IN ({placeholders})")
            params.extend(list(value))
        else:
            clauses.append(f"{column} = ?")
            params.append(value)
    return " AND ".join(clauses), tuple(params)


def execute_query(conn: sqlite3.Connection, query: QueryResult) -> sqlite3.Cursor:
    try:
        cursor = conn.execute(query.sql, query.params)
        conn.commit()
        return cursor
    except sqlite3.Error as exc:
        raise QueryBuilderError(f"Database execution failed: {exc}") from exc


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="SQL query builder demonstration")
    parser.add_argument("--database", default=":memory:", help="SQLite database path (default in-memory)")
    args = parser.parse_args()

    conn = sqlite3.connect(args.database)
    conn.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT, email TEXT)")

    builder = QueryBuilder("users", ["id", "name", "email"])
    insert_query = builder.insert({"name": "Alice", "email": "alice@example.com"})
    execute_query(conn, insert_query)

    select_query = builder.select(["id", "name"]).where({"name": "Alice"}).build()
    cursor = execute_query(conn, select_query)
    for row in cursor.fetchall():
        print(dict(row))

    update_query = builder.update({"email": "alice@newmail.com"}, {"name": "Alice"})
    execute_query(conn, update_query)

    delete_query = builder.delete({"name": "Alice"})
    execute_query(conn, delete_query)

    print("Demo completed.")
