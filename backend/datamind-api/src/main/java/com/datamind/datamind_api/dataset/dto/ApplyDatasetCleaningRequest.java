package com.datamind.datamind_api.dataset.dto;

import com.datamind.datamind_api.analysis.integration.python.dto.PythonCleaningOperation;
import jakarta.validation.Valid;
import jakarta.validation.constraints.NotEmpty;
import jakarta.validation.constraints.Size;

import java.util.List;

public record ApplyDatasetCleaningRequest(
        @NotEmpty(message = "At least one cleaning operation is required")
        @Size(max = 25, message = "A maximum of 25 cleaning operations may be submitted")
        List<@Valid PythonCleaningOperation> operations
) {
}
