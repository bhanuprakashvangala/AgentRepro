package com.example.excel;

import org.apache.poi.ss.usermodel.*;
import org.apache.poi.xssf.usermodel.XSSFWorkbook;

import java.io.FileOutputStream;
import java.io.IOException;
import java.time.LocalDate;
import java.util.*;

public class ExcelGenerator {
    private Workbook workbook;
    private CellStyle headerStyle;
    private CellStyle dateStyle;
    private CellStyle currencyStyle;

    public ExcelGenerator() {
        this.workbook = new XSSFWorkbook();
        initializeStyles();
    }

    private void initializeStyles() {
        // Header style
        headerStyle = workbook.createCellStyle();
        Font headerFont = workbook.createFont();
        headerFont.setBold(true);
        headerFont.setFontHeightInPoints((short) 12);
        headerFont.setColor(IndexedColors.WHITE.getIndex());
        headerStyle.setFont(headerFont);
        headerStyle.setFillForegroundColor(IndexedColors.DARK_BLUE.getIndex());
        headerStyle.setFillPattern(FillPatternType.SOLID_FOREGROUND);
        headerStyle.setBorderBottom(BorderStyle.THIN);
        headerStyle.setBorderTop(BorderStyle.THIN);
        headerStyle.setBorderLeft(BorderStyle.THIN);
        headerStyle.setBorderRight(BorderStyle.THIN);

        // Date style
        dateStyle = workbook.createCellStyle();
        CreationHelper createHelper = workbook.getCreationHelper();
        dateStyle.setDataFormat(createHelper.createDataFormat().getFormat("yyyy-mm-dd"));

        // Currency style
        currencyStyle = workbook.createCellStyle();
        currencyStyle.setDataFormat(createHelper.createDataFormat().getFormat("$#,##0.00"));
    }

    public Sheet createSheet(String sheetName) {
        return workbook.createSheet(sheetName);
    }

    public void createHeaderRow(Sheet sheet, String[] headers) {
        Row headerRow = sheet.createRow(0);
        for (int i = 0; i < headers.length; i++) {
            Cell cell = headerRow.createCell(i);
            cell.setCellValue(headers[i]);
            cell.setCellStyle(headerStyle);
        }
    }

    public void autoSizeColumns(Sheet sheet, int columnCount) {
        for (int i = 0; i < columnCount; i++) {
            sheet.autoSizeColumn(i);
        }
    }

    public void setCellValue(Row row, int columnIndex, Object value, CellStyle style) {
        Cell cell = row.createCell(columnIndex);

        if (value == null) {
            cell.setCellValue("");
        } else if (value instanceof String) {
            cell.setCellValue((String) value);
        } else if (value instanceof Number) {
            cell.setCellValue(((Number) value).doubleValue());
            if (style != null) {
                cell.setCellStyle(style);
            }
        } else if (value instanceof Date) {
            cell.setCellValue((Date) value);
            cell.setCellStyle(dateStyle);
        } else if (value instanceof LocalDate) {
            cell.setCellValue(value.toString());
        } else if (value instanceof Boolean) {
            cell.setCellValue((Boolean) value);
        } else {
            cell.setCellValue(value.toString());
        }
    }

