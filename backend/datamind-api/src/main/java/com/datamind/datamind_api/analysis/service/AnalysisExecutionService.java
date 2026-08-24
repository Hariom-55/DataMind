package com.datamind.datamind_api.analysis.service;

import com.datamind.datamind_api.analysis.entity.AnalysisJob;
import com.datamind.datamind_api.analysis.entity.AnalysisResult;
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
    private final AnalysisResultRepository analysisResultRepository;

    public AnalysisExecutionService(
            AnalysisJobRepository analysisJobRepository,
            AnalysisResultRepository analysisResultRepository
    ){
        this.analysisJobRepository = analysisJobRepository;
        this.analysisResultRepository = analysisResultRepository;
    }

    @Transactional
    public void completeJob(
            UUID jobId,
            Map<String, Object> resultData
    ){
        AnalysisJob job = analysisJobRepository
                .findById(jobId)
                .orElseThrow(
                        () -> new RuntimeException(
                                "Analysis job not found: " + jobId
                        )
                );

        AnalysisResult result = new AnalysisResult(job, resultData);

        analysisResultRepository.save(result);
        job.markAsCompleted();

        analysisJobRepository.save(job);
    }
}
