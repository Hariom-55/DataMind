package com.datamind.datamind_api.dataset.dto;

import java.time.LocalDateTime;
import java.util.UUID;
import com.fasterxml.jackson.annotation.JsonProperty;
import java.util.List;
import java.util.Map;

public record DatasetLineageResponse(
        UUID datasetVersionId,
        UUID parentDatasetVersionId,
        String operation,
        String columnName,
        Integer rowsAffected,
        String details,
        LocalDateTime createdAt,
        List<Map<String, Object>> operationConfig
) {
    public DatasetLineageResponse(UUID datasetVersionId, UUID parentDatasetVersionId,
                                  String operation, String columnName, Integer rowsAffected,
                                  String details, LocalDateTime createdAt) {
        this(datasetVersionId, parentDatasetVersionId, operation, columnName,
                rowsAffected, details, createdAt, List.of());
    }
    /** @deprecated Use datasetVersionId. */
    @Deprecated
    @JsonProperty("datasetId")
    public UUID getDatasetId() { return datasetVersionId; }

    /** @deprecated Use datasetVersionId. */
    @Deprecated
    public UUID datasetId() { return datasetVersionId; }

    /** @deprecated Use parentDatasetVersionId. */
    @Deprecated
    @JsonProperty("parentDatasetId")
    public UUID getParentDatasetId() { return parentDatasetVersionId; }

    /** @deprecated Use parentDatasetVersionId. */
    @Deprecated
    public UUID parentDatasetId() { return parentDatasetVersionId; }
}
