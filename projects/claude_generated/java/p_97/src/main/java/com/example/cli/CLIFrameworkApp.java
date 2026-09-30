package com.example.cli;

import picocli.CommandLine;
import picocli.CommandLine.*;
import java.io.*;
import java.util.*;
import java.util.concurrent.*;

// Main CLI Application
@Command(
    name = "myapp",
    mixinStandardHelpOptions = true,
    version = "1.0.0",
    description = "A comprehensive CLI application demonstrating various features",
    subcommands = {
        UserCommand.class,
        ConfigCommand.class,
        DataCommand.class
    }
)
class CLIApp implements Callable<Integer> {

    @Option(names = {"-v", "--verbose"}, description = "Enable verbose output")
    private boolean verbose;

    @Override
    public Integer call() {
        System.out.println("Welcome to MyApp CLI!");
        System.out.println("Use --help to see available commands");
        return 0;
    }

    public static void main(String[] args) {
        int exitCode = new CommandLine(new CLIApp()).execute(args);
        System.exit(exitCode);
    }
}

// User management commands
@Command(
    name = "user",
    description = "User management commands",
    subcommands = {
        UserListCommand.class,
        UserCreateCommand.class,
        UserDeleteCommand.class
    }
)
class UserCommand implements Callable<Integer> {
    @Override
    public Integer call() {
        System.out.println("User management. Use 'user --help' for available subcommands.");
        return 0;
    }
}

@Command(name = "list", description = "List all users")
class UserListCommand implements Callable<Integer> {

    @Option(names = {"-l", "--limit"}, description = "Limit number of results", defaultValue = "10")
    private int limit;

    @Option(names = {"-s", "--sort"}, description = "Sort by field", defaultValue = "name")
    private String sortBy;

    @Override
    public Integer call() {
        System.out.println("Listing users (limit: " + limit + ", sort by: " + sortBy + ")");

        // Simulate user list
        String[] users = {"Alice", "Bob", "Charlie", "Diana", "Eve"};
        for (int i = 0; i < Math.min(users.length, limit); i++) {
            System.out.println("  " + (i + 1) + ". " + users[i]);
        }

        return 0;
    }
}

@Command(name = "create", description = "Create a new user")
class UserCreateCommand implements Callable<Integer> {

    @Parameters(index = "0", description = "Username")
    private String username;

    @Option(names = {"-e", "--email"}, description = "User email", required = true)
    private String email;

    @Option(names = {"-r", "--role"}, description = "User role", defaultValue = "user")
    private String role;

    @Option(names = {"--admin"}, description = "Create as admin user")
    private boolean admin;

    @Override
    public Integer call() {
        if (admin) {
            role = "admin";
        }

        System.out.println("Creating user:");
        System.out.println("  Username: " + username);
        System.out.println("  Email: " + email);
        System.out.println("  Role: " + role);

        // Simulate user creation with progress
        System.out.print("Creating user");
        for (int i = 0; i < 3; i++) {
            System.out.print(".");
            try {
                Thread.sleep(300);
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
        }
        System.out.println(" Done!");

        return 0;
    }
}

@Command(name = "delete", description = "Delete a user")
class UserDeleteCommand implements Callable<Integer> {

    @Parameters(index = "0", description = "Username to delete")
    private String username;

    @Option(names = {"-f", "--force"}, description = "Force deletion without confirmation")
    private boolean force;

    @Override
    public Integer call() {
        if (!force) {
            System.out.print("Are you sure you want to delete user '" + username + "'? (y/N): ");
            Scanner scanner = new Scanner(System.in);
            String response = scanner.nextLine().trim().toLowerCase();

            if (!response.equals("y")) {
                System.out.println("Deletion cancelled");
                return 1;
            }
        }

        System.out.println("Deleting user: " + username);
        return 0;
    }
}

// Configuration commands
@Command(
    name = "config",
    description = "Configuration management",
    subcommands = {
        ConfigGetCommand.class,
        ConfigSetCommand.class,
        ConfigListCommand.class
    }
)
class ConfigCommand implements Callable<Integer> {
    @Override
    public Integer call() {
        System.out.println("Configuration management. Use 'config --help' for available subcommands.");
        return 0;
    }
}

@Command(name = "get", description = "Get configuration value")
class ConfigGetCommand implements Callable<Integer> {

    @Parameters(index = "0", description = "Configuration key")
    private String key;

    private static final Map<String, String> config = Map.of(
        "app.name", "MyApp",
        "app.version", "1.0.0",
        "server.port", "8080",
        "database.host", "localhost"
    );

