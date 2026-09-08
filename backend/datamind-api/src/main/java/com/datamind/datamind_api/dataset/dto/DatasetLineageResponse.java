package com.datamind.datamind_api.dataset.dto;

import java.time.LocalDateTime;
import java.util.UUID;

public record DatasetLineageResponse(
        UUID datasetId,
        UUID parentDatasetId,
        String operation,
        String columnName,
        Integer rowsAffected,
        String details,
        LocalDateTime createdAt
) {
}