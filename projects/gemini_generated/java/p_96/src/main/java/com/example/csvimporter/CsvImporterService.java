package com.example.csvimporter;

import org.apache.commons.csv.CSVFormat;
import org.apache.commons.csv.CSVParser;
import org.apache.commons.csv.CSVRecord;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.jdbc.core.BatchPreparedStatementSetter;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;

import javax.annotation.PostConstruct;
import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.sql.PreparedStatement;
import java.sql.SQLException;
import java.util.ArrayList;
import java.util.List;

@Service
public class CsvImporterService {

    private final JdbcTemplate jdbcTemplate;

    @Autowired
    public CsvImporterService(JdbcTemplate jdbcTemplate) {
        this.jdbcTemplate = jdbcTemplate;
    }

    @PostConstruct
    public void init() {
        jdbcTemplate.execute("DROP TABLE IF EXISTS users");
        jdbcTemplate.execute("CREATE TABLE users (id INT, name VARCHAR(255), email VARCHAR(255), age INT)");
    }

    public void importCsv(MultipartFile file) throws IOException {
        try (BufferedReader fileReader = new BufferedReader(new InputStreamReader(file.getInputStream(), "UTF-8"));
             CSVParser csvParser = new CSVParser(fileReader, CSVFormat.DEFAULT.withFirstRecordAsHeader().withIgnoreHeaderCase().withTrim())) {

            List<CSVRecord> csvRecords = csvParser.getRecords();
            List<Object[]> batchArgs = new ArrayList<>();

            for (CSVRecord csvRecord : csvRecords) {
                try {
                    int id = Integer.parseInt(csvRecord.get("id"));
                    String name = csvRecord.get("name");
                    String email = csvRecord.get("email");
                    int age = Integer.parseInt(csvRecord.get("age"));
                    batchArgs.add(new Object[]{id, name, email, age});
                } catch (NumberFormatException e) {
                    System.err.println("Skipping record due to number format error: " + csvRecord.toString() + " - " + e.getMessage());
                } catch (IllegalArgumentException e) {
                    System.err.println("Skipping record due to missing header or invalid column: " + csvRecord.toString() + " - " + e.getMessage());
                }
            }

            jdbcTemplate.batchUpdate("INSERT INTO users (id, name, email, age) VALUES (?, ?, ?, ?)", new BatchPreparedStatementSetter() {
                @Override
                public void setValues(PreparedStatement ps, int i) throws SQLException {
                    Object[] args = batchArgs.get(i);
                    ps.setInt(1, (Integer) args[0]);
                    ps.setString(2, (String) args[1]);
                    ps.setString(3, (String) args[2]);
                    ps.setInt(4, (Integer) args[3]);
                }

                @Override
                public int getBatchSize() {
                    return batchArgs.size();
                }
            });
        }
    }

    public List<Map<String, Object>> getAllUsers() {
        return jdbcTemplate.queryForList("SELECT * FROM users");
    }
}
