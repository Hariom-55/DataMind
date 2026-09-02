package com.datamind.datamind_api.analysis.worker;

import com.datamind.datamind_api.analysis.entity.AnalysisJob;
import com.datamind.datamind_api.analysis.entity.enums.AnalysisType;
import com.datamind.datamind_api.analysis.integration.python.PythonAnalysisClient;
import com.datamind.datamind_api.analysis.integration.python.PythonAnalysisException;
import com.datamind.datamind_api.analysis.integration.python.dto.PythonAnalysisResponse;
import com.datamind.datamind_api.analysis.service.AnalysisExecutionService;
import com.datamind.datamind_api.analysis.service.AnalysisJobService;
import com.datamind.datamind_api.dataset.entity.Dataset;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import java.util.HashMap;
import java.util.Map;
import java.util.Optional;
import java.util.UUID;

import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class AnalysisJobWorkerTest
{
    @Mock
    private AnalysisJobService analysisJobService;

    @Mock
    private PythonAnalysisClient pythonAnalysisClient;

    @Mock
    private AnalysisExecutionService analysisExecutionService;

    @Mock
    private AnalysisJob job;

    @Mock
    private PythonAnalysisResponse pythonResponse;

    @InjectMocks
    private AnalysisJobWorker analysisJobWorker;


    @Test
    void shouldDoNothingWhenNoPendingJobExists()
    {
        when(analysisJobService.claimNextPendingJob())
                .thenReturn(Optional.empty());

        analysisJobWorker.processPendingJob();

        verify(analysisJobService)
                .claimNextPendingJob();

        verifyNoInteractions(
                pythonAnalysisClient,
                analysisExecutionService
        );
    }


    @Test
    void shouldProcessJobSuccessfully()
    {
        UUID jobId = UUID.randomUUID();
        UUID datasetId = UUID.randomUUID();

        Dataset dataset = mock(Dataset.class);

        Map<String, Object> result = new HashMap<>();
        result.put("rows", 100);

        when(analysisJobService.claimNextPendingJob())
                .thenReturn(Optional.of(job));

        when(job.getId())
                .thenReturn(jobId);

        when(job.getDataset())
                .thenReturn(dataset);

        when(dataset.getId())
                .thenReturn(datasetId);

        when(job.getAnalysisType())
                .thenReturn(AnalysisType.EDA);

        when(dataset.getStoragePath())
                .thenReturn("./data/test.csv");

        when(dataset.getFileType())
                .thenReturn("text/csv");

        when(pythonAnalysisClient.analyze(
                jobId,
                datasetId,
                "EDA",
                "./data/test.csv",
                "text/csv"
        )).thenReturn(pythonResponse);

        when(pythonResponse.getStatus())
                .thenReturn("COMPLETED");

        when(pythonResponse.getError())
                .thenReturn(null);

        when(pythonResponse.getResult())
                .thenReturn(result);

        analysisJobWorker.processPendingJob();

        verify(pythonAnalysisClient)
                .analyze(
                        jobId,
                        datasetId,
                        "EDA",
                        "./data/test.csv",
                        "text/csv"
                );

        verify(analysisExecutionService)
                .completeJob(
                        jobId,
                        result
                );

        verify(analysisJobService, never())
                .failJob(any(), anyString());
    }


    @Test
    void shouldFailJobWhenPythonReturnsFailedResponse()
    {
        UUID jobId = UUID.randomUUID();
        UUID datasetId = UUID.randomUUID();

        Dataset dataset = mock(Dataset.class);

        when(analysisJobService.claimNextPendingJob())
                .thenReturn(Optional.of(job));

        when(job.getId())
                .thenReturn(jobId);

        when(job.getDataset())
                .thenReturn(dataset);

        when(dataset.getId())
                .thenReturn(datasetId);

        when(job.getAnalysisType())
                .thenReturn(AnalysisType.EDA);

        when(dataset.getStoragePath())
                .thenReturn("./data/test.csv");

        when(dataset.getFileType())
                .thenReturn("text/csv");

        when(pythonAnalysisClient.analyze(
                jobId,
                datasetId,
                "EDA",
                "./data/test.csv",
                "text/csv"
        )).thenReturn(pythonResponse);

        when(pythonResponse.getStatus())
                .thenReturn("FAILED");

        when(pythonResponse.getError())
                .thenReturn("Column parsing failed");

        analysisJobWorker.processPendingJob();

        verify(analysisJobService)
                .failJob(
                        jobId,
                        "Column parsing failed"
                );

        verify(analysisExecutionService, never())
                .completeJob(
                        any(UUID.class),
                        anyMap()
                );
    }


    @Test
    void shouldFailJobWhenPythonReturnsIncompleteResult()
    {
        UUID jobId = UUID.randomUUID();

        Dataset dataset = mock(Dataset.class);

        when(analysisJobService.claimNextPendingJob())
                .thenReturn(Optional.of(job));

        when(job.getId())
                .thenReturn(jobId);

        when(job.getDataset())
                .thenReturn(dataset);

        when(dataset.getId())
                .thenReturn(UUID.randomUUID());

        when(job.getAnalysisType())
                .thenReturn(AnalysisType.EDA);

        when(dataset.getStoragePath())
                .thenReturn("./data/test.csv");

        when(pythonAnalysisClient.analyze(
                any(),
                any(),
                anyString(),
                anyString(),
                any()
        )).thenReturn(pythonResponse);

        when(pythonResponse.getStatus())
                .thenReturn("COMPLETED");

        when(pythonResponse.getError())
                .thenReturn(null);

        when(pythonResponse.getResult())
                .thenReturn(null);

        analysisJobWorker.processPendingJob();

        verify(analysisJobService)
                .failJob(
                        jobId,
                        "Python Service did not return a completed result"
                );

        verify(analysisExecutionService, never())
                .completeJob(
                        any(UUID.class),
                        anyMap()
                );
    }


    @Test
    void shouldFailJobWhenPythonServiceThrowsException()
    {
        UUID jobId = UUID.randomUUID();

        Dataset dataset = mock(Dataset.class);

        when(analysisJobService.claimNextPendingJob())
                .thenReturn(Optional.of(job));

        when(job.getId())
                .thenReturn(jobId);

        when(job.getDataset())
                .thenReturn(dataset);

        when(dataset.getId())
                .thenReturn(UUID.randomUUID());

        when(job.getAnalysisType())
                .thenReturn(AnalysisType.EDA);

        when(dataset.getStoragePath())
                .thenReturn("./data/test.csv");

        PythonAnalysisException exception =
                new PythonAnalysisException(
                        "Python service unavailable"
                );

        when(pythonAnalysisClient.analyze(
                any(),
                any(),
                anyString(),
                anyString(),
                any()
        )).thenThrow(exception);

        analysisJobWorker.processPendingJob();

        verify(analysisJobService)
                .failJob(
                        jobId,
                        "Python service unavailable"
                );

        verify(analysisExecutionService, never())
                .completeJob(
                        any(UUID.class),
                        anyMap()
                );
    }
}