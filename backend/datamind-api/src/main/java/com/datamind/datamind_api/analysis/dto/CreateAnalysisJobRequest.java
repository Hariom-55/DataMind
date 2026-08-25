package com.datamind.datamind_api.analysis.dto;

import com.datamind.datamind_api.analysis.entity.enums.AnalysisType;
import jakarta.validation.constraints.NotNull;


import java.util.UUID;
public class CreateAnalysisJobRequest
{
    @NotNull
    private UUID datasetId;

    @NotNull
    private AnalysisType analysisType ;

    public CreateAnalysisJobRequest() {}

    public UUID getDatasetId() {
        return datasetId;
    }

    public AnalysisType getAnalysisType() {
        return analysisType;
    }

    public void setDatasetId(UUID datasetId) {
        this.datasetId = datasetId;
    }

    public void setAnalysisType(AnalysisType analysisType) {
        this.analysisType = analysisType;
    }
}
