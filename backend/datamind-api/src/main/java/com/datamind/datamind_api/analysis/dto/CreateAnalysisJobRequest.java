package com.datamind.datamind_api.analysis.dto;

import com.datamind.datamind_api.analysis.entity.enums.AnalysisType;

import java.util.UUID;
public class AnalysisJobCreateRequest
{
    private UUID datasetId;
    private AnalysisType analysisType ;

    public  AnalysisJobCreateRequest() {}

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
