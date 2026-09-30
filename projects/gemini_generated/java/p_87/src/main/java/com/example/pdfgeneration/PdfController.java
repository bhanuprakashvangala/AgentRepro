package com.example.pdfgeneration;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import java.util.HashMap;
import java.util.Map;

@RestController
public class PdfController {

    private final PdfGenerationService pdfGenerationService;

    @Autowired
    public PdfController(PdfGenerationService pdfGenerationService) {
        this.pdfGenerationService = pdfGenerationService;
    }

    @GetMapping("/generate-pdf")
    public ResponseEntity<byte[]> generatePdf(
            @RequestParam(defaultValue = "John Doe") String name,
            @RequestParam(defaultValue = "Spring Boot") String course
    ) {
        Map<String, Object> data = new HashMap<>();
        data.put("name", name);
        data.put("course", course);

        byte[] pdf = pdfGenerationService.generatePdf("template", data);

        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_PDF);
        headers.setContentDispositionFormData("attachment", "generated-pdf.pdf");

        return ResponseEntity.ok()
                .headers(headers)
                .body(pdf);
    }
}
