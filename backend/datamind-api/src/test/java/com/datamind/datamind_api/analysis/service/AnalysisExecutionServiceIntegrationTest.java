package com.datamind.datamind_api.analysis.service;

import com.datamind.datamind_api.analysis.entity.AnalysisJob;
import com.datamind.datamind_api.analysis.entity.AnalysisResult;
import com.datamind.datamind_api.analysis.entity.enums.AnalysisJobStatus;
import com.datamind.datamind_api.analysis.entity.enums.AnalysisType;
import com.datamind.datamind_api.analysis.repository.AnalysisJobRepository;
import com.datamind.datamind_api.analysis.repository.AnalysisResultRepository;
import com.datamind.datamind_api.dataset.entity.Dataset;
import com.datamind.datamind_api.dataset.repository.DatasetRepository;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;

import java.util.HashMap;
import java.util.Map;

import static org.junit.jupiter.api.Assertions.*;

@SpringBootTest
class AnalysisExecutionServiceIntegrationTest {

    @Autowired
    private AnalysisExecutionService analysisExecutionService;

    @Autowired
    private AnalysisJobRepository analysisJobRepository;

    @Autowired
    private AnalysisResultRepository analysisResultRepository;

    @Autowired
    private DatasetRepository datasetRepository;


    @BeforeEach
    void setUp() {
        cleanDatabase();
    }


    @AfterEach
    void tearDown() {
        cleanDatabase();
    }


    @Test
    void shouldSaveResultAndCompleteJob() {

        Dataset dataset = createDataset();

        AnalysisJob job = new AnalysisJob(
                dataset,
                AnalysisType.EDA,
                AnalysisJobStatus.PROCESSING
        );

        job = analysisJobRepository.save(job);

        Map<String, Object> resultData = new HashMap<>();

        resultData.put("rowCount", 100);
        resultData.put("columnCount", 5);
        resultData.put("duplicateRows", 2);

        analysisExecutionService.completeJob(
                job.getId(),
                resultData
        );

        AnalysisJob savedJob =
                analysisJobRepository
                        .findById(job.getId())
                        .orElseThrow();

        AnalysisResult savedResult =
                analysisResultRepository
                        .findByJobId(job.getId())
                        .orElseThrow();

        assertEquals(
                AnalysisJobStatus.COMPLETED,
                savedJob.getStatus()
        );

        assertNotNull(
                savedJob.getCompletedAt()
        );

        assertNull(
                savedJob.getErrorMessage()
        );

        assertEquals(
                job.getId(),
                savedResult.getJob().getId()
        );

        assertEquals(
                100,
                savedResult.getResultData().get("rowCount")
        );

        assertEquals(
                5,
                savedResult.getResultData().get("columnCount")
        );

        assertEquals(
                2,
                savedResult.getResultData().get("duplicateRows")
        );
    }


    @Test
    void shouldPersistCompleteAnalysisResultAsJson() {

        Dataset dataset = createDataset();

        AnalysisJob job = new AnalysisJob(
                dataset,
                AnalysisType.STATISTICAL,
                AnalysisJobStatus.PROCESSING
        );

        job = analysisJobRepository.save(job);

        Map<String, Object> resultData = new HashMap<>();

        Map<String, Object> ageStatistics = new HashMap<>();

        ageStatistics.put("count", 5);
        ageStatistics.put("mean", 30.5);
        ageStatistics.put("median", 30.0);

        resultData.put(
                "descriptiveStatistics",
                Map.of(
                        "age",
                        ageStatistics
                )
        );

        resultData.put(
                "correlations",
                Map.of(
                        "pearson",
                        Map.of(
                                "age",
                                Map.of("age", 1.0)
                        )
                )
        );

        analysisExecutionService.completeJob(
                job.getId(),
                resultData
        );

        AnalysisResult savedResult =
                analysisResultRepository
                        .findByJobId(job.getId())
                        .orElseThrow();

        assertNotNull(savedResult.getResultData());

        Map<String, Object> descriptiveStatistics =
                (Map<String, Object>)
                        savedResult.getResultData()
                                .get("descriptiveStatistics");

        assertNotNull(descriptiveStatistics);

        Map<String, Object> savedAgeStatistics =
                (Map<String, Object>)
                        descriptiveStatistics.get("age");

        assertEquals(
                5,
                savedAgeStatistics.get("count")
        );

        assertEquals(
                30.5,
                ((Number) savedAgeStatistics.get("mean"))
                        .doubleValue()
        );
    }


    @Test
    void shouldThrowExceptionWhenJobDoesNotExist() {

        var jobId = java.util.UUID.randomUUID();

        Map<String, Object> resultData =
                Map.of(
                        "rowCount",
                        100
                );

        assertThrows(
                com.datamind.datamind_api.analysis.exception
                        .AnalysisJobNotFoundException.class,
                () -> analysisExecutionService.completeJob(
                        jobId,
                        resultData
                )
        );

        assertTrue(
                analysisResultRepository
                        .findByJobId(jobId)
                        .isEmpty()
        );
    }


    private Dataset createDataset() {

        Dataset dataset = new Dataset(
                "test.csv",
                "hash-" + System.nanoTime(),
                100L,
                "csv"
        );

        dataset.setStoragePath(
                "./data/test.csv"
        );

        return datasetRepository.save(dataset);
    }


    private void cleanDatabase() {

        analysisResultRepository.deleteAll();
        analysisJobRepository.deleteAll();
        datasetRepository.deleteAll();
    }
}