    @Override
    public Integer call() {
        String value = config.get(key);

        if (value != null) {
            System.out.println(key + " = " + value);
            return 0;
        } else {
            System.err.println("Key not found: " + key);
            return 1;
        }
    }
}

@Command(name = "set", description = "Set configuration value")
class ConfigSetCommand implements Callable<Integer> {

    @Parameters(index = "0", description = "Configuration key")
    private String key;

    @Parameters(index = "1", description = "Configuration value")
    private String value;

    @Override
    public Integer call() {
        System.out.println("Setting " + key + " = " + value);
        return 0;
    }
}

@Command(name = "list", description = "List all configuration")
class ConfigListCommand implements Callable<Integer> {

    @Option(names = {"-f", "--filter"}, description = "Filter keys by prefix")
    private String filter;

    @Override
    public Integer call() {
        Map<String, String> config = Map.of(
            "app.name", "MyApp",
            "app.version", "1.0.0",
            "app.debug", "false",
            "server.port", "8080",
            "server.host", "localhost",
            "database.host", "localhost",
            "database.port", "5432"
        );

        System.out.println("Configuration:");
        config.entrySet().stream()
            .filter(entry -> filter == null || entry.getKey().startsWith(filter))
            .sorted(Map.Entry.comparingByKey())
            .forEach(entry -> System.out.println("  " + entry.getKey() + " = " + entry.getValue()));

        return 0;
    }
}

// Data processing commands
@Command(
    name = "data",
    description = "Data processing commands",
    subcommands = {
        DataImportCommand.class,
        DataExportCommand.class,
        DataTransformCommand.class
    }
)
class DataCommand implements Callable<Integer> {
    @Override
    public Integer call() {
        System.out.println("Data processing. Use 'data --help' for available subcommands.");
        return 0;
    }
}

@Command(name = "import", description = "Import data from file")
class DataImportCommand implements Callable<Integer> {

    @Parameters(index = "0", description = "Input file path")
    private String inputFile;

    @Option(names = {"-f", "--format"}, description = "File format (csv, json, xml)",
            defaultValue = "csv")
    private String format;

    @Option(names = {"--skip-header"}, description = "Skip header row")
    private boolean skipHeader;

    @Override
    public Integer call() {
        System.out.println("Importing data:");
        System.out.println("  File: " + inputFile);
        System.out.println("  Format: " + format);
        System.out.println("  Skip header: " + skipHeader);

        // Simulate import with progress bar
        System.out.println("\nProcessing...");
        int total = 100;
        for (int i = 0; i <= total; i += 10) {
            printProgressBar(i, total);
            try {
                Thread.sleep(200);
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
        }
        System.out.println("\n\nImport complete!");

        return 0;
    }

    private void printProgressBar(int current, int total) {
        int percentage = (int) ((current / (double) total) * 100);
        int progressLength = 40;
        int filled = (int) ((current / (double) total) * progressLength);

        StringBuilder bar = new StringBuilder("[");
        for (int i = 0; i < progressLength; i++) {
            bar.append(i < filled ? "=" : " ");
        }
        bar.append("] ").append(percentage).append("%");

        System.out.print("\r" + bar);
    }
}

@Command(name = "export", description = "Export data to file")
class DataExportCommand implements Callable<Integer> {

    @Parameters(index = "0", description = "Output file path")
    private String outputFile;

    @Option(names = {"-f", "--format"}, description = "Output format", defaultValue = "csv")
    private String format;

    @Option(names = {"--compress"}, description = "Compress output file")
    private boolean compress;

    @Override
    public Integer call() {
        System.out.println("Exporting data:");
        System.out.println("  File: " + outputFile);
        System.out.println("  Format: " + format);
        System.out.println("  Compress: " + compress);

        System.out.println("\nExporting 1000 records...");
        try {
            Thread.sleep(1000);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
        System.out.println("Export complete!");

        return 0;
    }
}

@Command(name = "transform", description = "Transform data with operations")
class DataTransformCommand implements Callable<Integer> {

    @Parameters(index = "0", description = "Input file")
    private String inputFile;

    @Parameters(index = "1", description = "Output file")
    private String outputFile;

    @Option(names = {"-o", "--operations"},
            description = "Operations to apply (filter, map, sort)",
            split = ",")
    private List<String> operations;

