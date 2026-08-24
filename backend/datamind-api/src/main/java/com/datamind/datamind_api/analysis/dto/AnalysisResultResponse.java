package com.datamind.datamind_api.analysis.dto;

import com.datamind.datamind_api.analysis.entity.AnalysisResult;

import java.time.LocalDateTime;
import java.util.Map;
import java.util.UUID;

public class AnalysisResultResponse
{
    private UUID id;
    private UUID jobId;
    private Map<String, Object> result;
    private LocalDateTime createdAt;

    public AnalysisResultResponse(AnalysisResult analysisResult)
    {
        this.id = analysisResult.getId();
        this.jobId = analysisResult.getJob().getId();
        this.result = analysisResult.getResultData();
        this.createdAt = analysisResult.getCreatedAt();
    }

    public UUID getId() {
        return id;
    }

    public UUID getJobId() {
        return jobId;
    }

    public Map<String, Object> getResult() {
        return result;
    }

    public LocalDateTime getCreatedAt() {
        return createdAt;
    }
}
