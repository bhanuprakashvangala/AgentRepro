package com.example.migration;

import com.zaxxer.hikari.*;
import java.sql.*;
import java.time.LocalDateTime;
import java.util.*;
import java.util.stream.Collectors;

interface Migration {
    int getVersion();
    String getDescription();
    void up(Connection connection) throws SQLException;
    void down(Connection connection) throws SQLException;
}

class MigrationRecord {
    private int version;
    private String description;
    private LocalDateTime appliedAt;
    private int executionTimeMs;
    private String checksum;

    public MigrationRecord(int version, String description, LocalDateTime appliedAt,
                          int executionTimeMs, String checksum) {
        this.version = version;
        this.description = description;
        this.appliedAt = appliedAt;
        this.executionTimeMs = executionTimeMs;
        this.checksum = checksum;
    }

    public int getVersion() { return version; }
    public String getDescription() { return description; }
    public LocalDateTime getAppliedAt() { return appliedAt; }
    public int getExecutionTimeMs() { return executionTimeMs; }
    public String getChecksum() { return checksum; }

    @Override
    public String toString() {
        return String.format("v%d: %s (applied: %s, duration: %dms)",
            version, description, appliedAt, executionTimeMs);
    }
}

class MigrationManager {
    private final HikariDataSource dataSource;

    public MigrationManager(HikariDataSource dataSource) {
        this.dataSource = dataSource;
        initializeSchemaVersionTable();
    }

    private void initializeSchemaVersionTable() {
        String createTableSQL = """
            CREATE TABLE IF NOT EXISTS schema_version (
                version INT PRIMARY KEY,
                description VARCHAR(255) NOT NULL,
                applied_at TIMESTAMP NOT NULL,
                execution_time_ms INT NOT NULL,
                checksum VARCHAR(64),
                success BOOLEAN NOT NULL
            )
            """;

        try (Connection conn = dataSource.getConnection();
             Statement stmt = conn.createStatement()) {
            stmt.execute(createTableSQL);
            System.out.println("Schema version table initialized");
        } catch (SQLException e) {
            throw new RuntimeException("Failed to initialize schema version table", e);
        }
    }

    public List<MigrationRecord> getAppliedMigrations() {
        List<MigrationRecord> records = new ArrayList<>();
        String query = "SELECT version, description, applied_at, execution_time_ms, checksum " +
                      "FROM schema_version WHERE success = true ORDER BY version";

        try (Connection conn = dataSource.getConnection();
             Statement stmt = conn.createStatement();
             ResultSet rs = stmt.executeQuery(query)) {

            while (rs.next()) {
                records.add(new MigrationRecord(
                    rs.getInt("version"),
                    rs.getString("description"),
                    rs.getTimestamp("applied_at").toLocalDateTime(),
                    rs.getInt("execution_time_ms"),
                    rs.getString("checksum")
                ));
            }
        } catch (SQLException e) {
            throw new RuntimeException("Failed to get applied migrations", e);
        }

        return records;
    }

    public int getCurrentVersion() {
        String query = "SELECT MAX(version) as max_version FROM schema_version WHERE success = true";

        try (Connection conn = dataSource.getConnection();
             Statement stmt = conn.createStatement();
             ResultSet rs = stmt.executeQuery(query)) {

            if (rs.next()) {
                return rs.getInt("max_version");
            }
        } catch (SQLException e) {
            throw new RuntimeException("Failed to get current version", e);
        }

        return 0;
    }

    public void recordMigration(Migration migration, long executionTimeMs, boolean success) {
        String insertSQL = """
            INSERT INTO schema_version (version, description, applied_at, execution_time_ms, checksum, success)
            VALUES (?, ?, ?, ?, ?, ?)
            """;

        try (Connection conn = dataSource.getConnection();
             PreparedStatement pstmt = conn.prepareStatement(insertSQL)) {

            pstmt.setInt(1, migration.getVersion());
            pstmt.setString(2, migration.getDescription());
            pstmt.setTimestamp(3, Timestamp.valueOf(LocalDateTime.now()));
            pstmt.setLong(4, executionTimeMs);
            pstmt.setString(5, generateChecksum(migration));
            pstmt.setBoolean(6, success);
            pstmt.executeUpdate();

        } catch (SQLException e) {
            throw new RuntimeException("Failed to record migration", e);
        }
    }