    public void createSalesReport(String outputPath) throws IOException {
        Sheet sheet = createSheet("Sales Report");

        // Headers
        String[] headers = {"Date", "Product", "Quantity", "Unit Price", "Total", "Sales Rep"};
        createHeaderRow(sheet, headers);

        // Sample data
        Object[][] data = {
            {new Date(), "Laptop", 5, 999.99, null, "John Doe"},
            {new Date(), "Mouse", 20, 29.99, null, "Jane Smith"},
            {new Date(), "Keyboard", 15, 79.99, null, "John Doe"},
            {new Date(), "Monitor", 8, 299.99, null, "Bob Johnson"},
            {new Date(), "Webcam", 12, 89.99, null, "Jane Smith"}
        };

        // Add data rows
        for (int i = 0; i < data.length; i++) {
            Row row = sheet.createRow(i + 1);
            for (int j = 0; j < data[i].length; j++) {
                if (j == 4) {
                    // Total column - add formula
                    Cell cell = row.createCell(j);
                    cell.setCellFormula(String.format("C%d*D%d", i + 2, i + 2));
                    cell.setCellStyle(currencyStyle);
                } else if (j == 3) {
                    // Unit Price column
                    setCellValue(row, j, data[i][j], currencyStyle);
                } else {
                    setCellValue(row, j, data[i][j], null);
                }
            }
        }

        // Add totals row
        int lastRow = data.length + 1;
        Row totalRow = sheet.createRow(lastRow);
        Cell totalLabel = totalRow.createCell(3);
        totalLabel.setCellValue("TOTAL:");
        totalLabel.setCellStyle(headerStyle);

        Cell totalCell = totalRow.createCell(4);
        totalCell.setCellFormula(String.format("SUM(E2:E%d)", lastRow));
        totalCell.setCellStyle(currencyStyle);

        autoSizeColumns(sheet, headers.length);

        saveWorkbook(outputPath);
        System.out.println("Sales report created: " + outputPath);
    }

    public void createEmployeeReport(String outputPath) throws IOException {
        Sheet sheet = createSheet("Employee Report");

        // Headers
        String[] headers = {"Employee ID", "Name", "Department", "Hire Date", "Salary", "Active"};
        createHeaderRow(sheet, headers);

        // Sample data
        Object[][] data = {
            {"EMP001", "Alice Johnson", "Engineering", new Date(), 85000.00, true},
            {"EMP002", "Bob Smith", "Marketing", new Date(), 72000.00, true},
            {"EMP003", "Charlie Brown", "Sales", new Date(), 68000.00, true},
            {"EMP004", "Diana Prince", "HR", new Date(), 75000.00, true},
            {"EMP005", "Eve Wilson", "Finance", new Date(), 90000.00, false}
        };

        // Add data rows
        for (int i = 0; i < data.length; i++) {
            Row row = sheet.createRow(i + 1);
            for (int j = 0; j < data[i].length; j++) {
                if (j == 4) {
                    // Salary column
                    setCellValue(row, j, data[i][j], currencyStyle);
                } else {
                    setCellValue(row, j, data[i][j], null);
                }
            }
        }

        // Add statistics
        int statsRow = data.length + 2;
        Row avgRow = sheet.createRow(statsRow);
        avgRow.createCell(3).setCellValue("Average Salary:");
        Cell avgCell = avgRow.createCell(4);
        avgCell.setCellFormula(String.format("AVERAGE(E2:E%d)", data.length + 1));
        avgCell.setCellStyle(currencyStyle);

        Row maxRow = sheet.createRow(statsRow + 1);
        maxRow.createCell(3).setCellValue("Max Salary:");
        Cell maxCell = maxRow.createCell(4);
        maxCell.setCellFormula(String.format("MAX(E2:E%d)", data.length + 1));
        maxCell.setCellStyle(currencyStyle);

        autoSizeColumns(sheet, headers.length);

        saveWorkbook(outputPath);
        System.out.println("Employee report created: " + outputPath);
    }

    public void saveWorkbook(String outputPath) throws IOException {
        try (FileOutputStream fileOut = new FileOutputStream(outputPath)) {
            workbook.write(fileOut);
        }
    }

    public void close() throws IOException {
        if (workbook != null) {
            workbook.close();
        }
    }

    // Example usage
    public static void main(String[] args) {
        ExcelGenerator generator = new ExcelGenerator();

        try {
            // Generate sales report
            generator.createSalesReport("sales_report.xlsx");

            // Create new generator for employee report
            ExcelGenerator generator2 = new ExcelGenerator();
            generator2.createEmployeeReport("employee_report.xlsx");
            generator2.close();

            System.out.println("\nReports generated successfully!");

        } catch (IOException e) {
            System.err.println("Error generating reports: " + e.getMessage());
            e.printStackTrace();
        } finally {
            try {
                generator.close();
            } catch (IOException e) {
                e.printStackTrace();
            }
        }
    }
}
