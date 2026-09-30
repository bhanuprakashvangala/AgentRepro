package com.example.jsonvalidator.model;

import java.util.List;

public class ValidationResponse {

    private boolean valid;
    private List<String> errors;
    private Object parsedObject;

    public ValidationResponse(boolean valid, List<String> errors, Object parsedObject) {
        this.valid = valid;
        this.errors = errors;
        this.parsedObject = parsedObject;
    }

    public boolean isValid() {
        return valid;
    }

    public void setValid(boolean valid) {
        this.valid = valid;
    }

    public List<String> getErrors() {
        return errors;
    }

    public void setErrors(List<String> errors) {
        this.errors = errors;
    }

    public Object getParsedObject() {
        return parsedObject;
    }

    public void setParsedObject(Object parsedObject) {
        this.parsedObject = parsedObject;
    }
}
