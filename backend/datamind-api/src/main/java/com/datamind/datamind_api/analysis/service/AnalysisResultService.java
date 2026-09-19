package com.datamind.datamind_api.analysis.service;

import com.datamind.datamind_api.analysis.entity.AnalysisJob;
import com.datamind.datamind_api.analysis.entity.AnalysisResult;
import com.datamind.datamind_api.analysis.exception.AnalysisResultNotFoundException;
import com.datamind.datamind_api.analysis.repository.AnalysisResultRepository;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.Map;
import java.util.UUID;

@Service
public class AnalysisResultService {
    private final AnalysisResultRepository analysisResultRepository;

    public AnalysisResultService(AnalysisResultRepository analysisResultRepository) {
        this.analysisResultRepository = analysisResultRepository;
    }

    @Transactional
    public AnalysisResult saveResult(AnalysisJob job, Map<String, Object> resultData) {
        if (resultData == null) {
            throw new IllegalArgumentException("Analysis result data is required");
        }

        return analysisResultRepository.findByJobId(job.getId())
                .orElseGet(() -> analysisResultRepository.save(new AnalysisResult(job, resultData)));
    }

    public AnalysisResult getResultByJobId(UUID jobId) {
        return analysisResultRepository.findByJobId(jobId)
                .orElseThrow(() -> new AnalysisResultNotFoundException(
                        "Analysis result not found for job: " + jobId
                ));
    }
}
