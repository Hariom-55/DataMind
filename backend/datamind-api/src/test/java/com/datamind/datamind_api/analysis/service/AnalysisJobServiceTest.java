package com.datamind.datamind_api.analysis.service;

import com.datamind.datamind_api.analysis.entity.AnalysisJob;
import com.datamind.datamind_api.analysis.entity.enums.AnalysisJobStatus;
import com.datamind.datamind_api.analysis.entity.enums.AnalysisType;
import com.datamind.datamind_api.analysis.exception.AnalysisJobNotFoundException;
import com.datamind.datamind_api.analysis.repository.AnalysisJobRepository;
import com.datamind.datamind_api.dataset.entity.Dataset;
import com.datamind.datamind_api.dataset.service.DatasetService;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.mockito.Mock;
import org.mockito.MockitoAnnotations;

import java.time.Duration;
import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;
import java.util.UUID;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.anyString;
import static org.mockito.Mockito.*;

class AnalysisJobServiceTest {

    @Mock
    private AnalysisJobRepository analysisJobRepository;

    @Mock
    private DatasetService datasetService;

    private AnalysisJobService analysisJobService;

    @BeforeEach
    void setUp() {
        MockitoAnnotations.openMocks(this);
        analysisJobService = new AnalysisJobService(
                analysisJobRepository,
                datasetService,
                3,
                Duration.ofMinutes(30)
        );
    }

    @Test
    void shouldCreateAnalysisJob() {
        UUID datasetId = UUID.randomUUID();
        Dataset dataset = mock(Dataset.class);
        AnalysisJob savedJob = mock(AnalysisJob.class);

        when(dataset.getId()).thenReturn(datasetId);
        when(dataset.getLogicalDatasetId()).thenReturn(datasetId);
        when(datasetService.getDatasetById(datasetId)).thenReturn(dataset);
        when(analysisJobRepository.save(any(AnalysisJob.class))).thenReturn(savedJob);

        AnalysisJob result = analysisJobService.createAnalysisJob(
                datasetId, AnalysisType.EDA, null
        );

        assertSame(savedJob, result);
        verify(datasetService, atLeastOnce()).getDatasetById(datasetId);
        verify(analysisJobRepository).save(any(AnalysisJob.class));
    }

    @Test
    void shouldTrimTargetColumnWhenCreatingJob() {
        UUID datasetId = UUID.randomUUID();
        Dataset dataset = mock(Dataset.class);
        when(dataset.getId()).thenReturn(datasetId);
        when(dataset.getLogicalDatasetId()).thenReturn(datasetId);
        when(datasetService.getDatasetById(datasetId)).thenReturn(dataset);
        when(analysisJobRepository.save(any(AnalysisJob.class)))
                .thenAnswer(invocation -> invocation.getArgument(0));

        AnalysisJob result = analysisJobService.createAnalysisJob(
                datasetId, AnalysisType.MACHINE_LEARNING, "  profit  "
        );

        assertEquals("profit", result.getTargetColumn());
    }

    @Test
    void shouldPersistHyperparameterTuningOptIn() {
        UUID logicalId = UUID.randomUUID();
        UUID versionId = UUID.randomUUID();
        Dataset dataset = mock(Dataset.class);
        Dataset version = mock(Dataset.class);
        when(dataset.getId()).thenReturn(logicalId);
        when(dataset.getLogicalDatasetId()).thenReturn(logicalId);
        when(version.getId()).thenReturn(versionId);
        when(version.getLogicalDatasetId()).thenReturn(logicalId);
        when(datasetService.getDatasetById(logicalId)).thenReturn(dataset);
        when(datasetService.getDatasetById(versionId)).thenReturn(version);
        when(analysisJobRepository.save(any(AnalysisJob.class)))
                .thenAnswer(invocation -> invocation.getArgument(0));

        AnalysisJob result = analysisJobService.createAnalysisJob(
                logicalId,
                versionId,
                AnalysisType.MACHINE_LEARNING,
                "profit",
                true
        );

        assertTrue(result.isEnableHyperparameterTuning());
    }

