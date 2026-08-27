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
}