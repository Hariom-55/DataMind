package com.datamind.datamind_api.analysis.integration.python.dto;

import java.util.List;

public record PythonCleaningResponse(
        String content,
        String content_hash,
        String extension,
        int original_rows,
        int cleaned_rows,
        int original_columns,
        int cleaned_columns,
        int operations_applied,
        List<PythonCleaningChange> changes
) {
}