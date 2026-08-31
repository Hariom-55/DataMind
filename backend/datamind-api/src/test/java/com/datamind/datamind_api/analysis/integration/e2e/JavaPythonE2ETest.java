package com.datamind.datamind_api.analysis.integration.e2e;

import com.datamind.datamind_api.analysis.entity.AnalysisJob;
import com.datamind.datamind_api.analysis.entity.AnalysisResult;
import com.datamind.datamind_api.analysis.entity.enums.AnalysisJobStatus;
import com.datamind.datamind_api.analysis.entity.enums.AnalysisType;
import com.datamind.datamind_api.analysis.repository.AnalysisJobRepository;
import com.datamind.datamind_api.analysis.repository.AnalysisResultRepository;
import com.datamind.datamind_api.analysis.worker.AnalysisJobWorker;
import com.datamind.datamind_api.dataset.entity.Dataset;
import com.datamind.datamind_api.dataset.repository.DatasetRepository;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.transaction.annotation.Transactional;

import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Map;
import java.util.UUID;

import static org.junit.jupiter.api.Assertions.*;

@SpringBootTest(
        properties = {
                "spring.task.scheduling.enabled=false"
        }
)
@Transactional
class JavaPythonE2ETest
{
    @Autowired
    private DatasetRepository datasetRepository;

    @Autowired
    private AnalysisJobRepository analysisJobRepository;

    @Autowired
    private AnalysisResultRepository analysisResultRepository;

    @Autowired
    private AnalysisJobWorker analysisJobWorker;


    @Test
    void shouldCompleteAnalysisJobThroughPythonEda()
            throws Exception
    {
        // Arrange
        Path datasetPath = Files.createTempFile(
                "datamind-e2e-",
                ".csv"
        );

        try
        {
            Files.writeString(
                    datasetPath,
                    """
                    name,age,city
                    Hariom,21,Delhi
                    Rahul,22,Mumbai
                    Aman,20,Delhi
                    """
            );

            Dataset dataset = new Dataset(
                    "e2e-test.csv",
                    "e2e-" + UUID.randomUUID(),
                    Files.size(datasetPath),
                    "text/csv"
            );

            dataset.setStoragePath(
                    datasetPath.toAbsolutePath().toString()
            );

            dataset = datasetRepository.saveAndFlush(dataset);

            AnalysisJob job = new AnalysisJob(
                    dataset,
                    AnalysisType.EDA,
                    AnalysisJobStatus.PENDING
            );

            job = analysisJobRepository.saveAndFlush(job);

            UUID jobId = job.getId();

            // Act
            analysisJobWorker.processPendingJob();

            // Assert
            AnalysisJob completedJob =
                    analysisJobRepository
                            .findById(jobId)
                            .orElseThrow();

            assertEquals(
                    AnalysisJobStatus.COMPLETED,
                    completedJob.getStatus()
            );

            AnalysisResult result =
                    analysisResultRepository
                            .findByJobId(jobId)
                            .orElseThrow();

            assertNotNull(result);
            assertNotNull(result.getResultData());

            Map<String, Object> resultData =
                    result.getResultData();

            assertNotNull(
                    resultData.get("overview")
            );
        }
        finally
        {
            Files.deleteIfExists(datasetPath);
        }
    }

