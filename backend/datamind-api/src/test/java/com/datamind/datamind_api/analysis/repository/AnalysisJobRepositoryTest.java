package com.datamind.datamind_api.analysis.repository;

import com.datamind.datamind_api.analysis.entity.AnalysisJob;
import com.datamind.datamind_api.analysis.entity.enums.AnalysisJobStatus;
import com.datamind.datamind_api.analysis.entity.enums.AnalysisType;
import com.datamind.datamind_api.dataset.entity.Dataset;
import com.datamind.datamind_api.dataset.repository.DatasetRepository;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.transaction.PlatformTransactionManager;
import org.springframework.transaction.support.TransactionTemplate;

import java.time.LocalDateTime;
import java.util.Optional;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicReference;
import java.util.UUID;

import static org.junit.jupiter.api.Assertions.*;

@SpringBootTest
class AnalysisJobRepositoryTest
{
    @Autowired
    private AnalysisJobRepository analysisJobRepository;

    @Autowired
    private DatasetRepository datasetRepository;

    @Autowired
    private AnalysisResultRepository analysisResultRepository;

    @Autowired
    private PlatformTransactionManager transactionManager;


    @BeforeEach
    void setUp()
    {
        cleanDatabase();
    }


    @AfterEach
    void tearDown()
    {
        cleanDatabase();
    }


    @Test
    void shouldFindOldestPendingJob()
    {
        Dataset dataset = createDataset();

        AnalysisJob job1 = createJob(
                dataset,
                LocalDateTime.of(2026, 1, 1, 10, 0)
        );

        AnalysisJob job2 = createJob(
                dataset,
                LocalDateTime.of(2026, 1, 1, 11, 0)
        );

        analysisJobRepository.save(job1);
        analysisJobRepository.save(job2);

        Optional<AnalysisJob> result =
                analysisJobRepository.findNextPendingJob(
                        AnalysisJobStatus.PENDING.name()
                );

        assertTrue(result.isPresent());

        assertEquals(
                job1.getId(),
                result.get().getId()
        );
    }


    @Test
    void shouldSkipLockedJob() throws InterruptedException
    {
        Dataset dataset = createDataset();

        AnalysisJob job1 = createJob(
                dataset,
                LocalDateTime.of(2026, 1, 1, 10, 0)
        );

        AnalysisJob job2 = createJob(
                dataset,
                LocalDateTime.of(2026, 1, 1, 11, 0)
        );

        analysisJobRepository.save(job1);
        analysisJobRepository.save(job2);

        CountDownLatch lockAcquired =
                new CountDownLatch(1);

        CountDownLatch releaseLock =
                new CountDownLatch(1);

        AtomicReference<UUID> lockedJobId =
                new AtomicReference<>();

        Thread worker1 = new Thread(() ->
        {
            TransactionTemplate transaction =
                    new TransactionTemplate(transactionManager);

            transaction.execute(status ->
            {
                Optional<AnalysisJob> result =
                        analysisJobRepository.findNextPendingJob(
                                AnalysisJobStatus.PENDING.name()
                        );

                assertTrue(result.isPresent());

                lockedJobId.set(
                        result.get().getId()
                );

                lockAcquired.countDown();

                try
                {
                    releaseLock.await(
                            10,
                            TimeUnit.SECONDS
                    );
                }
                catch (InterruptedException exception)
                {
                    Thread.currentThread().interrupt();
                }

                return null;
            });
        });

        worker1.start();

        assertTrue(
                lockAcquired.await(
                        10,
                        TimeUnit.SECONDS
                ),
                "Worker 1 failed to acquire database lock"
        );

        TransactionTemplate transaction =
                new TransactionTemplate(transactionManager);

        AnalysisJob secondJob =
                transaction.execute(status ->
                        analysisJobRepository
                                .findNextPendingJob(
                                        AnalysisJobStatus.PENDING.name()
                                )
                                .orElseThrow()
                );

        assertNotNull(lockedJobId.get());

        assertEquals(
                job1.getId(),
                lockedJobId.get()
        );

        assertEquals(
                job2.getId(),
                secondJob.getId()
        );

        assertNotEquals(
                lockedJobId.get(),
                secondJob.getId()
        );

        releaseLock.countDown();

        worker1.join(10_000);

        assertFalse(
                worker1.isAlive(),
                "Worker 1 did not finish"
        );
    }


    private Dataset createDataset()
    {
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


    private AnalysisJob createJob(
            Dataset dataset,
            LocalDateTime createdAt
    )
    {
        AnalysisJob job = new AnalysisJob(
                dataset,
                AnalysisType.EDA,
                AnalysisJobStatus.PENDING
        );

        job.setCreatedAt(createdAt);

        return job;
    }


    private void cleanDatabase()
    {
        analysisResultRepository.deleteAll();
        analysisJobRepository.deleteAll();
        datasetRepository.deleteAll();
    }
}