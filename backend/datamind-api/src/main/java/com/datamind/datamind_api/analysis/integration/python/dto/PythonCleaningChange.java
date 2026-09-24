package com.datamind.datamind_api.analysis.integration.python.dto;

import java.util.Map;

public record PythonCleaningChange(
        String operation,
        String column,
        int rowsAffected,
        String details,
        Map<String, Object> parameters
) {
    public PythonCleaningChange(String operation, String column, int rowsAffected, String details) {
        this(operation, column, rowsAffected, details, Map.of());
    }
}
