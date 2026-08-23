package com.datamind.datamind_api.analysis.integration.python.dto;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;

import java.util.Map;


@JsonIgnoreProperties(ignoreUnknown = true)
public class PythonAnalysisResponse
{
    private String status;
    private Map<String, Object> result;
    private String error;

    public PythonAnalysisResponse() {}

    public String getStatus() {
        return status;
    }

    public void setStatus(String status) {
        this.status = status;
    }

    public Map<String, Object> getResult() {
        return result;
    }

    public void setResult(Map<String, Object> result) {
        this.result = result;
    }

    public String getError() {
        return error;
    }

    public void setError(String error) {
        this.error = error;
    }
}
