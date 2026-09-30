package com.example.pdfservice.model;

import java.util.List;

public class ReportTemplate {

    private PageConfig page;
    private FontConfig fonts;
    private ColorConfig colors;
    private LogoConfig logo;
    private TableConfig table;

    public PageConfig getPage() {
        return page;
    }

    public void setPage(PageConfig page) {
        this.page = page;
    }

    public FontConfig getFonts() {
        return fonts;
    }

    public void setFonts(FontConfig fonts) {
        this.fonts = fonts;
    }

    public ColorConfig getColors() {
        return colors;
    }

    public void setColors(ColorConfig colors) {
        this.colors = colors;
    }

    public LogoConfig getLogo() {
        return logo;
    }

    public void setLogo(LogoConfig logo) {
        this.logo = logo;
    }

    public TableConfig getTable() {
        return table;
    }

    public void setTable(TableConfig table) {
        this.table = table;
    }

    public static class PageConfig {
        private float margin = 50f;
        private String backgroundColor;

        public float getMargin() {
            return margin;
        }

        public void setMargin(float margin) {
            this.margin = margin;
        }

        public String getBackgroundColor() {
            return backgroundColor;
        }

        public void setBackgroundColor(String backgroundColor) {
            this.backgroundColor = backgroundColor;
        }
    }

    public static class FontConfig {
        private float titleSize = 24f;
        private float subtitleSize = 14f;
        private float bodySize = 11f;
        private float tableHeaderSize = 12f;

        public float getTitleSize() {
            return titleSize;
        }

        public void setTitleSize(float titleSize) {
            this.titleSize = titleSize;
        }

        public float getSubtitleSize() {
            return subtitleSize;
        }

        public void setSubtitleSize(float subtitleSize) {
            this.subtitleSize = subtitleSize;
        }

        public float getBodySize() {
            return bodySize;
        }

        public void setBodySize(float bodySize) {
            this.bodySize = bodySize;
        }

        public float getTableHeaderSize() {
            return tableHeaderSize;
        }

        public void setTableHeaderSize(float tableHeaderSize) {
            this.tableHeaderSize = tableHeaderSize;
        }
    }

    public static class ColorConfig {
        private String primary;
        private String secondary;
        private String tableHeaderBackground;
        private String tableBorder;

        public String getPrimary() {
            return primary;
        }

        public void setPrimary(String primary) {
            this.primary = primary;
        }

        public String getSecondary() {
            return secondary;
        }

        public void setSecondary(String secondary) {
            this.secondary = secondary;
        }

        public String getTableHeaderBackground() {
            return tableHeaderBackground;
        }

        public void setTableHeaderBackground(String tableHeaderBackground) {
            this.tableHeaderBackground = tableHeaderBackground;
        }

        public String getTableBorder() {
            return tableBorder;
        }

        public void setTableBorder(String tableBorder) {
            this.tableBorder = tableBorder;
        }
    }

    public static class LogoConfig {
        private String text;
        private String background;
        private String foreground;

        public String getText() {
            return text;
        }

        public void setText(String text) {
            this.text = text;
        }

        public String getBackground() {
            return background;
        }

        public void setBackground(String background) {
            this.background = background;
        }

        public String getForeground() {
            return foreground;
        }

        public void setForeground(String foreground) {
            this.foreground = foreground;
        }
    }

    public static class TableConfig {
        private List<TableColumn> columns;

        public List<TableColumn> getColumns() {
            return columns;
        }

        public void setColumns(List<TableColumn> columns) {
            this.columns = columns;
        }
    }

    public static class TableColumn {
        private String header;
        private float width;

        public String getHeader() {
            return header;
        }

        public void setHeader(String header) {
            this.header = header;
        }

        public float getWidth() {
            return width;
        }

        public void setWidth(float width) {
            this.width = width;
        }
    }
}
