package com.datamind.datamind_api.analysis.entity;

import com.datamind.datamind_api.analysis.entity.enums.AnalysisJobStatus;
import com.datamind.datamind_api.analysis.entity.enums.AnalysisType;
import com.datamind.datamind_api.dataset.entity.Dataset;
import org.junit.jupiter.api.Test;

import java.time.LocalDateTime;

import static org.junit.jupiter.api.Assertions.*;

class AnalysisJobTest {

    private AnalysisJob createJob() {

        Dataset dataset = new Dataset();

        return new AnalysisJob(
                dataset,
                AnalysisType.EDA,
                AnalysisJobStatus.PENDING
        );
    }

    @Test
    void newJobShouldStartAsPending() {

        AnalysisJob job = createJob();

        assertEquals(
                AnalysisJobStatus.PENDING,
                job.getStatus()
        );

        assertEquals(
                0,
                job.getRetryCount()
        );

        assertNotNull(job.getCreatedAt());
    }

    @Test
    void markAsProcessingShouldChangeStatusAndSetStartedAt() {

        AnalysisJob job = createJob();

        job.markAsProcessing();

        assertEquals(
                AnalysisJobStatus.PROCESSING,
                job.getStatus()
        );

        assertNotNull(job.getStartedAt());
    }

    @Test
    void markAsCompletedShouldChangeStatusAndSetCompletedAt() {

        AnalysisJob job = createJob();

        job.markAsProcessing();
        job.markAsCompleted();

        assertEquals(
                AnalysisJobStatus.COMPLETED,
                job.getStatus()
        );

        assertNotNull(job.getCompletedAt());
        assertNull(job.getErrorMessage());
    }

    @Test
    void markAsFailedShouldStoreErrorMessage() {

        AnalysisJob job = createJob();

        job.markAsProcessing();

        String errorMessage = "Python service unavailable";

        job.markAsFailed(errorMessage);

        assertEquals(
                AnalysisJobStatus.FAILED,
                job.getStatus()
        );

        assertEquals(
                errorMessage,
                job.getErrorMessage()
        );

        assertNotNull(job.getCompletedAt());
    }

    @Test
    void retryShouldMoveJobBackToPending() {

        AnalysisJob job = createJob();

        job.markAsProcessing();
        job.markAsFailed("Temporary failure");

        job.retry();

        assertEquals(
                AnalysisJobStatus.PENDING,
                job.getStatus()
        );

        assertNull(job.getCompletedAt());
        assertNull(job.getErrorMessage());
    }

    @Test
    void incrementRetryCountShouldIncreaseRetryCount() {

        AnalysisJob job = createJob();

        assertEquals(0, job.getRetryCount());

        job.incrementRetryCount();

        assertEquals(1, job.getRetryCount());

        job.incrementRetryCount();

        assertEquals(2, job.getRetryCount());
    }
}