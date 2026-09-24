package com.datamind.datamind_api.analysis.integration.python.dto;

import java.util.List;
import java.util.Map;

public record PythonCleaningAssessmentResponse(
        int totalRows,
        int totalColumns,
        int issueCount,
        List<Map<String, Object>> issues,
        List<Map<String, Object>> recommendations
) {
}
