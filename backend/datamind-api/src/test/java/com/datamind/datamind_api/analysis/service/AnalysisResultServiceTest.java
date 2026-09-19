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

        UUID jobId = job.getId();

        Map<String, Object> resultData = Map.of(
                "rowCount", 100,
                "columnCount",
                5
        );

        AnalysisResult savedResult = mock(AnalysisResult.class);

        when(analysisResultRepository.findByJobId(jobId))
                .thenReturn(Optional.empty());

        when(analysisResultRepository.save(any(AnalysisResult.class)))
                .thenReturn(savedResult);

        assertSame(savedResult, analysisResultService.saveResult(job, resultData));

        verify(analysisResultRepository)
                .findByJobId(jobId);

        verify(analysisResultRepository)
                .save(any(AnalysisResult.class));
    }

    @Test
    void shouldReturnExistingResultInsteadOfCreatingDuplicate() {
        Dataset dataset = mock(Dataset.class);

        AnalysisJob job = mock(AnalysisJob.class);

        UUID jobId = UUID.randomUUID();

        AnalysisResult existingResult = mock(AnalysisResult.class);

        when(job.getId())
                .thenReturn(jobId);

        when(analysisResultRepository.findByJobId(jobId))
                .thenReturn(Optional.of(existingResult));

        assertSame(existingResult,
                analysisResultService.saveResult(
                        job,
                        Map.of("rows",
                                100)
                )
        );

        verify(analysisResultRepository, never()).save(any(AnalysisResult.class));
    }

    



    @Test
    void shouldGetResultByJobId() {
        UUID jobId = UUID.randomUUID();

        AnalysisResult analysisResult = mock(AnalysisResult.class);

        when(analysisResultRepository.findByJobId(jobId))
                .thenReturn(Optional.of(analysisResult));

        assertSame(analysisResult, analysisResultService.getResultByJobId(jobId));

        verify(analysisResultRepository).findByJobId(jobId);
    }

    @Test
    void shouldThrowExceptionWhenResultNotFound() {
        UUID jobId = UUID.randomUUID();
        when(analysisResultRepository.findByJobId(jobId)).thenReturn(Optional.empty());

        assertThrows(
                AnalysisResultNotFoundException.class,
                () -> analysisResultService.getResultByJobId(jobId)
        );
    }
}