    @Test
    void shouldCreateUnsupervisedMachineLearningJobWithoutTargetColumn() {
        UUID datasetId = UUID.randomUUID();
        Dataset dataset = mock(Dataset.class);
        when(datasetService.getDatasetById(datasetId)).thenReturn(dataset);
        when(dataset.getLogicalDatasetId()).thenReturn(datasetId);
        when(dataset.getId()).thenReturn(datasetId);
        when(datasetService.getCurrentVersion(datasetId)).thenReturn(dataset);
        when(analysisJobRepository.save(any(AnalysisJob.class)))
                .thenAnswer(invocation -> invocation.getArgument(0));

        AnalysisJob result = analysisJobService.createAnalysisJob(
                datasetId, AnalysisType.MACHINE_LEARNING, "  "
        );

        assertNull(result.getTargetColumn());
        verify(analysisJobRepository).save(any(AnalysisJob.class));
    }

    @Test
    void shouldRejectNullAnalysisType() {
        UUID datasetId = UUID.randomUUID();
        Dataset dataset = mock(Dataset.class);
        when(datasetService.getDatasetById(datasetId)).thenReturn(dataset);

        IllegalArgumentException exception = assertThrows(
                IllegalArgumentException.class,
                () -> analysisJobService.createAnalysisJob(datasetId, null, null)
        );

        assertEquals("analysisType is required", exception.getMessage());
        verify(analysisJobRepository, never()).save(any());
    }

    @Test
    void shouldRejectAnalysisTypesWithoutRegisteredImplementations() {
        UUID datasetId = UUID.randomUUID();
        IllegalArgumentException exception = assertThrows(
                IllegalArgumentException.class,
                () -> analysisJobService.createAnalysisJob(
                        datasetId, AnalysisType.TIME_SERIES, null
                )
        );

        assertEquals("Unsupported analysis type: TIME_SERIES", exception.getMessage());
        verifyNoInteractions(analysisJobRepository);
    }

    @Test
    void shouldGetAnalysisJobById() {
        UUID jobId = UUID.randomUUID();
        AnalysisJob job = mock(AnalysisJob.class);
        when(analysisJobRepository.findById(jobId)).thenReturn(Optional.of(job));

        assertSame(job, analysisJobService.getAnalysisJobById(jobId));
        verify(analysisJobRepository).findById(jobId);
    }

    @Test
    void shouldThrowExceptionWhenAnalysisJobNotFound() {
        UUID jobId = UUID.randomUUID();
        when(analysisJobRepository.findById(jobId)).thenReturn(Optional.empty());

        assertThrows(
                AnalysisJobNotFoundException.class,
                () -> analysisJobService.getAnalysisJobById(jobId)
        );
    }

    @Test
    void shouldClaimNextPendingJob() {
        AnalysisJob job = mock(AnalysisJob.class);
        Dataset version = mock(Dataset.class);
        when(job.getDatasetVersion()).thenReturn(version);
        when(analysisJobRepository.findNextPendingJob(AnalysisJobStatus.PENDING.name()))
                .thenReturn(Optional.of(job));

        Optional<AnalysisJob> result = analysisJobService.claimNextPendingJob();

        assertTrue(result.isPresent());
        assertSame(job, result.get());
        verify(job).markAsProcessing();
        verify(analysisJobRepository).save(job);
    }

    @Test
    void shouldReturnEmptyWhenNoPendingJobExists() {
        when(analysisJobRepository.findNextPendingJob(AnalysisJobStatus.PENDING.name()))
                .thenReturn(Optional.empty());

        assertTrue(analysisJobService.claimNextPendingJob().isEmpty());
        verify(analysisJobRepository, never()).save(any());
    }

    @Test
    void shouldCompleteJob() {
        UUID jobId = UUID.randomUUID();
        AnalysisJob job = mock(AnalysisJob.class);
        when(analysisJobRepository.findById(jobId)).thenReturn(Optional.of(job));

        analysisJobService.completeJob(jobId);

        verify(job).markAsCompleted();
        verify(analysisJobRepository).save(job);
    }

    @Test
    void shouldRetryFailedJobWhenRetryLimitNotReached() {
        UUID jobId = UUID.randomUUID();
        AnalysisJob job = mock(AnalysisJob.class);
        when(analysisJobRepository.findById(jobId)).thenReturn(Optional.of(job));
        when(job.getRetryCount()).thenReturn(1);

        analysisJobService.failJob(jobId, "Python analysis failed");

        verify(job).incrementRetryCount();
        verify(job).retry("Python analysis failed");
        verify(job, never()).markAsFailed(anyString());
        verify(analysisJobRepository).save(job);
    }

