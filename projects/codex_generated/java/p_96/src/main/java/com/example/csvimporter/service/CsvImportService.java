package com.example.csvimporter.service;

import java.io.BufferedReader;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.SQLException;
import java.util.ArrayList;
import java.util.List;
import javax.sql.DataSource;
import org.apache.commons.csv.CSVFormat;
import org.apache.commons.csv.CSVParser;
import org.apache.commons.csv.CSVRecord;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
public class CsvImportService {

    private static final Logger logger = LoggerFactory.getLogger(CsvImportService.class);
    private static final int BATCH_SIZE = 100;

    private final DataSource dataSource;

    public CsvImportService(DataSource dataSource) {
        this.dataSource = dataSource;
    }

    @Transactional
    public int importCsv(Path csvPath) throws IOException {
        try (BufferedReader reader = Files.newBufferedReader(csvPath);
             CSVParser parser = CSVFormat.DEFAULT
                     .withFirstRecordAsHeader()
                     .withTrim()
                     .parse(reader);
             Connection connection = dataSource.getConnection()) {

            connection.setAutoCommit(false);
            String sql = "INSERT INTO persons(name, email, age) VALUES (?, ?, ?)";
            try (PreparedStatement statement = connection.prepareStatement(sql)) {
                int count = 0;
                int batchCount = 0;
                for (CSVRecord record : parser) {
                    try {
                        String name = record.get("name");
                        String email = record.get("email");
                        String ageStr = record.get("age");
                        Integer age = ageStr == null || ageStr.isBlank() ? null : Integer.valueOf(ageStr);

                        statement.setString(1, name);
                        statement.setString(2, email);
                        if (age == null) {
                            statement.setNull(3, java.sql.Types.INTEGER);
                        } else {
                            statement.setInt(3, age);
                        }
                        statement.addBatch();
                        batchCount++;
                        count++;

                        if (batchCount >= BATCH_SIZE) {
                            statement.executeBatch();
                            batchCount = 0;
                        }
                    } catch (IllegalArgumentException | SQLException ex) {
                        logger.error("Skipping record {} due to error: {}", record.getRecordNumber(), ex.getMessage());
                    }
                }
                if (batchCount > 0) {
                    statement.executeBatch();
                }
                connection.commit();
                return count;
            } catch (SQLException ex) {
                connection.rollback();
                throw new IOException("Failed to import CSV", ex);
            } finally {
                connection.setAutoCommit(true);
            }
        } catch (SQLException ex) {
            throw new IOException("Failed to obtain database connection", ex);
        }
    }
}
