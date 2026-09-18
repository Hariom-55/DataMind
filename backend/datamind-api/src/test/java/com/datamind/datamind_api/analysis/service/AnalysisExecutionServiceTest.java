package com.datamind.datamind_api.analysis.service;

import com.datamind.datamind_api.analysis.entity.AnalysisJob;
import com.datamind.datamind_api.analysis.entity.AnalysisResult;
import com.datamind.datamind_api.analysis.exception.AnalysisJobNotFoundException;
import com.datamind.datamind_api.analysis.repository.AnalysisJobRepository;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import java.util.Map;
import java.util.Optional;
import java.util.UUID;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class AnalysisExecutionServiceTest {

    @Mock
    private AnalysisJobRepository analysisJobRepository;

    @Mock
    private AnalysisResultService analysisResultService;

    @InjectMocks
    private AnalysisExecutionService analysisExecutionService;

    @Test
    void shouldCompleteJobAndSaveResult() {

        UUID jobId = UUID.randomUUID();

        AnalysisJob job = mock(AnalysisJob.class);

        Map<String, Object> resultData = Map.of(
                "rowCount", 100,
                "columnCount", 5
        );

        AnalysisResult savedResult = mock(AnalysisResult.class);

        when(analysisJobRepository.findById(jobId))
                .thenReturn(Optional.of(job));

        when(analysisResultService.saveResult(job, resultData))
                .thenReturn(savedResult);

        analysisExecutionService.completeJob(
                jobId,
                resultData
        );

        verify(analysisJobRepository)
                .findById(jobId);

        verify(analysisResultService)
                .saveResult(job, resultData);

        verify(job)
                .markAsCompleted();

        verify(analysisJobRepository)
                .save(job);
    }

    @Test
    void shouldThrowExceptionWhenJobNotFound() {

        UUID jobId = UUID.randomUUID();

        Map<String, Object> resultData = Map.of(
                "rowCount", 100
        );

        when(analysisJobRepository.findById(jobId))
                .thenReturn(Optional.empty());

        assertThrows(
                AnalysisJobNotFoundException.class,
                () -> analysisExecutionService.completeJob(
                        jobId,
                        resultData
                )
        );

        verify(analysisJobRepository)
                .findById(jobId);

        verifyNoInteractions(analysisResultService);

        verify(analysisJobRepository, never())
                .save(any(AnalysisJob.class));
    }

    @Test
    void shouldCompleteInsightJobAndSaveNestedInsightResult()
    {
        UUID jobId = UUID.randomUUID();

        AnalysisJob job = mock(AnalysisJob.class);

        Map<String, Object> summary = Map.of(
                "totalInsights", 2,
                "high", 1,
                "medium", 1,
                "low", 0,
                "info", 0
        );

        Map<String, Object> insight = Map.of(
                "id", "INSIGHT-001",
                "category", "DATA_QUALITY",
                "severity", "HIGH",
                "source", "EDA",
                "title", "High missing-value rate"
        );

        Map<String, Object> insightData = Map.of(
                "summary", summary,
                "insights", java.util.List.of(insight)
        );

        Map<String, Object> resultData = Map.of(
                "analysis", Map.of(),
                "insights", insightData
        );

        AnalysisResult savedResult = mock(AnalysisResult.class);

        when(analysisJobRepository.findById(jobId))
                .thenReturn(Optional.of(job));

        when(analysisResultService.saveResult(job, resultData))
                .thenReturn(savedResult);

        analysisExecutionService.completeJob(
                jobId,
                resultData
        );

        verify(analysisJobRepository)
                .findById(jobId);

        verify(analysisResultService)
                .saveResult(job, resultData);

        verify(job)
                .markAsCompleted();

        verify(analysisJobRepository)
                .save(job);
    }
}