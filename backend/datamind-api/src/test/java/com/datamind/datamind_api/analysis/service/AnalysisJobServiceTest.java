package com.datamind.datamind_api.analysis.service;

import com.datamind.datamind_api.analysis.entity.AnalysisJob;
import com.datamind.datamind_api.analysis.entity.enums.AnalysisJobStatus;
import com.datamind.datamind_api.analysis.entity.enums.AnalysisType;
import com.datamind.datamind_api.analysis.exception.AnalysisJobNotFoundException;
import com.datamind.datamind_api.analysis.repository.AnalysisJobRepository;
import com.datamind.datamind_api.dataset.entity.Dataset;
import com.datamind.datamind_api.dataset.service.DatasetService;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;


import java.util.Optional;
import java.util.UUID;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
public class AnalysisJobServiceTest {

    @Mock
    private AnalysisJobRepository analysisJobRepository;

    @Mock
    private DatasetService datasetService;

    @InjectMocks
    private AnalysisJobService analysisJobService;

    @Test
    void shouldCreateAnalysisJob()
    {
        UUID datasetId = UUID.randomUUID();

        Dataset dataset = mock(Dataset.class);

        when(datasetService.getDatasetById(datasetId))
                .thenReturn(dataset);

        AnalysisJob savedJob = mock(AnalysisJob.class);

        when(analysisJobRepository.save(any(AnalysisJob.class)))
                .thenReturn(savedJob);

        AnalysisJob result = analysisJobService.createAnalysisJob(
                datasetId,
                AnalysisType.EDA,
                null
        );

        assertNotNull(result);
        assertSame(savedJob, result);

        verify(datasetService)
                .getDatasetById(datasetId);

        verify(analysisJobRepository)
                .save(any(AnalysisJob.class));
    }

    @Test
    void shouldGetAnalysisJobById()
    {
        UUID jobId = UUID.randomUUID();

        AnalysisJob job = mock(AnalysisJob.class);

        when(analysisJobRepository.findById(jobId))
                .thenReturn(Optional.of(job));

        AnalysisJob result = analysisJobService.getAnalysisJobById(jobId);

        assertSame(job,result);

        verify(analysisJobRepository)
                .findById(jobId);
    }

    @Test
    void shouldThrowExceptionWhenAnalysisJobNotFound()
    {
        UUID jobId = UUID.randomUUID();

        when(analysisJobRepository.findById(jobId))
                .thenReturn(Optional.empty());

        assertThrows(
                AnalysisJobNotFoundException.class,
                () -> analysisJobService.getAnalysisJobById(jobId)
        );

        verify(analysisJobRepository)
                .findById(jobId);
    }

    @Test
    void shouldClaimNextPendingJob()
    {
        AnalysisJob job = mock(AnalysisJob.class);

        when(analysisJobRepository.findNextPendingJob(
                AnalysisJobStatus.PENDING.name()
        ))
                .thenReturn(Optional.of(job));

        Optional<AnalysisJob> result =
                analysisJobService.claimNextPendingJob();

        assertTrue(result.isPresent());
        assertSame(job, result.get());

        verify(analysisJobRepository)
                .findNextPendingJob(AnalysisJobStatus.PENDING.name());

        verify(job)
                .markAsProcessing();

        verify(analysisJobRepository)
                .save(job);
    }

    @Test
    void shouldReturnEmptyWhenNoPendingJobExists()
    {
        when(analysisJobRepository.findNextPendingJob(
                AnalysisJobStatus.PENDING.name()
        )).thenReturn(Optional.empty());

        Optional<AnalysisJob> result =
                analysisJobService.claimNextPendingJob();

        assertTrue(result.isEmpty());

        verify(analysisJobRepository)
                .findNextPendingJob(AnalysisJobStatus.PENDING.name());

        verify(analysisJobRepository, never())
                .save(any());
    }

    @Test
    void shouldCompleteJob()
    {
        UUID jobId = UUID.randomUUID();
        AnalysisJob job = mock(AnalysisJob.class);

        when(analysisJobRepository.findById(jobId))
                .thenReturn(Optional.of(job));

        analysisJobService.completeJob(jobId);

        verify(job)
                .markAsCompleted();

        verify(analysisJobRepository)
                .save(job);
    }

    @Test
    void shouldRetryFailedJobWhenRetryLimitNotReached()
    {
        UUID jobId = UUID.randomUUID();

        AnalysisJob job = mock(AnalysisJob.class);

        when(analysisJobRepository.findById(jobId))
                .thenReturn(Optional.of(job));

        when(job.getRetryCount())
                .thenReturn(1);

        analysisJobService.failJob(
                jobId,
                "Python analysis failed"
        );

        verify(job)
                .incrementRetryCount();

        verify(job)
                .retry();

        verify(job ,never())
                .markAsFailed(anyString());

        verify(analysisJobRepository)
                .save(job);
    }

    @Test
    void shouldMarkJobAsFailedWhenRetryLimitReached()
    {
        UUID jobId = UUID.randomUUID();

        AnalysisJob job = mock(AnalysisJob.class);

        when(analysisJobRepository.findById(jobId))
                .thenReturn(Optional.of(job));

        when(job.getRetryCount())
                .thenReturn(3);

        String errorMessage = "Python analysis failed";

        analysisJobService.failJob(
                jobId,
                errorMessage
        );

        verify(job)
                .incrementRetryCount();

        verify(job)
                .markAsFailed(errorMessage);

        verify(job, never())
                .retry();

        verify(analysisJobRepository)
                .save(job);
    }
}
