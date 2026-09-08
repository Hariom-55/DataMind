package com.datamind.datamind_api.analysis.integration.python.dto;

import com.fasterxml.jackson.annotation.JsonProperty;

import java.util.List;
import java.util.UUID;

public record  PythonCleaningRequest (
        @JsonProperty("dataset_id")
        UUID datasetId,
        @JsonProperty("dataset_path")
        String datasetPath,
        @JsonProperty("operations")
        List<PythonCleaningOperation> operations,
        @JsonProperty("extension")
        String extension
){
    
}
