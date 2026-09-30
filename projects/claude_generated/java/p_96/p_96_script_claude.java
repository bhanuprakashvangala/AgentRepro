package com.example.config;

import com.google.gson.*;
import com.typesafe.config.*;
import java.io.*;
import java.nio.file.*;
import java.util.*;
import java.util.concurrent.*;
import java.util.function.Consumer;

interface ConfigurationSource {
    Map<String, Object> load();
    String getName();
}

class PropertiesConfigSource implements ConfigurationSource {
    private final String filePath;

    public PropertiesConfigSource(String filePath) {
        this.filePath = filePath;
    }

    @Override
    public Map<String, Object> load() {
        Map<String, Object> config = new HashMap<>();
        Properties props = new Properties();

        try (InputStream input = new FileInputStream(filePath)) {
            props.load(input);
            props.forEach((key, value) -> config.put(key.toString(), value));
        } catch (IOException e) {
            System.err.println("Failed to load properties from: " + filePath);
        }

        return config;
    }

    @Override
    public String getName() {
        return "Properties: " + filePath;
    }
}

class JsonConfigSource implements ConfigurationSource {
    private final String filePath;

    public JsonConfigSource(String filePath) {
        this.filePath = filePath;
    }

    @Override
    public Map<String, Object> load() {
        Map<String, Object> config = new HashMap<>();

        try {
            String content = Files.readString(Paths.get(filePath));
            JsonObject json = JsonParser.parseString(content).getAsJsonObject();
            config = flattenJson(json, "");
        } catch (IOException e) {
            System.err.println("Failed to load JSON from: " + filePath);
        }

        return config;
    }

    private Map<String, Object> flattenJson(JsonObject json, String prefix) {
        Map<String, Object> flat = new HashMap<>();

        json.entrySet().forEach(entry -> {
            String key = prefix.isEmpty() ? entry.getKey() : prefix + "." + entry.getKey();
            JsonElement value = entry.getValue();

            if (value.isJsonObject()) {
                flat.putAll(flattenJson(value.getAsJsonObject(), key));
            } else if (value.isJsonPrimitive()) {
                JsonPrimitive primitive = value.getAsJsonPrimitive();
                if (primitive.isString()) {
                    flat.put(key, primitive.getAsString());
                } else if (primitive.isNumber()) {
                    flat.put(key, primitive.getAsNumber());
                } else if (primitive.isBoolean()) {
                    flat.put(key, primitive.getAsBoolean());
                }
            }
        });

        return flat;
    }

    @Override
    public String getName() {
        return "JSON: " + filePath;
    }
}

class EnvironmentConfigSource implements ConfigurationSource {
    private final String prefix;

    public EnvironmentConfigSource(String prefix) {
        this.prefix = prefix;
    }

    @Override
    public Map<String, Object> load() {
        Map<String, Object> config = new HashMap<>();

        System.getenv().forEach((key, value) -> {
            if (prefix == null || key.startsWith(prefix)) {
                String configKey = prefix != null ? key.substring(prefix.length()) : key;
                configKey = configKey.toLowerCase().replace("_", ".");
                config.put(configKey, value);
            }
        });

        return config;
    }

    @Override
    public String getName() {
        return "Environment Variables" + (prefix != null ? " (prefix: " + prefix + ")" : "");
    }
}

interface ConfigChangeListener {
    void onConfigChange(String key, Object oldValue, Object newValue);
}

class ConfigManager {
    private final List<ConfigurationSource> sources = new ArrayList<>();
    private final Map<String, Object> config = new ConcurrentHashMap<>();
    private final List<ConfigChangeListener> listeners = new CopyOnWriteArrayList<>();
    private final ScheduledExecutorService reloadExecutor;
    private final Map<String, Object> defaults = new HashMap<>();

    public ConfigManager() {
        this.reloadExecutor = Executors.newSingleThreadScheduledExecutor();
    }

    public void addSource(ConfigurationSource source) {
        sources.add(source);
        System.out.println("Added config source: " + source.getName());
    }

    public void setDefault(String key, Object value) {
        defaults.put(key, value);
    }

    public void load() {
        Map<String, Object> newConfig = new HashMap<>(defaults);

        // Load from sources in order (later sources override earlier ones)
        for (ConfigurationSource source : sources) {
            Map<String, Object> sourceConfig = source.load();
            newConfig.putAll(sourceConfig);
        }

        // Detect changes and notify listeners
        newConfig.forEach((key, newValue) -> {
            Object oldValue = config.get(key);
            if (!Objects.equals(oldValue, newValue)) {
                notifyListeners(key, oldValue, newValue);
            }
        });

        config.clear();
        config.putAll(newConfig);

        System.out.println("Configuration loaded: " + config.size() + " keys");
    }

    public void reload() {
        System.out.println("Reloading configuration...");
        load();
    }

    public void startAutoReload(long intervalSeconds) {
        reloadExecutor.scheduleAtFixedRate(
            this::reload,
            intervalSeconds,
            intervalSeconds,
            TimeUnit.SECONDS
        );
        System.out.println("Auto-reload enabled (interval: " + intervalSeconds + "s)");
    }

