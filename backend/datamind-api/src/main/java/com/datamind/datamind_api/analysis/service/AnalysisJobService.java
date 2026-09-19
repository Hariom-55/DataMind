package com.datamind.datamind_api.analysis.service;

import com.datamind.datamind_api.analysis.entity.AnalysisJob;
import com.datamind.datamind_api.analysis.entity.enums.AnalysisJobStatus;
import com.datamind.datamind_api.analysis.entity.enums.AnalysisType;
import com.datamind.datamind_api.analysis.exception.AnalysisJobNotFoundException;
import com.datamind.datamind_api.analysis.repository.AnalysisJobRepository;
import com.datamind.datamind_api.dataset.entity.Dataset;
import com.datamind.datamind_api.dataset.service.DatasetService;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.util.StringUtils;

import java.time.LocalDateTime;
import java.util.Optional;
import java.util.UUID;

@Service
public class AnalysisJobService {
    private final AnalysisJobRepository analysisJobRepository;
    private final DatasetService datasetService;
    private final int maxRetries;
    private final int staleAfterMinutes;

    public AnalysisJobService(
            AnalysisJobRepository analysisJobRepository,
            DatasetService datasetService,
            @Value("${datamind.jobs.max-retries:3}") int maxRetries,
            @Value("${datamind.jobs.stale-after:30m}") java.time.Duration staleAfter
    ) {
        this.analysisJobRepository = analysisJobRepository;
        this.datasetService = datasetService;
        this.maxRetries = Math.max(1, maxRetries);
        this.staleAfterMinutes = Math.max(1, (int) staleAfter.toMinutes());
    }

    public AnalysisJob createAnalysisJob(UUID datasetId, AnalysisType analysisType, String targetColumn) {
        Dataset dataset = datasetService.getDatasetById(datasetId);
        validateAnalysisRequest(analysisType, targetColumn);

        AnalysisJob job = new AnalysisJob(dataset, analysisType, AnalysisJobStatus.PENDING);
        job.setTargetColumn(StringUtils.hasText(targetColumn) ? targetColumn.trim() : null);
        return analysisJobRepository.save(job);
    }

    private void validateAnalysisRequest(AnalysisType analysisType, String targetColumn) {
        if (analysisType == null) {
            throw new IllegalArgumentException("analysisType is required");
        }
        if (analysisType == AnalysisType.MACHINE_LEARNING && !StringUtils.hasText(targetColumn)) {
            throw new IllegalArgumentException("targetColumn is required for MACHINE_LEARNING analysis");
        }
    }

    public AnalysisJob getAnalysisJobById(UUID id) {
        return analysisJobRepository.findById(id)
                .orElseThrow(() -> new AnalysisJobNotFoundException("Analysis job not found with id: " + id));
    }

    @Transactional
    public Optional<AnalysisJob> claimNextPendingJob() {

        Optional<AnalysisJob> job =
                analysisJobRepository.findNextPendingJob(
                        AnalysisJobStatus.PENDING.name()
                );

        job.ifPresent(analysisJob -> {

            Dataset dataset = analysisJob.getDataset();

            dataset.getId();
            dataset.getStoragePath();
            dataset.getFileType();

            analysisJob.markAsProcessing();
            analysisJobRepository.save(analysisJob);
        });
        return job;
    }

    @Transactional
    public int recoverStaleJobs() {
        LocalDateTime cutoff = LocalDateTime.now().minusMinutes(staleAfterMinutes);
        var staleJobs = analysisJobRepository.findByStatusAndStartedAtBefore(
                AnalysisJobStatus.PROCESSING,
                cutoff
        );

        for (AnalysisJob job : staleJobs) {
            job.incrementRetryCount();
            if (job.getRetryCount() >= maxRetries) {
                job.markAsFailed("Job exceeded the maximum retry count after becoming stale");
            } else {
                job.retry("Job was recovered after exceeding the processing timeout");
            }
        }
        analysisJobRepository.saveAll(staleJobs);
        return staleJobs.size();
    }

    @Transactional
    public void completeJob(UUID jobId) {
        AnalysisJob job = getAnalysisJobById(jobId);
        job.markAsCompleted();
        analysisJobRepository.save(job);
    }

    @Transactional
    public void failJob(UUID jobId, String errorMessage) {
        AnalysisJob job = getAnalysisJobById(jobId);
        job.incrementRetryCount();

        if (job.getRetryCount() < maxRetries) {
            job.retry(errorMessage);
        } else {
            job.markAsFailed(errorMessage);
        }
        analysisJobRepository.save(job);
    }
}
