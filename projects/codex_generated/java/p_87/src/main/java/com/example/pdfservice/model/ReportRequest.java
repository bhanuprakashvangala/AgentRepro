package com.example.pdfservice.model;

import jakarta.validation.Valid;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotEmpty;

import java.util.List;

public class ReportRequest {

    @NotBlank
    private String title;

    private String subtitle;

    @NotBlank
    private String preparedFor;

    @NotBlank
    private String preparedBy;

    @Valid
    @NotEmpty
    private List<LineItem> items;

    private String notes;

    public String getTitle() {
        return title;
    }

    public void setTitle(String title) {
        this.title = title;
    }

    public String getSubtitle() {
        return subtitle;
    }

    public void setSubtitle(String subtitle) {
        this.subtitle = subtitle;
    }

    public String getPreparedFor() {
        return preparedFor;
    }

    public void setPreparedFor(String preparedFor) {
        this.preparedFor = preparedFor;
    }

    public String getPreparedBy() {
        return preparedBy;
    }

    public void setPreparedBy(String preparedBy) {
        this.preparedBy = preparedBy;
    }

    public List<LineItem> getItems() {
        return items;
    }

    public void setItems(List<LineItem> items) {
        this.items = items;
    }

    public String getNotes() {
        return notes;
    }

    public void setNotes(String notes) {
        this.notes = notes;
    }
}
