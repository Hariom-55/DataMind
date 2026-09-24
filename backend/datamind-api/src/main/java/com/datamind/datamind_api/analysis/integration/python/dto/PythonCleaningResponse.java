package com.datamind.datamind_api.analysis.integration.python.dto;

import java.util.List;

public record PythonCleaningResponse(
        String artifact_id,
        String sha256,
        String extension,
        int original_rows,
        int cleaned_rows,
        int original_columns,
        int cleaned_columns,
        int operations_applied,
        List<PythonCleaningChange> changes,
        String format,
        String content_type,
        long size_bytes
) {
    public PythonCleaningResponse(
            String ignoredArtifactReference,
            String sha256,
            String extension,
            int original_rows,
            int cleaned_rows,
            int original_columns,
            int cleaned_columns,
            int operations_applied,
            List<PythonCleaningChange> changes
    ) {
        this("00000000-0000-0000-0000-000000000000", sha256, extension, original_rows, cleaned_rows,
                original_columns, cleaned_columns, operations_applied, changes,
                "CSV", "text/csv", -1);
    }
}
