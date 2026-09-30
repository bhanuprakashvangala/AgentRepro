package com.example.pdfservice.service;

import com.example.pdfservice.model.LineItem;
import com.example.pdfservice.model.ReportRequest;
import com.example.pdfservice.model.ReportTemplate;
import java.awt.BasicStroke;
import java.awt.Color;
import java.awt.Font;
import java.awt.Graphics2D;
import java.awt.RenderingHints;
import java.awt.image.BufferedImage;
import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.math.BigDecimal;
import java.util.ArrayList;
import java.util.List;

import org.apache.pdfbox.pdmodel.PDDocument;
import org.apache.pdfbox.pdmodel.PDPage;
import org.apache.pdfbox.pdmodel.PDPageContentStream;
import org.apache.pdfbox.pdmodel.common.PDRectangle;
import org.apache.pdfbox.pdmodel.font.PDType1Font;
import org.apache.pdfbox.pdmodel.graphics.image.PDImageXObject;
import org.springframework.stereotype.Service;

@Service
public class PdfReportService {

    private final ReportTemplate template;

    public PdfReportService(TemplateLoader loader) throws IOException {
        this.template = loader.load("/templates/report-template.json");
    }

    public byte[] generateReport(ReportRequest request) throws IOException {
        try (PDDocument document = new PDDocument()) {
            PDPage page = new PDPage(PDRectangle.LETTER);
            document.addPage(page);

            try (PDPageContentStream contentStream = new PDPageContentStream(document, page)) {
                float margin = pageConfig().getMargin();
                PDRectangle mediaBox = page.getMediaBox();
                float width = mediaBox.getWidth();
                float height = mediaBox.getHeight();

                drawBackground(contentStream, width, height);
                float cursorY = height - margin;

                cursorY = drawHeader(document, contentStream, margin, cursorY, request);
                cursorY = drawMeta(contentStream, margin, cursorY, request);
                cursorY -= 20;
                cursorY = drawTable(document, contentStream, margin, width - margin, cursorY, request);
                cursorY -= 20;
                drawNotes(contentStream, margin, cursorY, request);
            }

            try (ByteArrayOutputStream baos = new ByteArrayOutputStream()) {
                document.save(baos);
                return baos.toByteArray();
            }
        }
    }

    private void drawBackground(PDPageContentStream contentStream, float width, float height) throws IOException {
        String hex = pageConfig().getBackgroundColor();
        if (hex == null || hex.isBlank()) {
            return;
        }
        Color color = parseColor(hex, new Color(0xF7, 0xFA, 0xFC));
        contentStream.setNonStrokingColor(color);
        contentStream.addRect(0, 0, width, height);
        contentStream.fill();
    }

    private float drawHeader(PDDocument document, PDPageContentStream contentStream, float margin, float cursorY,
                             ReportRequest request) throws IOException {
        float logoHeight = 60;
        float logoWidth = 160;
        ReportTemplate.LogoConfig logoConfig = template.getLogo();
        if (logoConfig == null) {
            logoConfig = new ReportTemplate.LogoConfig();
            logoConfig.setText("PDF Report");
            logoConfig.setBackground("#2B6CB0");
            logoConfig.setForeground("#FFFFFF");
        }
        BufferedImage logo = createLogo(logoConfig);
        PDImageXObject logoImage = PDImageXObject.createFromByteArray(document, toPngBytes(logo), "logo");
        contentStream.drawImage(logoImage, margin, cursorY - logoHeight, logoWidth, logoHeight);

        float textStartX = margin + logoWidth + 20;
        float textY = cursorY - 20;

        contentStream.beginText();
        contentStream.setFont(PDType1Font.HELVETICA_BOLD, fonts().getTitleSize());
        contentStream.setNonStrokingColor(parseColor(colors().getPrimary(), Color.decode("#2B6CB0")));
        contentStream.newLineAtOffset(textStartX, textY);
        contentStream.showText(request.getTitle());
        contentStream.endText();

        textY -= fonts().getSubtitleSize() + 6;
        if (request.getSubtitle() != null && !request.getSubtitle().isBlank()) {
            contentStream.beginText();
            contentStream.setFont(PDType1Font.HELVETICA_OBLIQUE, fonts().getSubtitleSize());
            contentStream.setNonStrokingColor(parseColor(colors().getSecondary(), Color.DARK_GRAY));
            contentStream.newLineAtOffset(textStartX, textY);
            contentStream.showText(request.getSubtitle());
            contentStream.endText();
        }

        return cursorY - logoHeight - 10;
    }

