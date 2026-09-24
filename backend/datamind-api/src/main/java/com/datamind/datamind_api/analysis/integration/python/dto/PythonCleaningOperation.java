package com.datamind.datamind_api.analysis.integration.python.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;
import jakarta.validation.Valid;
import java.util.Map;

public record  PythonCleaningOperation(
    @NotBlank(message = "operation is required")
    @Size(max = 64)
    String operation,
    @Size(max = 255)
    String column,
    @Valid
    Map<String, Object> parameters
) {
    public PythonCleaningOperation {
        parameters = parameters == null ? Map.of() : Map.copyOf(parameters);
    }

    public PythonCleaningOperation(String operation, String column) {
        this(operation, column, Map.of());
    }
}
