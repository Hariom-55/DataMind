package com.datamind.datamind_api.dataset.dto;

import com.datamind.datamind_api.analysis.integration.python.dto.PythonCleaningChange;

import java.util.List;
import java.util.UUID;

public record DatasetCleaningResponse(
        UUID logicalDatasetId,
        UUID parentDatasetVersionId,
        int parentVersionNumber,
        int originalRows,
        int cleanedRows,
        int originalColumns,
        int cleanedColumns,
        int operationsApplied,
        String format,
        String extension,
        String contentType,
        DatasetResponse dataset,
        List<PythonCleaningChange> changes,
        List<DatasetLineageResponse> lineage
) {
}