    public void removeMigrationRecord(int version) {
        String deleteSQL = "DELETE FROM schema_version WHERE version = ?";

        try (Connection conn = dataSource.getConnection();
             PreparedStatement pstmt = conn.prepareStatement(deleteSQL)) {

            pstmt.setInt(1, version);
            pstmt.executeUpdate();

        } catch (SQLException e) {
            throw new RuntimeException("Failed to remove migration record", e);
        }
    }

    private String generateChecksum(Migration migration) {
        return String.valueOf(migration.getClass().getName().hashCode());
    }

    public Connection getConnection() throws SQLException {
        return dataSource.getConnection();
    }
}

class MigrationRunner {
    private final MigrationManager manager;
    private final List<Migration> migrations;

    public MigrationRunner(MigrationManager manager) {
        this.manager = manager;
        this.migrations = new ArrayList<>();
    }

    public void addMigration(Migration migration) {
        migrations.add(migration);
    }

    public void addMigrations(Migration... migrations) {
        this.migrations.addAll(Arrays.asList(migrations));
    }

    public void migrate() {
        // Sort migrations by version
        migrations.sort(Comparator.comparingInt(Migration::getVersion));

        int currentVersion = manager.getCurrentVersion();
        System.out.println("Current database version: " + currentVersion);

        List<Migration> pendingMigrations = migrations.stream()
            .filter(m -> m.getVersion() > currentVersion)
            .collect(Collectors.toList());

        if (pendingMigrations.isEmpty()) {
            System.out.println("Database is up to date. No migrations to apply.");
            return;
        }

        System.out.println("Found " + pendingMigrations.size() + " pending migration(s)\n");

        for (Migration migration : pendingMigrations) {
            executeMigration(migration);
        }

        System.out.println("\nMigration complete. New version: " + manager.getCurrentVersion());
    }

    public void rollback(int targetVersion) {
        int currentVersion = manager.getCurrentVersion();

        if (targetVersion >= currentVersion) {
            System.out.println("Target version must be less than current version");
            return;
        }

        List<Migration> migrationsToRollback = migrations.stream()
            .filter(m -> m.getVersion() > targetVersion && m.getVersion() <= currentVersion)
            .sorted(Comparator.comparingInt(Migration::getVersion).reversed())
            .collect(Collectors.toList());

        System.out.println("Rolling back " + migrationsToRollback.size() + " migration(s)\n");

        for (Migration migration : migrationsToRollback) {
            executeRollback(migration);
        }

        System.out.println("\nRollback complete. Current version: " + manager.getCurrentVersion());
    }

    private void executeMigration(Migration migration) {
        System.out.println("Applying migration v" + migration.getVersion() + ": " +
                         migration.getDescription());

        long startTime = System.currentTimeMillis();
        boolean success = false;

        try (Connection conn = manager.getConnection()) {
            conn.setAutoCommit(false);

            try {
                migration.up(conn);
                conn.commit();
                success = true;

                long executionTime = System.currentTimeMillis() - startTime;
                manager.recordMigration(migration, executionTime, true);

                System.out.println("  ✓ Migration successful (" + executionTime + "ms)\n");

            } catch (SQLException e) {
                conn.rollback();
                System.err.println("  ✗ Migration failed: " + e.getMessage());
                manager.recordMigration(migration, System.currentTimeMillis() - startTime, false);
                throw new RuntimeException("Migration failed", e);
            }

        } catch (SQLException e) {
            throw new RuntimeException("Database connection failed", e);
        }
    }

    private void executeRollback(Migration migration) {
        System.out.println("Rolling back v" + migration.getVersion() + ": " +
                         migration.getDescription());

        try (Connection conn = manager.getConnection()) {
            conn.setAutoCommit(false);

            try {
                migration.down(conn);
                conn.commit();
                manager.removeMigrationRecord(migration.getVersion());

                System.out.println("  ✓ Rollback successful\n");

            } catch (SQLException e) {
                conn.rollback();
                System.err.println("  ✗ Rollback failed: " + e.getMessage());
                throw new RuntimeException("Rollback failed", e);
            }

        } catch (SQLException e) {
            throw new RuntimeException("Database connection failed", e);
        }
    }

    public void showStatus() {
        int currentVersion = manager.getCurrentVersion();
        List<MigrationRecord> applied = manager.getAppliedMigrations();

        System.out.println("=== Migration Status ===");
        System.out.println("Current version: " + currentVersion);
        System.out.println("Applied migrations: " + applied.size());
        System.out.println();

        if (!applied.isEmpty()) {
            System.out.println("Migration History:");
            for (MigrationRecord record : applied) {
                System.out.println("  " + record);
            }
        }

        long pendingCount = migrations.stream()
            .filter(m -> m.getVersion() > currentVersion)
            .count();

        if (pendingCount > 0) {
            System.out.println("\nPending migrations: " + pendingCount);
        }
    }
}