    @Test
    void shouldRetryAnalysisJobWhenPythonCannotFindDataset()
    {
        // Arrange
        Dataset dataset = new Dataset(
                "missing-dataset.csv",
                "e2e-missing-" + UUID.randomUUID(),
                100L,
                "text/csv"
        );

        dataset.setStoragePath(
                Path.of(
                        System.getProperty("java.io.tmpdir"),
                        "datamind-e2e-missing-" + UUID.randomUUID() + ".csv"
                ).toString()
        );

        dataset = datasetRepository.saveAndFlush(dataset);

        AnalysisJob job = new AnalysisJob(
                dataset,
                AnalysisType.EDA,
                AnalysisJobStatus.PENDING
        );

        job = analysisJobRepository.saveAndFlush(job);

        UUID jobId = job.getId();

        // Act
        analysisJobWorker.processPendingJob();

        // Assert
        AnalysisJob retriedJob =
                analysisJobRepository
                        .findById(jobId)
                        .orElseThrow();

        assertEquals(
                AnalysisJobStatus.PENDING,
                retriedJob.getStatus()
        );

        assertEquals(
                1,
                retriedJob.getRetryCount()
        );

        assertNull(
                retriedJob.getErrorMessage()
        );

        assertNull(
                retriedJob.getStartedAt()
        );

        assertNull(
                retriedJob.getCompletedAt()
        );

        assertTrue(
                analysisResultRepository
                        .findByJobId(jobId)
                        .isEmpty()
        );
    }

    @Test
    void shouldMarkAnalysisJobFailedAfterMaximumRetries()
    {
        // Arrange
        Dataset dataset = new Dataset(
                "missing-dataset.csv",
                "e2e-max-retry-" + UUID.randomUUID(),
                100L,
                "text/csv"
        );

        Path missingDatasetPath = Path.of(
                System.getProperty("java.io.tmpdir"),
                "datamind-e2e-missing-" + UUID.randomUUID() + ".csv"
        );

        dataset.setStoragePath(
                missingDatasetPath.toAbsolutePath().toString()
        );

        dataset = datasetRepository.saveAndFlush(dataset);

        AnalysisJob job = new AnalysisJob(
                dataset,
                AnalysisType.EDA,
                AnalysisJobStatus.PENDING
        );

        job = analysisJobRepository.saveAndFlush(job);

        UUID jobId = job.getId();

        // Act + Assert — Attempt 1
        analysisJobWorker.processPendingJob();

        AnalysisJob afterFirstAttempt =
                analysisJobRepository.findById(jobId).orElseThrow();

        assertEquals(
                AnalysisJobStatus.PENDING,
                afterFirstAttempt.getStatus()
        );

        assertEquals(
                1,
                afterFirstAttempt.getRetryCount()
        );

        // Act + Assert — Attempt 2
        analysisJobWorker.processPendingJob();

        AnalysisJob afterSecondAttempt =
                analysisJobRepository.findById(jobId).orElseThrow();

        assertEquals(
                AnalysisJobStatus.PENDING,
                afterSecondAttempt.getStatus()
        );

        assertEquals(
                2,
                afterSecondAttempt.getRetryCount()
        );

        // Act + Assert — Attempt 3
        analysisJobWorker.processPendingJob();

        AnalysisJob afterThirdAttempt =
                analysisJobRepository.findById(jobId).orElseThrow();

        assertEquals(
                AnalysisJobStatus.FAILED,
                afterThirdAttempt.getStatus()
        );

        assertEquals(
                3,
                afterThirdAttempt.getRetryCount()
        );

        assertNotNull(
                afterThirdAttempt.getErrorMessage()
        );

        assertNotNull(
                afterThirdAttempt.getCompletedAt()
        );

        assertNull(
                afterThirdAttempt.getStartedAt()
        );

        assertTrue(
                analysisResultRepository
                        .findByJobId(jobId)
                        .isEmpty()
        );
    }

