package com.datamind.datamind_api.analysis.service;

import com.datamind.datamind_api.analysis.entity.AnalysisJob;
import com.datamind.datamind_api.analysis.entity.AnalysisResult;
import com.datamind.datamind_api.analysis.exception.AnalysisJobNotFoundException;
import com.datamind.datamind_api.analysis.repository.AnalysisJobRepository;
import com.datamind.datamind_api.analysis.repository.AnalysisResultRepository;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.Map;
import java.util.Optional;
import java.util.UUID;

@Service
public class AnalysisExecutionService
{
    private final AnalysisJobRepository analysisJobRepository;
    private final AnalysisResultService analysisResultService;

    public AnalysisExecutionService(
            AnalysisJobRepository analysisJobRepository,
            AnalysisResultService analysisResultService
    ){
        this.analysisJobRepository = analysisJobRepository;
        this.analysisResultService = analysisResultService;
    }

    @Transactional
    public void completeJob(
            UUID jobId,
            Map<String, Object> resultData
    ){
        AnalysisJob job = analysisJobRepository
                .findById(jobId)
                .orElseThrow(
                        () -> new AnalysisJobNotFoundException(
                                "Analysis job not found: " + jobId
                        )
                );

        analysisResultService.saveResult(job, resultData);
        job.markAsCompleted();
        analysisJobRepository.save(job);
    }
}