    public void stopAutoReload() {
        reloadExecutor.shutdown();
    }

    public String getString(String key) {
        return getString(key, null);
    }

    public String getString(String key, String defaultValue) {
        Object value = config.get(key);
        return value != null ? value.toString() : defaultValue;
    }

    public int getInt(String key) {
        return getInt(key, 0);
    }

    public int getInt(String key, int defaultValue) {
        Object value = config.get(key);
        if (value instanceof Number) {
            return ((Number) value).intValue();
        }
        if (value instanceof String) {
            try {
                return Integer.parseInt((String) value);
            } catch (NumberFormatException e) {
                return defaultValue;
            }
        }
        return defaultValue;
    }

    public double getDouble(String key, double defaultValue) {
        Object value = config.get(key);
        if (value instanceof Number) {
            return ((Number) value).doubleValue();
        }
        if (value instanceof String) {
            try {
                return Double.parseDouble((String) value);
            } catch (NumberFormatException e) {
                return defaultValue;
            }
        }
        return defaultValue;
    }

    public boolean getBoolean(String key) {
        return getBoolean(key, false);
    }

    public boolean getBoolean(String key, boolean defaultValue) {
        Object value = config.get(key);
        if (value instanceof Boolean) {
            return (Boolean) value;
        }
        if (value instanceof String) {
            return Boolean.parseBoolean((String) value);
        }
        return defaultValue;
    }

    public Map<String, Object> getSection(String prefix) {
        Map<String, Object> section = new HashMap<>();
        String searchPrefix = prefix + ".";

        config.forEach((key, value) -> {
            if (key.startsWith(searchPrefix)) {
                String subKey = key.substring(searchPrefix.length());
                section.put(subKey, value);
            }
        });

        return section;
    }

    public boolean hasKey(String key) {
        return config.containsKey(key);
    }

    public Set<String> getAllKeys() {
        return new HashSet<>(config.keySet());
    }

    public void addChangeListener(ConfigChangeListener listener) {
        listeners.add(listener);
    }

    public void removeChangeListener(ConfigChangeListener listener) {
        listeners.remove(listener);
    }

    private void notifyListeners(String key, Object oldValue, Object newValue) {
        for (ConfigChangeListener listener : listeners) {
            try {
                listener.onConfigChange(key, oldValue, newValue);
            } catch (Exception e) {
                System.err.println("Error in change listener: " + e.getMessage());
            }
        }
    }

    public void printConfig() {
        System.out.println("\n=== Current Configuration ===");
        config.entrySet().stream()
            .sorted(Map.Entry.comparingByKey())
            .forEach(entry -> System.out.println(entry.getKey() + " = " + entry.getValue()));
    }

    public Map<String, Object> getAll() {
        return new HashMap<>(config);
    }
}

class TypesafeConfigManager {
    private Config config;

    public TypesafeConfigManager() {
        this.config = ConfigFactory.load();
    }

    public TypesafeConfigManager(String resource) {
        this.config = ConfigFactory.load(resource);
    }

    public void reload() {
        ConfigFactory.invalidateCaches();
        this.config = ConfigFactory.load();
        System.out.println("Typesafe config reloaded");
    }

    public String getString(String path) {
        return config.getString(path);
    }

    public int getInt(String path) {
        return config.getInt(path);
    }

    public boolean getBoolean(String path) {
        return config.getBoolean(path);
    }

    public List<String> getStringList(String path) {
        return config.getStringList(path);
    }

    public Config getConfig(String path) {
        return config.getConfig(path);
    }

    public boolean hasPath(String path) {
        return config.hasPath(path);
    }

    public void printConfig() {
        System.out.println("\n=== Typesafe Configuration ===");
        System.out.println(config.root().render(ConfigRenderOptions.concise()));
    }
}

class ConfigValidator {
    public static boolean validate(ConfigManager config, Map<String, Class<?>> schema) {
        List<String> errors = new ArrayList<>();

        schema.forEach((key, expectedType) -> {
            if (!config.hasKey(key)) {
                errors.add("Missing required key: " + key);
            } else {
                // Type validation could be added here
            }
        });

        if (!errors.isEmpty()) {
            System.err.println("Configuration validation errors:");
            errors.forEach(error -> System.err.println("  - " + error));
            return false;
        }

        System.out.println("Configuration validation passed");
        return true;
    }
}

public class ConfigManagerApp {