// Sample Migrations
class CreateUsersTableMigration implements Migration {
    @Override
    public int getVersion() { return 1; }

    @Override
    public String getDescription() { return "Create users table"; }

    @Override
    public void up(Connection conn) throws SQLException {
        String sql = """
            CREATE TABLE users (
                id BIGINT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """;

        try (Statement stmt = conn.createStatement()) {
            stmt.execute(sql);
        }
    }

    @Override
    public void down(Connection conn) throws SQLException {
        try (Statement stmt = conn.createStatement()) {
            stmt.execute("DROP TABLE IF EXISTS users");
        }
    }
}

class AddPasswordColumnMigration implements Migration {
    @Override
    public int getVersion() { return 2; }

    @Override
    public String getDescription() { return "Add password column to users"; }

    @Override
    public void up(Connection conn) throws SQLException {
        String sql = "ALTER TABLE users ADD COLUMN password_hash VARCHAR(255) NOT NULL DEFAULT ''";

        try (Statement stmt = conn.createStatement()) {
            stmt.execute(sql);
        }
    }

    @Override
    public void down(Connection conn) throws SQLException {
        try (Statement stmt = conn.createStatement()) {
            stmt.execute("ALTER TABLE users DROP COLUMN password_hash");
        }
    }
}

class CreatePostsTableMigration implements Migration {
    @Override
    public int getVersion() { return 3; }

    @Override
    public String getDescription() { return "Create posts table"; }

    @Override
    public void up(Connection conn) throws SQLException {
        String sql = """
            CREATE TABLE posts (
                id BIGINT AUTO_INCREMENT PRIMARY KEY,
                user_id BIGINT NOT NULL,
                title VARCHAR(200) NOT NULL,
                content TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
            """;

        try (Statement stmt = conn.createStatement()) {
            stmt.execute(sql);
        }
    }

    @Override
    public void down(Connection conn) throws SQLException {
        try (Statement stmt = conn.createStatement()) {
            stmt.execute("DROP TABLE IF EXISTS posts");
        }
    }
}

class AddIndexToPostsMigration implements Migration {
    @Override
    public int getVersion() { return 4; }

    @Override
    public String getDescription() { return "Add index on posts user_id"; }

    @Override
    public void up(Connection conn) throws SQLException {
        try (Statement stmt = conn.createStatement()) {
            stmt.execute("CREATE INDEX idx_posts_user_id ON posts(user_id)");
        }
    }

    @Override
    public void down(Connection conn) throws SQLException {
        try (Statement stmt = conn.createStatement()) {
            stmt.execute("DROP INDEX IF EXISTS idx_posts_user_id");
        }
    }
}

public class DatabaseMigrationTool {

    public static void main(String[] args) {
        System.out.println("=== Database Migration Tool ===\n");

        // Setup database connection
        HikariConfig config = new HikariConfig();
        config.setJdbcUrl("jdbc:h2:mem:migrationdb;DB_CLOSE_DELAY=-1");
        config.setUsername("sa");
        config.setPassword("");
        config.setMaximumPoolSize(5);

        HikariDataSource dataSource = new HikariDataSource(config);

        // Initialize migration manager
        MigrationManager manager = new MigrationManager(dataSource);
        MigrationRunner runner = new MigrationRunner(manager);

        // Add migrations
        runner.addMigrations(
            new CreateUsersTableMigration(),
            new AddPasswordColumnMigration(),
            new CreatePostsTableMigration(),
            new AddIndexToPostsMigration()
        );

        // Show initial status
        System.out.println("Initial State:");
        runner.showStatus();
        System.out.println();

        // Run migrations
        System.out.println("--- Running Migrations ---");
        runner.migrate();
        System.out.println();

        // Show status after migration
        runner.showStatus();
        System.out.println();

        // Demonstrate rollback
        System.out.println("\n--- Demonstrating Rollback ---");
        System.out.println("Rolling back to version 2...");
        runner.rollback(2);
        System.out.println();

        runner.showStatus();
        System.out.println();

        // Re-apply migrations
        System.out.println("\n--- Re-applying Migrations ---");
        runner.migrate();
        System.out.println();

        runner.showStatus();

        // Cleanup
        dataSource.close();
        System.out.println("\n=== Migration Demo Complete ===");
    }
}