    private float drawMeta(PDPageContentStream contentStream, float margin, float cursorY, ReportRequest request)
            throws IOException {
        contentStream.beginText();
        contentStream.setFont(PDType1Font.HELVETICA_BOLD, fonts().getBodySize());
        contentStream.setNonStrokingColor(parseColor(colors().getSecondary(), Color.DARK_GRAY));
        contentStream.newLineAtOffset(margin, cursorY);
        contentStream.showText("Prepared for: ");
        contentStream.setFont(PDType1Font.HELVETICA, fonts().getBodySize());
        contentStream.showText(request.getPreparedFor());
        contentStream.endText();

        cursorY -= fonts().getBodySize() + 4;

        contentStream.beginText();
        contentStream.setFont(PDType1Font.HELVETICA_BOLD, fonts().getBodySize());
        contentStream.setNonStrokingColor(parseColor(colors().getSecondary(), Color.DARK_GRAY));
        contentStream.newLineAtOffset(margin, cursorY);
        contentStream.showText("Prepared by: ");
        contentStream.setFont(PDType1Font.HELVETICA, fonts().getBodySize());
        contentStream.showText(request.getPreparedBy());
        contentStream.endText();

        return cursorY - fonts().getBodySize() - 6;
    }

    private float drawTable(PDDocument document, PDPageContentStream contentStream, float startX, float endX,
                            float cursorY, ReportRequest request) throws IOException {

        float tableWidth = endX - startX;
        float rowHeight = 22;
        float y = cursorY;
        List<ReportTemplate.TableColumn> columns = tableConfig().getColumns();

        // Table header background
        contentStream.setNonStrokingColor(parseColor(colors().getTableHeaderBackground(), Color.LIGHT_GRAY));
        contentStream.addRect(startX, y - rowHeight, tableWidth, rowHeight);
        contentStream.fill();

        contentStream.setStrokingColor(parseColor(colors().getTableBorder(), Color.GRAY));
        contentStream.setLineWidth(0.75f);
        contentStream.addRect(startX, y - rowHeight, tableWidth, rowHeight);
        contentStream.stroke();

        float currentX = startX;
        for (ReportTemplate.TableColumn column : columns) {
            float colWidth = column.getWidth();
            contentStream.beginText();
            contentStream.setFont(PDType1Font.HELVETICA_BOLD, fonts().getTableHeaderSize());
            contentStream.setNonStrokingColor(parseColor(colors().getSecondary(), Color.BLACK));
            contentStream.newLineAtOffset(currentX + 6, y - rowHeight + 6);
            contentStream.showText(column.getHeader());
            contentStream.endText();
            currentX += colWidth;
        }

        y -= rowHeight;

        BigDecimal grandTotal = BigDecimal.ZERO;

        for (LineItem item : request.getItems()) {
            currentX = startX;
            float maxRowHeight = rowHeight;
            List<String> descriptionLines = wrapText(item.getDescription(), columns.get(1).getWidth() - 12, fonts().getBodySize());
            maxRowHeight = Math.max(maxRowHeight, (descriptionLines.size()) * (fonts().getBodySize() + 2) + 6);

            // Row border
            contentStream.setNonStrokingColor(Color.WHITE);
            contentStream.addRect(startX, y - maxRowHeight, tableWidth, maxRowHeight);
            contentStream.fill();
            contentStream.setNonStrokingColor(parseColor(colors().getSecondary(), Color.DARK_GRAY));

            float textY = y - 16;
            contentStream.beginText();
            contentStream.setFont(PDType1Font.HELVETICA_BOLD, fonts().getBodySize());
            contentStream.newLineAtOffset(currentX + 6, textY);
            contentStream.showText(item.getItem());
            contentStream.endText();

            currentX += columns.get(0).getWidth();
            textY = y - 16;
            contentStream.beginText();
            contentStream.setFont(PDType1Font.HELVETICA, fonts().getBodySize());
            contentStream.newLineAtOffset(currentX + 6, textY);
            for (String line : descriptionLines) {
                contentStream.showText(line);
                textY -= fonts().getBodySize() + 2;
                contentStream.newLineAtOffset(0, -fonts().getBodySize() - 2);
            }
            contentStream.endText();

            currentX += columns.get(1).getWidth();
            contentStream.beginText();
            contentStream.setFont(PDType1Font.HELVETICA, fonts().getBodySize());
            contentStream.newLineAtOffset(currentX + 6, y - 16);
            contentStream.showText(String.valueOf(item.getQuantity()));
            contentStream.endText();

            currentX += columns.get(2).getWidth();
            contentStream.beginText();
            contentStream.setFont(PDType1Font.HELVETICA, fonts().getBodySize());
            contentStream.newLineAtOffset(currentX + 6, y - 16);
            contentStream.showText(String.format("$%.2f", item.getUnitPrice()));
            contentStream.endText();

            currentX += columns.get(3).getWidth();
            BigDecimal total = item.getTotal();
            grandTotal = grandTotal.add(total);
            contentStream.beginText();
            contentStream.setFont(PDType1Font.HELVETICA_BOLD, fonts().getBodySize());
            contentStream.newLineAtOffset(currentX + 6, y - 16);
            contentStream.showText(String.format("$%.2f", total));
            contentStream.endText();

            contentStream.setStrokingColor(parseColor(colors().getTableBorder(), Color.GRAY));
            contentStream.addRect(startX, y - maxRowHeight, tableWidth, maxRowHeight);
            contentStream.stroke();

            y -= maxRowHeight;
        }

        // Total row
        contentStream.setStrokingColor(parseColor(colors().getPrimary(), Color.BLUE));
        contentStream.addRect(startX, y - rowHeight, tableWidth, rowHeight);
        contentStream.stroke();
        contentStream.beginText();
        contentStream.setFont(PDType1Font.HELVETICA_BOLD, fonts().getBodySize() + 1);
        contentStream.setNonStrokingColor(parseColor(colors().getPrimary(), Color.BLUE));
        contentStream.newLineAtOffset(startX + tableWidth - 150, y - 16);
        contentStream.showText("Grand Total: " + String.format("$%.2f", grandTotal));
        contentStream.endText();

        return y - rowHeight;
    }

