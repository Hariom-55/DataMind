package com.datamind.datamind_api.analysis.service;

import com.datamind.datamind_api.analysis.entity.AnalysisJob;
import com.datamind.datamind_api.analysis.entity.AnalysisResult;
import com.datamind.datamind_api.analysis.entity.enums.AnalysisJobStatus;
import com.datamind.datamind_api.analysis.entity.enums.AnalysisType;
import com.datamind.datamind_api.analysis.exception.AnalysisResultNotFoundException;
import com.datamind.datamind_api.analysis.repository.AnalysisResultRepository;
import com.datamind.datamind_api.dataset.entity.Dataset;
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
class AnalysisResultServiceTest {

    @Mock
    private AnalysisResultRepository analysisResultRepository;

    @InjectMocks
    private AnalysisResultService analysisResultService;

    @Test
    void shouldSaveAnalysisResult() {

        Dataset dataset = mock(Dataset.class);

        AnalysisJob job = new AnalysisJob(
                dataset,
                AnalysisType.EDA,
                AnalysisJobStatus.PROCESSING
        );

        Map<String, Object> resultData = Map.of(
                "rowCount", 100,
                "columnCount", 5
        );

        AnalysisResult savedResult = mock(AnalysisResult.class);

        when(analysisResultRepository.save(any(AnalysisResult.class)))
                .thenReturn(savedResult);

        AnalysisResult result =
                analysisResultService.saveResult(
                        job,
                        resultData
                );

        assertSame(savedResult, result);

        verify(analysisResultRepository)
                .save(any(AnalysisResult.class));
    }

    @Test
    void shouldGetResultByJobId() {

        UUID jobId = UUID.randomUUID();

        AnalysisResult analysisResult =
                mock(AnalysisResult.class);

        when(analysisResultRepository.findByJobId(jobId))
                .thenReturn(Optional.of(analysisResult));

        AnalysisResult result =
                analysisResultService.getResultByJobId(jobId);

        assertSame(
                analysisResult,
                result
        );

        verify(analysisResultRepository)
                .findByJobId(jobId);
    }

    @Test
    void shouldThrowExceptionWhenResultNotFound() {

        UUID jobId = UUID.randomUUID();

        when(analysisResultRepository.findByJobId(jobId))
                .thenReturn(Optional.empty());

        assertThrows(
                AnalysisResultNotFoundException.class,
                () -> analysisResultService.getResultByJobId(jobId)
        );

        verify(analysisResultRepository)
                .findByJobId(jobId);
    }
}