    public static void main(String[] args) throws IOException, InterruptedException {
        System.out.println("=== Configuration Management System ===\n");

        // Create sample configuration files
        createSampleConfigs();

        // Example 1: Basic configuration loading
        System.out.println("--- Example 1: Multiple Configuration Sources ---");

        ConfigManager configManager = new ConfigManager();

        // Set defaults
        configManager.setDefault("app.name", "MyApp");
        configManager.setDefault("app.version", "1.0.0");
        configManager.setDefault("server.port", 8080);

        // Add sources (in order of priority)
        configManager.addSource(new PropertiesConfigSource("config.properties"));
        configManager.addSource(new JsonConfigSource("config.json"));
        configManager.addSource(new EnvironmentConfigSource("APP_"));

        // Load configuration
        configManager.load();
        configManager.printConfig();

        // Example 2: Type-safe access
        System.out.println("\n--- Example 2: Type-Safe Configuration Access ---");

        String appName = configManager.getString("app.name");
        int serverPort = configManager.getInt("server.port");
        boolean debugMode = configManager.getBoolean("app.debug", false);

        System.out.println("Application: " + appName);
        System.out.println("Server Port: " + serverPort);
        System.out.println("Debug Mode: " + debugMode);

        // Example 3: Configuration sections
        System.out.println("\n--- Example 3: Configuration Sections ---");

        Map<String, Object> databaseConfig = configManager.getSection("database");
        System.out.println("Database configuration:");
        databaseConfig.forEach((key, value) ->
            System.out.println("  " + key + " = " + value)
        );

        // Example 4: Change listeners
        System.out.println("\n--- Example 4: Configuration Change Listeners ---");

        configManager.addChangeListener((key, oldValue, newValue) -> {
            System.out.println("  [Listener] Config changed: " + key);
            System.out.println("    Old value: " + oldValue);
            System.out.println("    New value: " + newValue);
        });

        // Modify config file to trigger change detection
        System.out.println("\nModifying configuration...");
        Files.writeString(Paths.get("config.json"),
            "{\"app\":{\"name\":\"MyApp\",\"version\":\"2.0.0\"},\"server\":{\"port\":9090}}");

        configManager.reload();

        // Example 5: Configuration validation
        System.out.println("\n--- Example 5: Configuration Validation ---");

        Map<String, Class<?>> schema = Map.of(
            "app.name", String.class,
            "app.version", String.class,
            "server.port", Integer.class
        );

        boolean valid = ConfigValidator.validate(configManager, schema);
        System.out.println("Configuration valid: " + valid);

        // Example 6: Typesafe Config (Lightbend)
        System.out.println("\n--- Example 6: Typesafe Config Library ---");

        // Create application.conf
        String hoconConfig = """
            app {
              name = "TypesafeApp"
              version = "1.0.0"
              features = ["auth", "cache", "logging"]
            }
            database {
              host = "localhost"
              port = 5432
              name = "mydb"
            }
            """;
        Files.writeString(Paths.get("application.conf"), hoconConfig);

        TypesafeConfigManager typesafeConfig = new TypesafeConfigManager("application");
        System.out.println("App name: " + typesafeConfig.getString("app.name"));
        System.out.println("DB port: " + typesafeConfig.getInt("database.port"));
        System.out.println("Features: " + typesafeConfig.getStringList("app.features"));

        // Example 7: Environment-specific configuration
        System.out.println("\n--- Example 7: Environment-Specific Overrides ---");

        ConfigManager envConfig = new ConfigManager();
        envConfig.setDefault("app.env", "development");

        // Load base config
        envConfig.addSource(new JsonConfigSource("config.json"));

        // Load environment-specific config (would override base)
        String environment = System.getProperty("env", "development");
        System.out.println("Current environment: " + environment);

        envConfig.load();

        // Example 8: All configuration keys
        System.out.println("\n--- Example 8: All Configuration Keys ---");

        Set<String> allKeys = configManager.getAllKeys();
        System.out.println("Total configuration keys: " + allKeys.size());
        System.out.println("Keys: " + allKeys);

        // Cleanup
        configManager.stopAutoReload();

        // Clean up sample files
        Files.deleteIfExists(Paths.get("config.properties"));
        Files.deleteIfExists(Paths.get("config.json"));
        Files.deleteIfExists(Paths.get("application.conf"));

        System.out.println("\n=== Configuration Management Demo Complete ===");
        System.out.println("\nKey Features:");
        System.out.println("  ✓ Multiple configuration sources");
        System.out.println("  ✓ Hierarchical configuration with fallbacks");
        System.out.println("  ✓ Type-safe access methods");
        System.out.println("  ✓ Dynamic reloading");
        System.out.println("  ✓ Change listeners");
        System.out.println("  ✓ Configuration validation");
        System.out.println("  ✓ Environment-specific overrides");
        System.out.println("  ✓ Configuration sections");
    }

    private static void createSampleConfigs() throws IOException {
        // Create sample properties file
        String properties = """
            app.name=MyApplication
            app.version=1.0.0
            server.port=8080
            database.host=localhost
            database.port=5432
            database.name=mydb
            """;
        Files.writeString(Paths.get("config.properties"), properties);

        // Create sample JSON file
        String json = """
            {
              "app": {
                "name": "MyApp",
                "version": "1.0.0",
                "debug": true
              },
              "server": {
                "port": 8080,
                "host": "0.0.0.0"
              },
              "database": {
                "host": "localhost",
                "port": 5432,
                "name": "mydb",
                "username": "admin"
              }
            }
            """;
        Files.writeString(Paths.get("config.json"), json);
    }
}