    private void drawNotes(PDPageContentStream contentStream, float margin, float cursorY, ReportRequest request)
            throws IOException {
        if (request.getNotes() == null || request.getNotes().isBlank()) {
            return;
        }
        contentStream.beginText();
        contentStream.setFont(PDType1Font.HELVETICA_OBLIQUE, fonts().getBodySize());
        contentStream.setNonStrokingColor(parseColor(colors().getSecondary(), Color.DARK_GRAY));
        contentStream.newLineAtOffset(margin, cursorY);
        contentStream.showText("Notes: " + request.getNotes());
        contentStream.endText();
    }

    private List<String> wrapText(String text, float maxWidth, float fontSize) throws IOException {
        List<String> lines = new ArrayList<>();
        String[] words = text.split("\\s+");
        StringBuilder currentLine = new StringBuilder();
        for (String word : words) {
            String candidate = currentLine.length() == 0 ? word : currentLine + " " + word;
            float candidateWidth = getStringWidth(candidate, fontSize);
            if (candidateWidth > maxWidth && currentLine.length() > 0) {
                lines.add(currentLine.toString());
                currentLine = new StringBuilder(word);
            } else {
                currentLine = new StringBuilder(candidate);
            }
        }
        if (currentLine.length() > 0) {
            lines.add(currentLine.toString());
        }
        return lines;
    }

