package com.datamind.datamind_api.analysis.service;

import com.datamind.datamind_api.analysis.entity.AnalysisJob;
import com.datamind.datamind_api.analysis.entity.enums.AnalysisJobStatus;
import com.datamind.datamind_api.analysis.entity.enums.AnalysisType;
import com.datamind.datamind_api.analysis.exception.AnalysisJobNotFoundException;
import com.datamind.datamind_api.analysis.repository.AnalysisJobRepository;
import org.springframework.data.domain.PageRequest;
import com.datamind.datamind_api.dataset.entity.Dataset;
import com.datamind.datamind_api.dataset.service.DatasetService;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.util.StringUtils;

import java.time.LocalDateTime;
import java.time.Duration;
import java.util.Optional;
import java.util.List;
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
            @Value("${datamind.jobs.stale-after:30m}") Duration staleAfter
    ) {
        this.analysisJobRepository = analysisJobRepository;
        this.datasetService = datasetService;
        this.maxRetries = Math.max(1, maxRetries);
        this.staleAfterMinutes = Math.max(1, (int) staleAfter.toMinutes());
    }

    @Transactional
    public AnalysisJob createAnalysisJob(
            UUID datasetId,
            UUID datasetVersionId,
            AnalysisType analysisType,
            String targetColumn
    ) {
        return createAnalysisJob(datasetId, datasetVersionId, analysisType, targetColumn, false);
    }

    @Transactional
    public AnalysisJob createAnalysisJob(
            UUID datasetId,
            UUID datasetVersionId,
            AnalysisType analysisType,
            String targetColumn,
            boolean enableHyperparameterTuning
    ) {
        return createAnalysisJob(datasetId, datasetVersionId, analysisType, targetColumn,
                enableHyperparameterTuning, List.of());
    }

    @Transactional
    public AnalysisJob createAnalysisJob(
            UUID datasetId,
            UUID datasetVersionId,
            AnalysisType analysisType,
            String targetColumn,
            boolean enableHyperparameterTuning,
            List<java.util.Map<String, Object>> hypothesisTests
    ) {
        validateAnalysisRequest(analysisType, targetColumn);
        if (analysisType != AnalysisType.STATISTICAL
                && hypothesisTests != null && !hypothesisTests.isEmpty()) {
            throw new IllegalArgumentException("hypothesisTests are only supported for STATISTICAL analysis");
        }
        if (hypothesisTests != null && hypothesisTests.size() > 10) {
            throw new IllegalArgumentException("At most 10 hypothesis tests may be requested");
        }

        Dataset logicalOrVersion = datasetService.getDatasetById(datasetId);

        if (datasetVersionId == null) {
            throw new IllegalArgumentException("datasetVersionId is required");
        }
        Dataset version = datasetService.getDatasetById(datasetVersionId);
        UUID logicalId = logicalOrVersion.getLogicalDatasetId() != null
                ? logicalOrVersion.getLogicalDatasetId()
                : (logicalOrVersion.getId() != null ? logicalOrVersion.getId() : datasetId);
        if (version.getLogicalDatasetId() == null
                || !logicalId.equals(version.getLogicalDatasetId())) {
            throw new IllegalArgumentException(
                    "datasetVersionId does not belong to logicalDatasetId"
            );
        }

        AnalysisJob job = new AnalysisJob(
                logicalOrVersion,
                version,
                analysisType,
                AnalysisJobStatus.PENDING
        );
        job.setTargetColumn(StringUtils.hasText(targetColumn) ? targetColumn.trim() : null);
        job.setEnableHyperparameterTuning(enableHyperparameterTuning);
        job.setHypothesisTests(hypothesisTests);
        return analysisJobRepository.save(job);
    }

    public AnalysisJob createAnalysisJob(
            UUID datasetId,
            AnalysisType analysisType,
            String targetColumn
    ) {
        validateAnalysisRequest(analysisType, targetColumn);
        Dataset dataset = datasetService.getDatasetById(datasetId);
        UUID logicalId = dataset.getLogicalDatasetId() != null
                ? dataset.getLogicalDatasetId()
                : (dataset.getId() != null ? dataset.getId() : datasetId);
        Dataset currentVersion = datasetService.getCurrentVersion(logicalId);
        if (currentVersion == null) {
            currentVersion = dataset;
        }
        UUID versionId = currentVersion.getId() != null
                ? currentVersion.getId()
                : datasetId;
        return createAnalysisJob(logicalId, versionId, analysisType, targetColumn);
    }

    private void validateAnalysisRequest(AnalysisType analysisType, String targetColumn) {
        if (analysisType == null) {
            throw new IllegalArgumentException("analysisType is required");
        }
        if (analysisType == AnalysisType.TIME_SERIES
                || analysisType == AnalysisType.TEXT_ANALYSIS) {
            throw new IllegalArgumentException(
                    "Unsupported analysis type: " + analysisType
            );
        }
        // A missing target selects the analytics service's unsupervised
        // KMeans/PCA workflow. A supplied target selects supervised ML.
    }

    @Transactional(readOnly = true)
    public List<AnalysisJob> getAnalysisHistory(
            UUID logicalDatasetId,
            UUID datasetVersionId,
            AnalysisType analysisType,
            AnalysisJobStatus status,
            int limit
    ) {
        if (logicalDatasetId == null) {
            throw new IllegalArgumentException("logicalDatasetId is required");
        }
        int safeLimit = Math.max(1, Math.min(limit, 100));
        return analysisJobRepository.findHistory(
                logicalDatasetId,
                datasetVersionId,
                analysisType,
                status,
                PageRequest.of(0, safeLimit)
        );
    }

    public AnalysisJob getAnalysisJobById(UUID id) {
        return analysisJobRepository.findById(id)
                .orElseThrow(() -> new AnalysisJobNotFoundException(
                        "Analysis job not found with id: " + id
                ));
    }

    @Transactional
    public Optional<AnalysisJob> claimNextPendingJob() {
        Optional<AnalysisJob> job =
                analysisJobRepository.findNextPendingJob(AnalysisJobStatus.PENDING.name());

        job.ifPresent(analysisJob -> {
            Dataset version = analysisJob.getDatasetVersion();
            if (version == null) {
                version = analysisJob.getDataset();
                analysisJob.setDatasetVersion(version);
            }

            version.getId();
            version.getStoragePath();
            version.getFileType();

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
                job.markAsFailed(
                        "Job exceeded the maximum retry count after becoming stale"
                );
            } else {
                job.retry(
                        "Job was recovered after exceeding the processing timeout"
                );
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
