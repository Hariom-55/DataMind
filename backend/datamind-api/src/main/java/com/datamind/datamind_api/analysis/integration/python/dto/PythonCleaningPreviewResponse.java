package com.datamind.datamind_api.analysis.integration.python.dto;

import java.util.List;

public record PythonCleaningPreviewResponse(
        int originalRows,
        int cleanedRows,
        int originalColumns,
        int cleanedColumns,
        int operationsApplied,
        List<PythonCleaningChange> changes
) {
}
