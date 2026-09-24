package com.datamind.datamind_api.dataset.dto;

import com.datamind.datamind_api.analysis.integration.python.dto.PythonCleaningChange;

import java.util.List;
import java.util.UUID;

public record CleaningPreviewResponse(
        UUID logicalDatasetId,
        UUID datasetVersionId,
        int versionNumber,
        int originalRows,
        int cleanedRows,
        int originalColumns,
        int cleanedColumns,
        int operationsApplied,
        List<PythonCleaningChange> changes
) {
}