    private float getStringWidth(String text, float fontSize) throws IOException {
        return (PDType1Font.HELVETICA.getStringWidth(text) / 1000) * fontSize;
    }

    private Color parseColor(String hex, Color fallback) {
        if (hex == null) {
            return fallback;
        }
        try {
            return Color.decode(hex);
        } catch (NumberFormatException ex) {
            return fallback;
        }
    }

    private BufferedImage createLogo(ReportTemplate.LogoConfig logoConfig) {
        int width = 360;
        int height = 120;
        BufferedImage image = new BufferedImage(width, height, BufferedImage.TYPE_INT_ARGB);
        Graphics2D g2d = image.createGraphics();
        try {
            g2d.setRenderingHint(RenderingHints.KEY_ANTIALIASING, RenderingHints.VALUE_ANTIALIAS_ON);
            g2d.setColor(parseColor(logoConfig.getBackground(), Color.BLUE));
            g2d.fillRoundRect(0, 0, width, height, 30, 30);

            g2d.setStroke(new BasicStroke(4f));
            g2d.setColor(parseColor(logoConfig.getForeground(), Color.WHITE));
            g2d.drawRoundRect(4, 4, width - 8, height - 8, 24, 24);

            g2d.setFont(new Font("SansSerif", Font.BOLD, 26));
            g2d.setColor(parseColor(logoConfig.getForeground(), Color.WHITE));
            int textWidth = g2d.getFontMetrics().stringWidth(logoConfig.getText());
            int textX = (width - textWidth) / 2;
            int textY = height / 2 + g2d.getFontMetrics().getAscent() / 2 - 10;
            g2d.drawString(logoConfig.getText(), textX, textY);
        } finally {
            g2d.dispose();
        }
        return image;
    }

    private byte[] toPngBytes(BufferedImage image) throws IOException {
        try (ByteArrayOutputStream out = new ByteArrayOutputStream()) {
            javax.imageio.ImageIO.write(image, "png", out);
            return out.toByteArray();
        }
    }

    private ReportTemplate.FontConfig fonts() {
        if (template.getFonts() == null) {
            template.setFonts(new ReportTemplate.FontConfig());
        }
        return template.getFonts();
    }

    private ReportTemplate.ColorConfig colors() {
        if (template.getColors() == null) {
            ReportTemplate.ColorConfig config = new ReportTemplate.ColorConfig();
            config.setPrimary("#2B6CB0");
            config.setSecondary("#2D3748");
            config.setTableHeaderBackground("#E2E8F0");
            config.setTableBorder("#CBD5E0");
            template.setColors(config);
        }
        return template.getColors();
    }

    private ReportTemplate.PageConfig pageConfig() {
        if (template.getPage() == null) {
            template.setPage(new ReportTemplate.PageConfig());
        }
        return template.getPage();
    }

    private ReportTemplate.TableConfig tableConfig() {
        if (template.getTable() == null || template.getTable().getColumns() == null
                || template.getTable().getColumns().isEmpty()) {
            ReportTemplate.TableConfig config = new ReportTemplate.TableConfig();
            List<ReportTemplate.TableColumn> defaultColumns = new ArrayList<>();
            defaultColumns.add(createColumn("Item", 140));
            defaultColumns.add(createColumn("Description", 220));
            defaultColumns.add(createColumn("Qty", 60));
            defaultColumns.add(createColumn("Unit Price", 90));
            defaultColumns.add(createColumn("Total", 90));
            config.setColumns(defaultColumns);
            template.setTable(config);
        }
        return template.getTable();
    }

    private ReportTemplate.TableColumn createColumn(String header, float width) {
        ReportTemplate.TableColumn column = new ReportTemplate.TableColumn();
        column.setHeader(header);
        column.setWidth(width);
        return column;
    }
}
