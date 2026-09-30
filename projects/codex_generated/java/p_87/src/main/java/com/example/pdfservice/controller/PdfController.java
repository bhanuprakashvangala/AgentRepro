package com.example.pdfservice.controller;

import com.example.pdfservice.model.LineItem;
import com.example.pdfservice.model.ReportRequest;
import com.example.pdfservice.service.PdfReportService;
import jakarta.validation.Valid;
import java.io.IOException;
import java.math.BigDecimal;
import java.util.List;
import java.util.Map;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/pdf")
public class PdfController {

    private final PdfReportService pdfReportService;

    public PdfController(PdfReportService pdfReportService) {
        this.pdfReportService = pdfReportService;
    }

    @PostMapping(value = "/generate", produces = MediaType.APPLICATION_PDF_VALUE)
    public ResponseEntity<byte[]> generate(@RequestBody @Valid ReportRequest request) throws IOException {
        byte[] pdf = pdfReportService.generateReport(request);
        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_PDF);
        headers.setContentDispositionFormData("attachment", "report.pdf");
        headers.setContentLength(pdf.length);
        return ResponseEntity.ok().headers(headers).body(pdf);
    }

    @GetMapping(value = "/sample", produces = MediaType.APPLICATION_PDF_VALUE)
    public ResponseEntity<byte[]> sample() throws IOException {
        ReportRequest sampleRequest = buildSampleRequest();
        byte[] pdf = pdfReportService.generateReport(sampleRequest);
        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_PDF);
        headers.setContentDispositionFormData("attachment", "sample-report.pdf");
        headers.setContentLength(pdf.length);
        return ResponseEntity.ok().headers(headers).body(pdf);
    }

    @GetMapping("/template")
    public Map<String, Object> templateInfo() {
        return Map.of(
                "title", "Quarterly Performance Summary",
                "subtitle", "Includes dynamic tables, images, and styling.",
                "requiredFields", List.of("title", "preparedFor", "preparedBy", "items[]"),
                "notes", "POST /api/pdf/generate with a JSON body matching ReportRequest."
        );
    }

    private ReportRequest buildSampleRequest() {
        ReportRequest request = new ReportRequest();
        request.setTitle("Acme Analytics Quarterly Report");
        request.setSubtitle("Q2 Performance Overview");
        request.setPreparedFor("Innovatech Industries");
        request.setPreparedBy("Acme Analytics");

        LineItem item1 = new LineItem();
        item1.setItem("Website Audit");
        item1.setDescription("Comprehensive analysis of site structure, SEO health, and performance bottlenecks.");
        item1.setQuantity(1);
        item1.setUnitPrice(new BigDecimal("1200.00"));

        LineItem item2 = new LineItem();
        item2.setItem("Marketing Campaign");
        item2.setDescription("Targeted multi-channel marketing campaign spanning social, email, and search ads.");
        item2.setQuantity(3);
        item2.setUnitPrice(new BigDecimal("650.00"));

        LineItem item3 = new LineItem();
        item3.setItem("Data Dashboard");
        item3.setDescription("Custom-built analytics dashboard with real-time KPIs and executive summary views.");
        item3.setQuantity(2);
        item3.setUnitPrice(new BigDecimal("900.00"));

        request.setItems(List.of(item1, item2, item3));
        request.setNotes("Generated at runtime using Apache PDFBox template rendering.");
        return request;
    }
}
