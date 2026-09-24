package com.datamind.datamind_api.dataset.dto;

import java.util.List;
import java.util.Map;

public record CleaningAssessmentResponse(
        int totalRows,
        int totalColumns,
        int issueCount,
        List<Map<String, Object>> issues,
        List<Map<String, Object>> recommendations
) {
}
