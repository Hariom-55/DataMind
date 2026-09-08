package com.datamind.datamind_api.analysis.integration.python.dto;

public record PythonCleaningChange(
        String operation,
        String column,
        int rowsAffected,
        String details
) {
}