    @Test
    void shouldMarkJobAsFailedWhenRetryLimitReached() {
        UUID jobId = UUID.randomUUID();
        AnalysisJob job = mock(AnalysisJob.class);
        when(analysisJobRepository.findById(jobId)).thenReturn(Optional.of(job));
        when(job.getRetryCount()).thenReturn(3);

        analysisJobService.failJob(jobId, "Python analysis failed");

        verify(job).incrementRetryCount();
        verify(job).markAsFailed("Python analysis failed");
        verify(job, never()).retry(anyString());
        verify(analysisJobRepository).save(job);
    }

    @Test
    void shouldRecoverStaleJobs() {
        AnalysisJob staleJob = mock(AnalysisJob.class);
        when(staleJob.getRetryCount()).thenReturn(1);
        when(analysisJobRepository.findByStatusAndStartedAtBefore(
                eq(AnalysisJobStatus.PROCESSING), any(LocalDateTime.class)))
                .thenReturn(List.of(staleJob));

        int recovered = analysisJobService.recoverStaleJobs();

        assertEquals(1, recovered);
        verify(staleJob).incrementRetryCount();
        verify(staleJob).retry("Job was recovered after exceeding the processing timeout");
        verify(analysisJobRepository).saveAll(List.of(staleJob));
    }

    @Test
    void shouldFailStaleJobWhenRetryLimitIsReached() {
        AnalysisJob staleJob = mock(AnalysisJob.class);
        when(staleJob.getRetryCount()).thenReturn(3);
        when(analysisJobRepository.findByStatusAndStartedAtBefore(
                eq(AnalysisJobStatus.PROCESSING), any(LocalDateTime.class)))
                .thenReturn(List.of(staleJob));

        assertEquals(1, analysisJobService.recoverStaleJobs());

        verify(staleJob).incrementRetryCount();
        verify(staleJob).markAsFailed(
                "Job exceeded the maximum retry count after becoming stale"
        );
        verify(staleJob, never()).retry(anyString());
        verify(analysisJobRepository).saveAll(List.of(staleJob));
    }

    @Test
    void shouldCreateInsightAnalysisJob() {
        UUID datasetId = UUID.randomUUID();
        Dataset dataset = mock(Dataset.class);
        AnalysisJob savedJob = mock(AnalysisJob.class);

        when(dataset.getId()).thenReturn(datasetId);
        when(dataset.getLogicalDatasetId()).thenReturn(datasetId);
        when(datasetService.getDatasetById(datasetId)).thenReturn(dataset);
        when(analysisJobRepository.save(any(AnalysisJob.class))).thenReturn(savedJob);

        AnalysisJob result = analysisJobService.createAnalysisJob(
                datasetId, AnalysisType.INSIGHT, null
        );

        assertSame(savedJob, result);
        verify(analysisJobRepository).save(any(AnalysisJob.class));
    }

    @Test
    void shouldQueryAnalysisHistoryWithFiltersAndBoundedLimit() {
        UUID logicalId = UUID.randomUUID();
        UUID versionId = UUID.randomUUID();
        analysisJobService.getAnalysisHistory(
                logicalId, versionId, AnalysisType.EDA, AnalysisJobStatus.COMPLETED, 500
        );

        verify(analysisJobRepository).findHistory(
                eq(logicalId), eq(versionId), eq(AnalysisType.EDA),
                eq(AnalysisJobStatus.COMPLETED), argThat(pageable -> pageable.getPageSize() == 100)
        );
    }

    @Test
    void shouldPersistHypothesisTestConfigurationForStatisticalJobs() {
        UUID logicalId = UUID.randomUUID();
        UUID versionId = UUID.randomUUID();
        Dataset dataset = mock(Dataset.class);
        Dataset version = mock(Dataset.class);
        var testRequest = List.of(java.util.Map.<String, Object>of(
                "test", "ONE_SAMPLE_T_TEST", "column", "age", "referenceValue", 25.0,
                "alpha", 0.05
        ));
        when(dataset.getLogicalDatasetId()).thenReturn(logicalId);
        when(version.getLogicalDatasetId()).thenReturn(logicalId);
        when(datasetService.getDatasetById(logicalId)).thenReturn(dataset);
        when(datasetService.getDatasetById(versionId)).thenReturn(version);
        when(analysisJobRepository.save(any(AnalysisJob.class)))
                .thenAnswer(invocation -> invocation.getArgument(0));

        AnalysisJob job = analysisJobService.createAnalysisJob(
                logicalId, versionId, AnalysisType.STATISTICAL, null, false, testRequest
        );

        assertEquals(testRequest, job.getHypothesisTests());
    }
}
