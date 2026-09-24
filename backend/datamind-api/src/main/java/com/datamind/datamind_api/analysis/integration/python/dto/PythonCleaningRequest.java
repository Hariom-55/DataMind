package com.datamind.datamind_api.analysis.integration.python.dto;

import com.fasterxml.jackson.annotation.JsonProperty;

import java.util.List;
import java.util.UUID;

public record  PythonCleaningRequest (
        @JsonProperty("dataset_version_id")
        UUID datasetVersionId,
        @JsonProperty("dataset_path")
        String datasetPath,
        @JsonProperty("operations")
        List<PythonCleaningOperation> operations,
        @JsonProperty("extension")
        String extension
){
    
}
