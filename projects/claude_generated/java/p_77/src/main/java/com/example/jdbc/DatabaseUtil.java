package com.example.jdbc;

import com.zaxxer.hikari.HikariConfig;
import com.zaxxer.hikari.HikariDataSource;

import java.sql.*;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class DatabaseUtil {
    private final HikariDataSource dataSource;

    public DatabaseUtil(String jdbcUrl, String username, String password) {
        HikariConfig config = new HikariConfig();
        config.setJdbcUrl(jdbcUrl);
        config.setUsername(username);
        config.setPassword(password);
        config.setMaximumPoolSize(10);
        config.setConnectionTimeout(30000);
        config.setIdleTimeout(600000);
        config.setMaxLifetime(1800000);

        this.dataSource = new HikariDataSource(config);
        System.out.println("Database connection pool initialized");
    }

    /**
     * Execute SELECT query and return results as list of maps
     */
    public List<Map<String, Object>> executeQuery(String sql, Object... params) throws SQLException {
        List<Map<String, Object>> results = new ArrayList<>();

        try (Connection conn = dataSource.getConnection();
             PreparedStatement stmt = conn.prepareStatement(sql)) {

            setParameters(stmt, params);

            try (ResultSet rs = stmt.executeQuery()) {
                ResultSetMetaData metaData = rs.getMetaData();
                int columnCount = metaData.getColumnCount();

                while (rs.next()) {
                    Map<String, Object> row = new HashMap<>();
                    for (int i = 1; i <= columnCount; i++) {
                        row.put(metaData.getColumnName(i), rs.getObject(i));
                    }
                    results.add(row);
                }
            }
        }

        return results;
    }

    /**
     * Execute INSERT, UPDATE, or DELETE and return affected rows
     */
    public int executeUpdate(String sql, Object... params) throws SQLException {
        try (Connection conn = dataSource.getConnection();
             PreparedStatement stmt = conn.prepareStatement(sql)) {

            setParameters(stmt, params);
            return stmt.executeUpdate();
        }
    }

    /**
     * Execute batch updates
     */
    public int[] executeBatch(String sql, List<Object[]> paramsList) throws SQLException {
        try (Connection conn = dataSource.getConnection();
             PreparedStatement stmt = conn.prepareStatement(sql)) {

            for (Object[] params : paramsList) {
                setParameters(stmt, params);
                stmt.addBatch();
            }

            return stmt.executeBatch();
        }
    }

    /**
     * Execute transaction with multiple statements
     */
    public void executeTransaction(TransactionCallback callback) throws SQLException {
        Connection conn = null;
        try {
            conn = dataSource.getConnection();
            conn.setAutoCommit(false);

            callback.execute(conn);

            conn.commit();
        } catch (SQLException e) {
            if (conn != null) {
                try {
                    conn.rollback();
                    System.out.println("Transaction rolled back");
                } catch (SQLException rollbackEx) {
                    throw new SQLException("Rollback failed", rollbackEx);
                }
            }
            throw e;
        } finally {
            if (conn != null) {
                try {
                    conn.setAutoCommit(true);
                    conn.close();
                } catch (SQLException closeEx) {
                    // Log error
                }
            }
        }
    }

    /**
     * Set prepared statement parameters
     */
    private void setParameters(PreparedStatement stmt, Object[] params) throws SQLException {
        for (int i = 0; i < params.length; i++) {
            stmt.setObject(i + 1, params[i]);
        }
    }

    /**
     * Close datasource
     */
    public void close() {
        if (dataSource != null && !dataSource.isClosed()) {
            dataSource.close();
            System.out.println("Database connection pool closed");
        }
    }

    @FunctionalInterface
    public interface TransactionCallback {
        void execute(Connection conn) throws SQLException;
    }

    // Example usage
    public static void main(String[] args) {
        String jdbcUrl = "jdbc:h2:mem:testdb";
        DatabaseUtil db = new DatabaseUtil(jdbcUrl, "sa", "");

        try {
            // Create table
            db.executeUpdate("CREATE TABLE users (id INT PRIMARY KEY, name VARCHAR(255), email VARCHAR(255))");

            // Insert data
            db.executeUpdate("INSERT INTO users VALUES (?, ?, ?)", 1, "Alice", "alice@example.com");
            db.executeUpdate("INSERT INTO users VALUES (?, ?, ?)", 2, "Bob", "bob@example.com");

            // Query data
            List<Map<String, Object>> users = db.executeQuery("SELECT * FROM users WHERE id > ?", 0);
            users.forEach(System.out::println);

            // Batch insert
            List<Object[]> batchParams = List.of(
                    new Object[]{3, "Charlie", "charlie@example.com"},
                    new Object[]{4, "Diana", "diana@example.com"}
            );
            db.executeBatch("INSERT INTO users VALUES (?, ?, ?)", batchParams);

            // Transaction example
            db.executeTransaction(conn -> {
                try (PreparedStatement stmt = conn.prepareStatement("UPDATE users SET name = ? WHERE id = ?")) {
                    stmt.setString(1, "Alice Updated");
                    stmt.setInt(2, 1);
                    stmt.executeUpdate();
                }
            });

            System.out.println("All operations completed successfully!");

        } catch (SQLException e) {
            e.printStackTrace();
        } finally {
            db.close();
        }
    }
}