    @Override
    public Integer call() {
        System.out.println("Transforming data:");
        System.out.println("  Input: " + inputFile);
        System.out.println("  Output: " + outputFile);
        System.out.println("  Operations: " + operations);

        if (operations != null) {
            for (String op : operations) {
                System.out.println("  Applying: " + op);
            }
        }

        return 0;
    }
}

// Utility class for CLI helpers
class CLIHelper {
    public static void printBanner(String appName, String version) {
        System.out.println("╔═══════════════════════════════════╗");
        System.out.println("║   " + appName + " v" + version + "   ║");
        System.out.println("╚═══════════════════════════════════╝");
        System.out.println();
    }

    public static boolean confirm(String message) {
        System.out.print(message + " (y/N): ");
        Scanner scanner = new Scanner(System.in);
        String response = scanner.nextLine().trim().toLowerCase();
        return response.equals("y") || response.equals("yes");
    }

    public static String prompt(String message) {
        System.out.print(message + ": ");
        Scanner scanner = new Scanner(System.in);
        return scanner.nextLine().trim();
    }

    public static void printTable(String[] headers, List<String[]> rows) {
        // Calculate column widths
        int[] widths = new int[headers.length];
        for (int i = 0; i < headers.length; i++) {
            widths[i] = headers[i].length();
        }

        for (String[] row : rows) {
            for (int i = 0; i < row.length; i++) {
                widths[i] = Math.max(widths[i], row[i].length());
            }
        }

        // Print header
        printRow(headers, widths);
        printSeparator(widths);

        // Print rows
        for (String[] row : rows) {
            printRow(row, widths);
        }
    }

    private static void printRow(String[] cells, int[] widths) {
        for (int i = 0; i < cells.length; i++) {
            System.out.print(String.format("%-" + widths[i] + "s", cells[i]));
            if (i < cells.length - 1) {
                System.out.print(" | ");
            }
        }
        System.out.println();
    }

    private static void printSeparator(int[] widths) {
        for (int i = 0; i < widths.length; i++) {
            System.out.print("-".repeat(widths[i]));
            if (i < widths.length - 1) {
                System.out.print("-+-");
            }
        }
        System.out.println();
    }
}

public class CLIFrameworkApp {

    public static void main(String[] args) {
        System.out.println("=== CLI Framework Demo ===\n");

        CLIHelper.printBanner("MyApp", "1.0.0");

        System.out.println("Example commands:\n");

        String[] examples = {
            "java CLIApp user list --limit 5",
            "java CLIApp user create john --email john@example.com --admin",
            "java CLIApp user delete john --force",
            "",
            "java CLIApp config get app.name",
            "java CLIApp config set app.debug true",
            "java CLIApp config list --filter app",
            "",
            "java CLIApp data import data.csv --format csv --skip-header",
            "java CLIApp data export output.json --format json --compress",
            "java CLIApp data transform input.csv output.csv --operations filter,sort",
            "",
            "java CLIApp --help",
            "java CLIApp user --help"
        };

        for (String example : examples) {
            if (example.isEmpty()) {
                System.out.println();
            } else {
                System.out.println("  $ " + example);
            }
        }

        // Demonstrate table printing
        System.out.println("\n--- Example Table Output ---");
        String[] headers = {"ID", "Name", "Email", "Role"};
        List<String[]> rows = List.of(
            new String[]{"1", "Alice", "alice@example.com", "admin"},
            new String[]{"2", "Bob", "bob@example.com", "user"},
            new String[]{"3", "Charlie", "charlie@example.com", "user"}
        );
        CLIHelper.printTable(headers, rows);

        // Demonstrate the actual CLI
        System.out.println("\n--- Running Actual Commands ---\n");

        // Run some example commands
        runCommand("user list --limit 3");
        System.out.println();

        runCommand("config list --filter app");
        System.out.println();

        runCommand("data import sample.csv --format csv");

        System.out.println("\n=== CLI Framework Demo Complete ===");
        System.out.println("\nKey Features:");
        System.out.println("  ✓ Command hierarchy with subcommands");
        System.out.println("  ✓ Argument parsing (options, flags, parameters)");
        System.out.println("  ✓ Auto-generated help text");
        System.out.println("  ✓ Input validation");
        System.out.println("  ✓ Interactive prompts");
        System.out.println("  ✓ Progress indicators");
        System.out.println("  ✓ Table formatting");
        System.out.println("  ✓ Exit codes for error handling");
    }

    private static void runCommand(String commandLine) {
        System.out.println("$ myapp " + commandLine);
        String[] args = commandLine.split("\\s+");
        new CommandLine(new CLIApp()).execute(args);
    }
}