    @Test
    void shouldCompleteStatisticalAnalysisJobThroughPython()
    {
        Dataset dataset = new Dataset(
                "statistical-e2e.csv",
                "e2e-statistical-" + UUID.randomUUID(),
                0L,
                "text/csv"
        );

        Path datasetPath;

        try
        {
            datasetPath = Files.createTempFile(
                    "datamind-statistical-e2e-",
                    ".csv"
            );

            Files.writeString(
                    datasetPath,
                    """
                    age,salary
                    20,20000
                    30,30000
                    40,40000
                    50,50000
                    60,60000
                    """
            );

            dataset.setStoragePath(
                    datasetPath.toAbsolutePath().toString()
            );

            dataset = datasetRepository.saveAndFlush(dataset);

            AnalysisJob job = new AnalysisJob(
                    dataset,
                    AnalysisType.STATISTICAL,
                    AnalysisJobStatus.PENDING
            );

            job = analysisJobRepository.saveAndFlush(job);

            UUID jobId = job.getId();

            // Act
            analysisJobWorker.processPendingJob();

            // Assert
            AnalysisJob completedJob =
                    analysisJobRepository
                            .findById(jobId)
                            .orElseThrow();

            assertEquals(
                    AnalysisJobStatus.COMPLETED,
                    completedJob.getStatus()
            );

            AnalysisResult result =
                    analysisResultRepository
                            .findByJobId(jobId)
                            .orElseThrow();

            assertNotNull(result);
            assertNotNull(result.getResultData());

            Map<String, Object> resultData =
                    result.getResultData();

            assertTrue(
                    resultData.containsKey("descriptiveStatistics")
            );

            assertTrue(
                    resultData.containsKey("correlations")
            );

            Map<String, Object> descriptiveStatistics =
                    (Map<String, Object>)
                            resultData.get("descriptiveStatistics");

            assertTrue(
                    descriptiveStatistics.containsKey("age")
            );

            assertTrue(
                    descriptiveStatistics.containsKey("salary")
            );

            Map<String, Object> ageStatistics =
                    (Map<String, Object>)
                            descriptiveStatistics.get("age");

            assertEquals(
                    5,
                    ((Number) ageStatistics.get("count")).intValue()
            );

            assertEquals(
                    40.0,
                    ((Number) ageStatistics.get("mean")).doubleValue(),
                    0.001
            );

            Map<String, Object> correlations =
                    (Map<String, Object>)
                            resultData.get("correlations");

            assertTrue(
                    correlations.containsKey("pearson")
            );

            assertTrue(
                    correlations.containsKey("spearman")
            );

            Map<String, Object> pearson =
                    (Map<String, Object>)
                            correlations.get("pearson");

            Map<String, Object> agePearson =
                    (Map<String, Object>)
                            pearson.get("age");

            assertEquals(
                    1.0,
                    ((Number) agePearson.get("salary")).doubleValue(),
                    0.001
            );
        }
        catch (Exception exception)
        {
            throw new RuntimeException(exception);
        }

    }

    @Test
void shouldRetryStatisticalAnalysisJobWhenPythonCannotFindDataset()
{
    // Arrange
    Dataset dataset = new Dataset(
            "missing-statistical-dataset.csv",
            "e2e-statistical-missing-" + UUID.randomUUID(),
            100L,
            "text/csv"
    );

    dataset.setStoragePath(
            Path.of(
                    System.getProperty("java.io.tmpdir"),
                    "datamind-statistical-missing-" +
                            UUID.randomUUID() +
                            ".csv"
            ).toString()
    );

    dataset = datasetRepository.saveAndFlush(dataset);

    AnalysisJob job = new AnalysisJob(
            dataset,
            AnalysisType.STATISTICAL,
            AnalysisJobStatus.PENDING
    );

    job = analysisJobRepository.saveAndFlush(job);

    UUID jobId = job.getId();

    // Act
    analysisJobWorker.processPendingJob();

    // Assert
    AnalysisJob retriedJob =
            analysisJobRepository
                    .findById(jobId)
                    .orElseThrow();

    assertEquals(
            AnalysisJobStatus.PENDING,
            retriedJob.getStatus()
    );

    assertEquals(
            1,
            retriedJob.getRetryCount()
    );

    assertNull(
            retriedJob.getErrorMessage()
    );

    assertNull(
            retriedJob.getStartedAt()
    );

    assertNull(
            retriedJob.getCompletedAt()
    );

    assertTrue(
            analysisResultRepository
                    .findByJobId(jobId)
                    .isEmpty()
    );
}
}